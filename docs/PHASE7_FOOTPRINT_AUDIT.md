# Phase 7 – IRCSS-Grundriss-Audit

## Grundlage und Integrität

Blender **5.2.2 LTS**, `GenerateHouse` aus der unveränderten `GeometryNodesFrenchHous.blend`.

SHA-256: `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5`.

Audit: [`audit_phase7_footprint.py`](../scripts/audit_phase7_footprint.py), [`footprint_audit.json`](../tests/addon/phase7/footprint_audit.json). Der Audit läuft ausdrücklich mit dem installierten **0.2.0-Referenz-ZIP**, nicht mit der neuen Initialisierungslogik. Alle Versuchsmeshes entstehen nur an einem neuen temporären Haus, ohne Speichern des Originalassets.

## Was die vorhandene Gruppe benötigt

Das ursprüngliche HouseOne-Eingabemesh enthält vier Punkte, eine Quad-Fläche und übliche Blender-Auswahl-/Kantenattribute sowie `UVMap`. Keine besonderen benannten Grundrissattribute sind erforderlich: Ein neu erzeugtes Mesh mit **vier Vertices und einer positiv orientierten Quad-Fläche** erzeugt ebenfalls das vollständige Haus.

Das alte Quad ist leicht schief und nicht ganz eben (Z etwa −0,03088…0), zudem nicht exakt um den lokalen Ursprung zentriert. Es wird deshalb für neue 0.3-Häuser nicht skaliert oder still als vermeintlich perfektes Rechteck behandelt.

### Achsen und Symmetrie

- **Hausbreite = lokale Y-Ausdehnung** der Front.
- **Haustiefe = lokale X-Ausdehnung**.
- Front-/Türseite: **lokal +X**. Im Originalgraph bestätigt `Vector Math.047` den Vergleich des Frontnormalenfeldes mit `(1,0,0)`; `Compare.020` filtert die nicht ausreichend nach vorne gerichteten Kandidaten.
- Die Dachmittel-Auswahl arbeitet mit X und der Mitte **X=0** (`Separate XYZ.002`, `Compare.002`, Bounds-Verzweigung).
- Der neue Starter ist sowohl in X als auch in Y um 0 zentriert: Damit erfüllt er die Dach-Symmetrieebene X=0 **und** die ungefähr X-achsensymmetrische Grundrissannahme des Originalprojekts. Das Dach läuft nicht von einem versehentlich verschobenen Mittelpunkt aus.
- Boden des neuen Rechtecks: **Z=0**. Face-Reihenfolge `(0,1,3,2)` mit Normalenrichtung +Z.

```text
(-D/2, -W/2, 0) ── (+D/2, -W/2, 0)
(-D/2, +W/2, 0) ── (+D/2, +W/2, 0)
```

Die tatsächliche zyklische Face-Reihenfolge verbindet die Punkte ohne Überkreuzung. Eingabefläche = W×D > 0; keine negativen/degenerierten Eingabequads.

## Auswertung im vorhandenen Graph

Die Gruppe übernimmt Eingabegeometrie direkt, führt sie durch den bestehenden Transformations-/lokalen Arbeitsraum und erzeugt daraus den Körper. Relevante Original-Frames:

- `Make ground floor`, `create XY foundation for second floor`, `Make base shape for floor N`: Extrusion/Stockwerksschleife.
- `Get just the base of the roof`, `Calculate roof height`, `select the center cut to pull up`: Dachbasis und Mittelgrat.
- `Pull out the roof over hang in Y - forward axis`: Original-Frame-Beschriftung, **keine neue UI-Achsdefinition**. Entscheidend für die Bedienung sind das lokale Eingabequad und der nachgewiesene +X-Türfilter.
- `Generate possible window spots`: Kurven-/Kantenlängen steuern mögliche Fensterpositionen; der verbundene Längenpfad hat einen 1,5-m-Abstand als Ausgangswert.
- `Spawn the bases of the support beams`: vorhandenes Resampling im Längenmodus, etwa 0,71 m.
- Eck-/Randabstände löschen ungeeignete Fenster-/Türkandidaten; vorhandene Bool-/Fachwerkoperationen bleiben verantwortlich.

Eine Maßänderung verändert deshalb **die Anzahl und Verteilung** der Bauteile. Sie streckt nicht einfach Fenster, Türen, Dachziegel oder Texturen wie eine globale Skalierung. Verschobene/anders große Eingaben können bei unverändertem Seed andere Detailkandidaten ergeben; das ist originales Verhalten.

### Höhe und Zufall

Die Dachhöhe wird im Original unter anderem aus einer Zufallsgröße etwa 1,6…2,4 abgeleitet. Die ID berücksichtigt Seed und Objektposition, u.a. über einen Dot-Product mit `(7,3; 10,7; 8,6)` und weitere Konstanten. Weitere `GetPositionBasedSeed`-Aufrufe sind vorhanden. Die Höhe ist somit **nicht** ein neuer unabhängiger Breiten-/Tiefenparameter.

Alle drei Vergleichshäuser besitzen Seed 29, Stockwerkswert 2, Dachkrümmung 1,66 und gleiche Farben. Ihre unterschiedlichen Weltpositionen dürfen trotzdem Details und genaue Höhen ändern. Die Änderung der Form selbst wird zusätzlich in den 0.2-Kontrollauswertungen am **gleichen Ursprung** nachgewiesen.

## Rechteck-Adapter in 0.3

`footprints.py` kapselt ausschließlich dieses begrenzte Eingabemesh:

- Objekt-Marker `mbg_footprint_version=1`, Presetabsicht in `mbg_shape`.
- Breite/Tiefe werden aus den **wirklichen Meshvertices** gelesen, nicht aus einer zweiten UI-Parameterkopie.
- Maßänderung schreibt die vier lokalen Koordinaten und taggt nur das betroffene Objekt/Datablock für das Live-Update.
- Keine Änderungen an `GenerateHouse`, Untergruppen, originalen Shadern oder den acht RNA-Eingängen. `BeamCollor` bleibt unverändert geschrieben.
- Kein globaler Load-/Depsgraph-Reparaturhandler. Ein beliebig manuell editiertes Mesh wird nicht automatisch zurückgebogen.
- Normales Shift-D erzeugt eigene Meshdaten. Alt-D bleibt zunächst absichtlich Blender-typisch geteilt; **vor einer Add-on-Maßänderung** erfolgt Copy-on-Write. Native Duplikation bindet den `Object`-RNA-Eingang bereits auf das Duplikat um; das wurde an 0.2 und 0.3 getestet.
- Manuelles Edit-Mode-Bearbeiten eines Alt-D-Meshes bleibt dagegen Blenders bewusst geteilte Bearbeitung. Dafür macht das Add-on keine gegenteilige Garantie. Die neuen Regler sind im Edit Mode gesperrt.

## Transformationen und präziser Export

Objektposition/-rotation/-skalierung werden von den Dimension-Settern **nicht** geändert oder angewendet. Reglerwerte sind lokale Maße, **1 BU = 1 m bei Objektskalierung 1**. Nichtuniforme Objektskalierung wirkt zusätzlich und wird im Panel angezeigt; die Maße sind keine geschätzte Welt-Bounding-Box einschließlich Dachüberstand.

Der Graph nutzt `Self Object`/`Object Info` und einen inversen Matrixpfad für seinen Arbeitsraum. Daher darf man dessen Transformationsannahmen nicht durch Apply Transform ersetzen.

Ein zusätzlicher Stresstest fand eine alte Kopier-Ungenauigkeit des Phase-6-Exporters bei einem **exakt symmetrischen Rechteck**, Yaw 0,47 rad und Scale `(−1,2; 0,8; 1,1)`: Das erneute Setzen derselben `matrix_world` zerlegte/rekomponierte die Spiegelung, änderte die Kanaldarstellung und erzeugte einen Matrixfehler von **1,1920929e−7**. Die achsensensitiven GN-Entscheidungen ergaben anschließend eine nicht mehr bijektiv passende Balkenfläche.

Minimale Korrektur: Bei statischen, unparenteten, constraintfreien Objekten behält die Exportkopie ihre von `Object.copy()` bereits exakt übernommenen Transformationskanäle. Für Parent-/Constraint-/Animationsauflösung bleibt der bisherige Matrixpfad erhalten. Keine Änderungen am Originalobjekt oder an Nodes.

[`transform_diagnostic.json`](../tests/addon/phase7/transform_diagnostic.json) misst danach **0 Matrixfehler** für die Kanalübernahme. Der transformierte Rechteckexport besteht den vollständigen Polygon-/GLB-Abgleich (122.124 Polygone, 0 fehlend/zusätzlich). Vier echte alte Phase-6-Häuser wurden zusätzlich erneut exportiert; alle vier Vergleichs-GLBs bleiben byteidentisch zu ihren Phase-6-Referenzen, einschließlich der geometrisch vollständigen Spiegelungsvariante.

## Beobachtete Grenzen, keine verdeckte Optimierung

Freigegebene Eingabegrenzen: Breite **3,2…7,0**, Tiefe **3,0…5,0 BU**. Technische Eckwerte, mehrere Seeds, 1/2/3 Stockwerke, Kurvenwerte 0,5/1,66/2,5 und ein zusätzlicher 8-Stockwerke-Fall wurden gemessen. Das ist keine exhaustive Prüfung jeder möglichen Kombination oder ein 50-Häuser-Lasttest.

Der Originalgenerator emittiert bereits am originalen 0.2-HouseOne **3.582 Nullflächen unter 23.061 direkten Polygonen**. Die 0.2-Kontrollrechtecke zeigen ebenfalls solche Flächen (z.B. Compact 2.379/16.676). Die 0.3-Stichproben ordnen die gemessenen Nullflächen dem Slot **Stone** zu. Sie sind keine degenerierten Eingabequads und kein erst durch einen neuen Dachgenerator entstandener Schaden.

Diese geerbten Ausgabeflächen bleiben vollständig erhalten und werden transparent protokolliert. Keine Löschung auf Verdacht, keine Polygonoptimierung und keine Behauptung eines komplett fehlerfreien/manifold Originalmeshes. Die betrachteten sichtbaren Häuser, Normaleinheitswerte, vollständige Instanzrealisierung und Godot-Importe funktionieren. Größere/kleinere, schiefe, L-/U-förmige oder komplexe Grundrisse sind **nicht freigegeben**.
