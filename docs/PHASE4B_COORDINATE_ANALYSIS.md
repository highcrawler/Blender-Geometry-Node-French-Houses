# Phase 4B – Generated-Koordinaten

## Befund

**Die Putzkoordinaten der bisherigen Phase-4-Meshkopie sind für das tatsächliche Original korrekt.** Der Geometriefehler liegt bei fehlenden Instanzen, nicht beim Phase-4-Putz-PNG. Das ungeprüfte Realisieren aller HouseOne-Instanzen würde jedoch den Texspace verändern. Deshalb wird auf der vollständigen Exportkopie der ursprüngliche **ausgewertete direkte Mesh-Texspace** explizit erhalten.

Keine manuell geschätzte Anpassung, keine neue Schadensmaske, kein Generatorumbau. Es wird kein zusätzlicher Koordinaten-Attributkanal benötigt; das ursprüngliche affine Mapping lässt sich hier vollständig aus Blender-Texspace-Daten ableiten.

## Shaderquellen

Der originale `UpperFloorsPaint`-Shader bleibt unverändert. Vollständiger Shadergraph aus Phase 4: [`source_audit.json`](../tests/baking/phase4/source_audit.json), Erklärung: [Phase-4-Audit](PHASE4_BAKING_AUDIT.md).

- `Texture Coordinate.Generated` speist Putzvariation und die originale Noise-/Map-Range-Schadensmaske.
- Ziegelprojektion: `LocalPosition` (POINT/FLOAT_VECTOR) und `LocalNormal` (CORNER/FLOAT_VECTOR), nicht die Bake-UVs. `PaintColor` ist das GN-Farbattribut.
- Der Base-Color-Pfad hängt weder von Bake-UV noch von einem externen Object-Coordinate-Referenzobjekt ab.
- Normal-/Bump-Pfade sind separat und werden weiterhin nicht gebacken.
- Die neuen Pflanzen-/Fensterinstanzen besitzen teils eigene ursprüngliche Koordinatenräume; deren prozedurale Materialtreue ist **nicht** durch das Fixieren des Hauptmesh-Texspace bewiesen. Es wird ausschließlich der Putz gebacken. Kein Putzmaterial kommt in den getrennten Instanzblättern vor.

## Welche Bounding Box ist relevant?

Generated entspricht auf dem direkten HouseOne-Mesh im getesteten Cycles-Pfad der affinen Abbildung

`G = (local_position - texspace_location) / (2 * texspace_size) + 0.5`.

Der belegte Texspace vor der Realisierung:

```
location = ( 0.2749263048, -0.0458972454, 3.8331906796)
size     = ( 1.9639080763,  3.2427241802, 4.0750875473)
```

`size` sind Halbausdehnungen, keine vollen Abmessungen. Die Input-Quad-Daten von `HouseOne.data` haben dagegen

```
location = (0.2602571845, -0.0453312397, -0.0154382288)
size     = (1.5434243679,  2.9279062748,  0.0154382288)
```

**Diese Input-Quad-Werte sind nicht der ursprüngliche Render-Bezugsraum.** Ein expliziter Vorversuch damit erzeugte deutlich falsche, stark vergrößerte Z-Koordinaten und wurde verworfen. Die Diskrepanz zwischen Eingabe- und Auswertungsmesh allein beweist keinen Fehler von Phase 4.

Nach Realisierung erweitert Pflanzengeometrie die Meshgrenzen in Y. Ein neues Auto-Texspace des gesamten Meshes normalisiert daher anders. Minimale Korrektur ausschließlich an `fixed = realized_mesh.copy()`:

```python
fixed.use_auto_texspace = False
fixed.texspace_location = phase4_direct_mesh.texspace_location
fixed.texspace_size = phase4_direct_mesh.texspace_size
```

Lokale Geometrie und GN-Attribute bleiben erhalten. Objektpositionen werden für die Vergleichsbilder nicht verändert; die abschließende GLB-Zentrierung verwendet nur den Objekttransform. Zur Laufzeit liest das PBR-Material ausschließlich die gebackenen UVs, nicht mehr Generated.

## Tatsächliche Referenz statt verschobener GN-Kopie

`GenerateHouse` enthält `GetPositionBasedSeed`, das Object-Info-Location aus `Self Object` verarbeitet. Eine vor der Auswertung zentrierte Kopie kann deshalb **andere Fenster-/Pflanzenverteilungen** erzeugen, auch wenn Modifier und Eingabemesh gleich erscheinen. Das erklärt die irreführende Phase-4-GN-Kontrolle und den ersten Kontrollkopien-Vorversuch dieser Phase.

A verwendet jetzt **das tatsächliche ursprüngliche HouseOne**, ohne Transformänderung. Kamera/Licht werden in dessen Weltkoordinaten ausgerichtet. C wird ebenfalls zuerst an der Originalposition ausgewertet. Erst das fertig ausgewertete Mesh wird beim Export zentriert. Das verhindert eine unbemerkte Änderung des Seed-Raums. Die Korrektur benötigt keinen Eingriff in die Seed-Logik.

## Float-Nachweis

Scene-Materialoverride: `Generated → Emission`, Ausgabe **32-Bit OpenEXR**, keine Farb-/Beleuchtungsanpassung. PNG-Diagnosen verwenden nur zur Sichtbarkeit die feste Darstellungsskala 0,01; die Metrik wird auf unskalierten EXR-Werten berechnet.

Eine per BVH-Raycasts aus den realisierten Originalpolygonen ermittelte Sichtbarkeitsmaske enthält ausschließlich tatsächlich sichtbaren Putz. Zwei Pixel Erosion schließen antialisierte Materialgrenzen aus. Die Fassade liefert **101.588** Vergleichspixel. Das ist keine frei ausgesuchte Rechteckregion.

| Vergleich mit tatsächlichem Original | mittlerer absoluter Koordinatenfehler | maximaler Fehler |
|---|---:|---:|
| Phase4 direktes Mesh | **0** | **0** |
| nur realisiert, neuer Auto-Texspace | 0,0008922779 | 0,0052191429 |
| realisiert + erhaltener ursprünglicher Texspace | **0** | **0** |

Float-Renderings, Sichtbarkeitsmaske und Zahlen: [`geometry.json`](../tests/baking/phase4b/geometry.json), `coordinates_float_*_facade.exr`, `plaster_mask_facade.png`. Diese Messung ist ein direkter Fassadennachweis, keine behauptete Pixelverifikation jeder verdeckten Fläche. Die identischen ursprünglichen Texspace-Parameter und unveränderten lokalen Putzpositionen liefern zusätzlich die objektweite mathematische Begründung.

Die triplanaren Attribute `LocalPosition` und `LocalNormal` wurden auf **allen ursprünglichen Putzpunkten/-ecken** gegen die vollständige Exportkopie geprüft: maximale Abweichung jeweils **0**. Keine neue Tri-/UV-Projektion im Originalshader.

## Bake-Nachweis und Grenzen

Der neue Bake auf vollständiger Geometrie erzeugt exakt dasselbe UV-Layout und exakt dieselben PNG-Bytes wie Phase 4:

`1fef33e7b37104a491fe53584ff1e1b2284d0e169c3334e8d455a14d6bb7e2fd`.

Das ist ein positives Ergebnis, kein unterlassener Test: zweimal gebacken pro Blender-Prozess und zusätzlich in unabhängigen Prozessen wiederholt. Originaler Color-Pfad, Cycles CPU DIFFUSE/COLOR, 1024² sRGB, kein Direct/Indirect, 8 Pixel EXTEND. Kein Normal-/Roughness-/anderes Material-Bake.

Der korrekte Phase-4-Bake muss also **nicht optisch verschoben oder neu entworfen** werden. Er kann auf der vollständigen Geometrie unverändert reproduziert werden. Ein erneuter Bake wurde nur zum Nachweis der korrigierten Geometriemethode erzeugt.

1024²-Resampling bleibt verlustbehaftet, Original-Bump fehlt. Exakte Übereinstimmung der Generated-Werte bedeutet nicht pixelidentisches beleuchtetes Endbild oder generelle Übertragbarkeit auf jeden GN-Instanzshader.
