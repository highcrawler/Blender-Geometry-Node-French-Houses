# Phase 4B – Ergebnis

**RESULT: PASS – für HouseOne-Geometrie und Putz-Base-Color-Koordinatentreue.**

Branch: `experiment/geometry-coordinate-fidelity-04b`.
Basis: `03a3e9eb053b5976cd4bed9e15e8ffd53744b948` (abgeschlossene Phase 4, PARTIAL).
Abschlusscommit: der Commit dieses Berichts auf diesem Experiment-Branch; konkrete ID im Git-Verlauf/Abschlussprotokoll. Kein Merge nach `main`.

## Tatsächliche Ursachen und Korrektur

1. **Bewiesener Geometrieverlust:** `new_from_object` am ausgewerteten HouseOne übernahm nur den direkten GN-Mesh-Anteil. **2.595 sichtbare zugehörige DG-Instanzblätter mit 103.658 Dreiecken fehlten**: Fachwerk, Fenster-/Gaubendetails und Pflanzen. Dachziegel und Steingeometrie waren dagegen bereits enthalten.
2. **Keine falschen Phase-4-Putzkoordinaten nachgewiesen, sondern positiv widerlegt:** Phase4 und tatsächliches Original liefern auf 101.588 sichtbaren Fassaden-Putzpixeln exakt gleiche Float-Generated-Werte. Das Putz-PNG und das UV-Layout bleiben im korrigierten Versuch vollständig byte-/werteidentisch zu Phase4.
3. **Zusätzlicher Fallstrick der Realisierung:** Neu enthaltene Pflanzen erweitern die Mesh-Bounds. Reine Realisierung mit neuem Auto-Texspace verursacht messbar andere Generated-Koordinaten. Auf der isolierten vollständigen Exportkopie wird daher der ursprüngliche ausgewertete direkte Mesh-Texspace fixiert; danach Fehler **0**.
4. **Fehlerhafte frühere Vergleichskontrolle:** Eine vor der GN-Auswertung verschobene Hauskopie beeinflusst die positionsbasierte Seed-Logik. Die neue Referenz verwendet das tatsächliche unveränderte HouseOne an seiner Originalposition. Erst das eingefrorene Exportmesh wird zentriert.

Minimale technische Änderung: zusätzlicher Realize-All-Wrapper **nur auf einer HouseOne-Kopie**, anschließend ursprünglichen ausgewerteten Texspace an der Exportmeshkopie erhalten. Kein Eingriff in originale Nodes, Seed-Logik oder Materialshader. Keine allgemeine Export-/Bake-Engine.

## Abnahmeevidenz

| Prüfung | Ergebnis |
|---|---|
| Original / Phase4 / vollständige Kopie | 154.602 / 50.944 / **154.602** Dreiecke |
| Original ↔ vollständige Kopie | 97.060 Polygone bijektiv; 0 fehlend/zusätzlich; max. Eckfehler 1,1681e-6 BU |
| Silhouetten Iso/Front/Seite/Fassade | Original und realisiert in allen vier Ansichten RGBA-identisch |
| GLB-Positionsvergleich je Material, beidseitig | max. 4,771e-7 BU, Materialdreieckszahlen exakt |
| korrigierte Generated-Werte, sichtbarer Putz | MAE 0, maximal 0 (32-Bit-EXR) |
| LocalPosition / LocalNormal, sämtliche ursprüngliche Putzecken | maximale Abweichung jeweils 0 |
| Bake | Original-Putzshader, nur Base Color, 1024², sRGB |
| Phase4 ↔ Phase4B Atlas / UVs | PNG byteidentisch / UV-Polygone exakt gleich |
| unabhängige Blender-Prozesse | identische PNG- und GLB-Hashes |
| GLB | **12.262.708 Bytes**, ein Mesh, zwölf Material-Primitives, ein eingebettetes PNG |
| Godot 4.7 Import und grafischer Lauf | 154.602 Dreiecke, zwölf Surfaces, Putztextur 1024²; acht echte Vorher-/Nachher-Screenshots |
| Originaldatei | SHA-256 unverändert; nie gespeichert |

GLB SHA-256: `edb6773b237c06627f09e146e4a6212575977eb03de4dee3705874efb4af25d7`.

Putz-PNG SHA-256: `1fef33e7b37104a491fe53584ff1e1b2284d0e169c3334e8d455a14d6bb7e2fd` (wie Phase4).

Alle relevanten Instanzen sind enthalten; keine ungeklärte fehlende Instanz verbleibt für den untersuchten HouseOne-Zustand. Gleiche Geometrie bedeutet nicht identische glTF-Vertexzahlen: Material-/UV-/Normalensplits und Triangulierung werden getrennt behandelt.

## Bilder und technische Berichte

- [Geometrie-Audit](PHASE4B_GEOMETRY_AUDIT.md): Eigentümerschaft, Materialien, Instanzen, Bounds, API-Verfahren.
- [Koordinatenanalyse](PHASE4B_COORDINATE_ANALYSIS.md): Shader, Texspace, falsifizierte Input-Quad-Hypothese, Float-Nachweis.
- [Visuelle Verifikation](PHASE4B_VISUAL_VERIFICATION.md): alle vier Ansichten, Vorher-/Nachher-Tafeln, Godot, Grenzen.
- Direkt: [Geometrie Iso](../tests/baking/phase4b/geometry_iso.png), [Putz Original/Phase4/Phase4B](../tests/baking/phase4b/comparison_facade.png), [Godot vorher/nachher](../tests/baking/phase4b/godot_comparison_facade.png).

Artefakte ausschließlich unter [`tests/baking/phase4b/`](../tests/baking/phase4b/), zusätzlich importfähige Kopie in `godot-test/assets/`:

- `probe.json`, `instances.json`, `geometry.json`: Quellreferenzen, Blattmatrizen/IDs, A/B/C-Metriken, Polygonabgleich und Koordinatenfehler.
- `coordinates_float_*_facade.exr`, `plaster_mask_facade.png`: direkte Koordinatenmessung.
- `shader_*`, `silhouette_*`, `generated_*`, `bake4*`, `godot_*`: echte Einzelbilder; `comparison_*`, `geometry_*`, `godot_comparison_*`, `*_delta_*`: abgeleitete Tafeln/Overlays.
- `HouseOne_Phase4B.glb`, `HouseOne_Plaster_BaseColor.png`, `bake_uv.json`, `bake_measurements.json`: korrigierter Versuch, Export-/UV-/Attributprüfung und Bake-Messwerte.
- `repeat_reference.json`, `image_metrics.json`: unabhängige Prozessreferenz und Wiederholungsvergleich.
- `probe.log`, `bake.log`, `fidelity.log`, `godot_import.log`, `godot_capture.log`, `godot_measurements.json`, `images.log`: ausgeführte Verfahren. `fidelity.log` ist der bis RENDERS_COMPLETE extrahierte Audit-/Renderabschnitt des vollständigen Bake-Laufs.

## Reproduktion aus Repository-Wurzel

Benötigt lokal installierte Blender 5.2.2 LTS, Godot 4.7, Python 3 + Pillow. Kein Download/Update des Toolchains erforderlich. In dieser Umgebung direkter Blender-Pfad statt Snap-Launcher:

```bash
/snap/blender/current/blender -b --factory-startup -t 4 -P scripts/phase4b_probe.py
/snap/blender/current/blender -b --factory-startup -t 4 -P scripts/phase4b_bake.py
# Derselbe Versuch in einem neuen Prozess; überschreibt nur Phase4B-Ausgaben:
/snap/blender/current/blender -b --factory-startup -t 4 -P scripts/phase4b_bake.py
cp tests/baking/phase4b/HouseOne_Phase4B.glb godot-test/assets/HouseOne_Phase4B.glb

# Godot-Konfiguration und Laufzeitdaten bleiben innerhalb dieses Repositories:
mkdir -p tests/baking/phase4b/runtime/{config,data,cache}
export XDG_CONFIG_HOME="$PWD/tests/baking/phase4b/runtime/config"
export XDG_DATA_HOME="$PWD/tests/baking/phase4b/runtime/data"
export XDG_CACHE_HOME="$PWD/tests/baking/phase4b/runtime/cache"
godot --headless --path godot-test --editor --import --quit
godot --path godot-test --rendering-driver opengl3 \
  --script res://scripts/phase4b_capture.gd -- --output "$PWD/tests/baking/phase4b"
python3 scripts/phase4b_images.py
```

`phase4b_bake.py` führt zuerst automatisch den unabhängigen A/B/C-Audit und alle Kontrollrenderings aus `phase4b_fidelity.py` aus. Optional kann dieser Audit auch allein mit denselben Blender-Flags gestartet werden. Er enthält keine neue Textur-Bake-Variante.

Bake: Cycles CPU, DIFFUSE ausschließlich COLOR, Direct/Indirect aus, 1024×1024 sRGB, 8 Pixel EXTEND. Nur 1.105 Putzpolygone erhalten Smart-UV-Project 66°, 0,02 Fraction-Margin; Original-UV und Attribute bleiben erhalten. Alle anderen Materialien schreiben nur in einen RAM-Sink. Zwei identische Bakes je Prozess. GLB: `GLB`, `use_selection=True`, `use_active_scene=True`, keine Animationen, keine Vertexfarben; allein korrigierte Meshkopie ausgewählt. Zwölf Materialzuweisungen erhalten, eine Base-Color-Textur auf `TEXCOORD_1`, PNG-Bytestrom aus BIN-Chunk überprüft.

Die mitgelieferte `repeat_reference.json` ist die festgehaltene unabhängige erste Prozessreferenz. `phase4b_images.py` prüft den neuen Lauf dagegen. Hashgleichheit gilt für die dokumentierte CPU-/Blender-Konfiguration, nicht pauschal für alle Versionen/Geräte. Keine großen `.blend`-Zwischendateien erforderlich.

## Einschränkungen und Reichweite

- Die neue vollständige Variante ist deutlich größer: 154.602 statt 50.944 Dreiecke; kein Performance-/FPS-Nachweis und keine Optimierung in diesem Experiment.
- Generated-Floatmessung unmittelbar auf der sichtbaren Fassade; objektweite Begründung zusätzlich durch fixierten identischen Texspace, unveränderte lokale Geometrie und GN-Putzattribute. Kein Anspruch auf jede verdeckte Fläche oder jedes andere instanzierte Shader-Koordinatensystem.
- 1024² verursacht weichere Details; Normal-/Bump-Relief wird nicht übertragen. Keine neuen auffälligen Putz-UV-/Geometrie-/Importfehler beobachtet.
- **Keine vollständige Nichtputz-Materialtreue:** Phase-3-Konstanten bleiben, neue Pflanzenslots verwenden Principled-Defaults. Weiße statt prozedural farbiger Blüten und vereinfachtes Glas sind sichtbar und ausdrücklich nicht als erfolgreich übertragene Originalmaterialien bewertet. Keine zusätzlichen Material-Bakes zur Kaschierung dieses begrenzten Tests.
- Keine Aussage über andere Gebäudetypen oder einen verschobenen, neu ausgewerteten Generator. Die bestehende Methode ohne HouseOne-Instanzkorrektur wäre weiterhin unvollständig.

Git-Speicherung: größte neue Einzeldatei 12,26 MB, keine LFS-Migration notwendig; native Git-Ablage wie bisher. Lokale Godot-Konfiguration/Caches bleiben ignoriert. Keine destruktive Bereinigung; alte unversionierte Phase-2-Skripte bleiben unangetastet.

## Zweiter Gebäudetyp?

**JA – mit der hier geprüften, korrigierten Methode als begrenztem Experiment, nicht mit dem unveränderten Phase-4-Meshexport.** Die zwei Kernfragen sind für HouseOne geschlossen: vollständige Instanzgeometrie wird bijektiv nachgewiesen, und der vollständige Bake reproduziert exakt den ursprünglichen räumlichen Putz-Bezugsraum. Die positionsabhängige GN-Auswertung muss vor jeder Zentrierung eingefroren werden. Andere Gebäudetypen benötigen ihren eigenen Eigentümerschafts-, Texspace- und Attributnachweis.

**Genau ein nächster Entwicklungsschritt:** Dasselbe begrenzte A/B/C-Geometrie- und Putzkoordinatenexperiment an **HouseTWo** durchführen, ohne den Generator umzubauen oder eine allgemeine Pipeline daraus zu machen.
