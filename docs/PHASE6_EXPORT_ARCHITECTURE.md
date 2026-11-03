# Phase 6 – Selected House GLB Export: Architektur

## Umfang und Installation

Add-on **0.2.0**, Blender **5.2.2 LTS**. Grundlage: abgeschlossene Phase 5, `a20ce4a`. Neue Datei `addon/medieval_building_generator/exporter.py`; kleine Erweiterungen von Operator, Panel, Registrierung und Manifest. Keine Änderungen an IRCSS-Gruppen, Quellbibliothek, Phase-3/4B-Exportskripten oder vorhandenen Tests.

Installierbares Artefakt: [`medieval_building_generator-0.2.0.zip`](../tests/addon/phase6/medieval_building_generator-0.2.0.zip). Blender → Edit → Preferences → Get Extensions → Menü → **Install from Disk**, ZIP auswählen und aktivieren. Bei bereits installierter 0.1.0 über dieselbe Installation aktualisieren, nicht beide Versionen parallel aktivieren.

Im N-Panel **Medieval Buildings** ein erzeugtes Haus aktiv auswählen → **Export → Export Selected House (.glb)** → Ort/Name auswählen → Export bestätigen. Gespeicherte Häuser benötigen dafür keine erneut erreichbare IRCSS-Quelldatei. Die acht vorhandenen Regler und das Erstellen bleiben unverändert.

## Transaktion

1. Aktives Objekt muss Marker `mbg_house_version`, Mesh und kompatiblen Generator besitzen und im Object Mode sein. Sichtbarkeit und selbstreferenzierender `Object`-Eingang werden geprüft. Namen sind keine Gebäudeidentifikation.
2. Quellobjekt und Dependency Graph an der **ursprünglichen Weltposition** auswerten. Direkte Dreiecke plus ausschließlich sichtbare Mesh-Instanzen mit `parent.original == source` zählen, inklusive Materialverteilung.
3. Temporäre Objekt-/Eingabemeshkopie mit aufgelöster originaler Weltmatrix in der Quellszene auswerten. Animation/Parent/Constraints dieser **Kopie** entfernen, aufgelöste Matrix beibehalten. Der Generator-`Object`-Eingang bleibt auf dem Originalobjekt, damit die positionsabhängige Zufallslogik identisch bleibt.
4. **Nur an dieser Kopie** einen neuen, nachgeschalteten Modifier hinzufügen: `Group Input → Realize Instances (Realize All=True) → Group Output`. Unverändertes `GenerateHouse` und Untergruppen weiterhin referenzieren.
5. Ausgewertetes vollständiges Mesh entnehmen. Seine Dreieckszahlen **pro Originalmaterial** müssen mit der zuvor gezielt ermittelten Quellgeometrie übereinstimmen. Andernfalls abbrechen, statt eine unvollständige GLB auszugeben.
6. Erst das eingefrorene Mesh um den Boden-/Grundriss-Pivot verschieben. Rotation/Skalierung einbacken; bei negativem Determinantenwert die Polygonorientierung korrigieren.
7. Nur auf diesem Mesh PBR-Materialkopien zuweisen. Ein isoliertes temporäres Export-Scene mit **genau einem Objekt ohne Modifier** anlegen. Export: `use_selection=True`, `use_active_scene=True`, GLB, Y-up, keine Animationen/Skins/Kameras/Lichter/Vertexfarben/Extras.
8. In eine temporäre `.glb` im Zielverzeichnis schreiben. Header, genau ein Mesh und vollständige Dreieckszahl nachprüfen. Erst dann atomar an den endgültigen Zielpfad übernehmen.
9. `finally`: ursprüngliches Fenster-Scene/View-Layer, komplette Auswahl und aktives Objekt wiederherstellen; temporäre Objekte, Scene, Meshes, Gruppe, Materialien und unvollständige Datei entfernen.

Die kleine temporäre Evaluationskopie in der Quellszene ist notwendig für den geprüften Phase-4B-Auswertungsraum. Die GLB erhält **niemals** diese Szene: Der eigentliche glTF-Export sieht nur das isolierte Ein-Objekt-Scene.

## Dateidialog und Überschreiben

`ExportHelper` öffnet Blenders Standard-Dateibrowser. Unicode-Buchstaben/Ziffern bleiben erhalten; Satzzeichen, Leerzeichen und Pfadtrenner werden zu `_`, Länge begrenzt auf 120 Zeichen plus `.glb`. Beispiel: `Renamed / Castle : 03` → `Renamed_Castle_03.glb`.

Der Operator hält während der Dateiauswahl eine Python-Objektreferenz auf das ursprüngliche aktive Haus. Ein anderer aktiver Kandidat führt zum Abbruch. Marker, eigener Object-Eingang und Dependency-Graph-Eigentümerschaft werden unabhängig davon geprüft.

**Wichtiges GUI-Testergebnis:** `check_existing=True` war allein keine belastbare explizite Überschreibbestätigung. Deshalb zeigt der Operator bei vorhandenem Ziel ein zusätzliches Blender-Bestätigungsfenster **GLB überschreiben?**. Vorher findet keine Geometrieauswertung/Dateierzeugung statt. Escape/Cancel lässt die vorhandene Datei unverändert. Erst der bestätigte zweite Execute-Aufruf erlaubt Ersetzen. Ein direkter Python-Operatoraufruf darf bestehende Dateien nicht still überschreiben.

Ohne Überschreibfreigabe verwendet die Transaktion `os.link` als atomaren No-Clobber-Commit und entfernt danach die temporäre Datei; mit ausdrücklicher Freigabe `os.replace`. Dadurch überschreibt auch ein Rennen mit einer zwischenzeitlich neu erstellten Zieldatei nicht unbemerkt deren Inhalt. Unterstützt ist die getestete Linux-Umgebung mit regulärem lokalen Dateisystem; bei nicht unterstütztem Hardlink schlägt der Export kontrolliert fehl. Fehlende Zielordner werden nicht heimlich erzeugt.

## PBR-Materialstatus

Kein Baking und keine externen Texturen. Jedes verwendete Originalmaterial erhält eine eigenständige temporäre Principled-PBR-Entsprechung. Keine Source-Shader werden bearbeitet.

- `Roof` → tatsächlicher Haus-Eingang `RoofColor`.
- `UpperFloorsPaint` → `PaintColor`.
- `Beam` → originale Schreibweise **`BeamCollor`**.
- Grundgeschosswand / Stein → dokumentierte Phase-3-Grundfarbkonstanten.
- Glas → deckendes Blau-Grau, keine physikalische Transmission.
- Pflanzen/Blüten → explizite Grün-/Blütenfarbpalette für die neu realisierten bekannten IRCSS-Slots, **keine** automatische Principled-Default-Übernahme mit zufällig weißen Blüten.
- Nicht erkannte, tatsächlich benutzte Slots → Braun-Fallback und Warnung. In den geprüften Varianten **keine benutzten unbekannten Slots**. Der unbenutzte leere Slot im Datenblock ist separat in der Materialpolicy erfasst, aber nicht in der GLB.

Die ursprüngliche Putzstruktur, Stein-/Holz-/Dachshader-Variation, Normal-/Bump-Effekte, Glas und prozedurale Blütenfarben sind **nicht vollständig treu**. Pflanzen-Texturen und Alpha-Cutouts werden nicht gebacken; die einfachen PBR-Ersatzmaterialien sind deckend. Der Export ist eine absichtliche einfache Farb-/PBR-Annäherung. Die drei Hausfarben wurden unabhängig gegen die GLB-`baseColorFactor` geprüft. Weiß wäre nur bei absichtlich weißem Eingangs-Putz eine kontrollierte Grundfarbe, kein fehlendes Material. Die Abnahmevarianten verwenden unterschiedliche Putz-/Balken-/Dachfarben.

Weil kein Originalshader gebacken wird, ist kein neues Generated-/Texspace-System erforderlich. Die Phase-4B-Erkenntnis bleibt gültig: Für späteres Baking müssten ursprünglicher direkter Texspace und Triplanar-Attribute erneut erhalten und pro Haus nachgewiesen werden. Das alte HouseOne-Bake wird hier **nicht** blind verallgemeinert.

## Sicherheit und Nachweise

Integration vergleicht vor/nach jedem Export: Szenenobjekte, Matrizen, Inputmeshes, Modifier/echte RNA-Werte, Auswahl/aktiv, Datenblock-Inventar, Assettransformationen, Node-Gruppenreferenzen und originale Materialknoten/-werte/-links. Erfolgs- und injizierte Fehlerpfade werden gleich geprüft. Die gespeicherte Bibliotheksdatei und das Originalasset bleiben byteidentisch. Im gesonderten Guard-Test bleibt auch `bpy.data.is_dirty` **false → false**.

Zusätzlich wird unabhängig vom Exporter die zugehörige Originaloberfläche aufgezeichnet: bijektiver Polygonvergleich mit der realisierten Kopie sowie materialweiser beidseitiger GLB-Positionsvergleich. Siehe [Auswahl/Pivot](PHASE6_SELECTION_AND_PIVOT.md) und [Abschluss](PHASE6_RESULT.md).
