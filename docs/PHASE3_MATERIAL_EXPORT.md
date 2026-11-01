# Phase 3 – HouseOne: reversibler PBR-Materialexport

**Branch:** `experiment/material-export-03`; Ausgangspunkt: Phase-2-Branch `experiment/material-export-02`. Quelle `GeometryNodesFrenchHous.blend` SHA-256 `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5`. Blender 5.2.2 LTS, Godot 4.7 (OpenGL 3). Die Quelle, `GenerateHouse` und frühere Testdateien bleiben unverändert. Vorhandene unversionierte `scripts/phase2_probe.py` und `scripts/phase2_api_probe.py` gehören **nicht** zu Phase 3 und werden nicht committet.

## A: Ursache vor der Konvertierung

`scripts/phase3_audit.py` untersucht das **ausgewertete** HouseOne-Mesh und parst den JSON-Chunk der Phase-2-`BASELINE.glb` direkt. Rohdaten: [`tests/materials/phase3_audit.json`](../tests/materials/phase3_audit.json). Das Mesh hat sechs Slots (`0=None`, fünf belegt), 50.944 Dreiecke; Slot-Triangles: `Roof=7256`, `GroundFloorWalls=20`, `UpperFloorsPaint=2210`, `Beam=4718`, `Stone=36740`. GN-Attribute `RoofColor`, `PaintColor`, `BeamColor` sind `FLOAT_COLOR/POINT`; Samples: `(0.479232,0.055295,0.110550)`, `(1,1,1)`, `(0.270599,0.214137,0.220440)`. Eine vorhandene `UVMap` ist CORNER-basiert. Die konkreten Blender-Principled-Base-Color-Eingänge aller fünf Originalmaterialien sind über Blender-Nodes verknüpft, nicht konstant: Shadergruppen, Noise, Vektor-/Triplanar-Verarbeitung und GN-Named-Attributes; Details in [`MATERIAL_AUDIT.md`](MATERIAL_AUDIT.md). Keine der tatsächlich genutzten Materialketten hat eine Image-Texture-Node (die drei gepackten Bilder im Quellprojekt werden hier nicht referenziert).

Im Phase-2-GLB: fünf Primitives mit Materialindizes `0..4`, fünf PBR-Materialien jeweils nur `metallicFactor=0`, **kein `baseColorFactor`, keine `baseColorTexture`, null Images, null Textures**. Jedes Primitive hat `COLOR_0`–`COLOR_3`, aber diese Kanäle repräsentieren nicht den fertig berechneten Blender-Shader. Somit sind **nicht** alle Farb-/Geometriedaten verloren, und Slotzuweisungen funktionieren; verloren geht die *Verknüpfung/Verarbeitung* der Farben zu Base Color. Der fast weiße Godot-Import ist primär ein exportiertes Material ohne Base Color, **nicht** ein belegter GLB-Container-/Godot-Importdefekt. Die helle Phase-2-Testbeleuchtung überstrahlt zusätzlich wirksame neue Albedos (s. Vergleich); für Phase 3 wurde nur die Godot-Beleuchtung gedimmt.

## B: Minimaler Exportweg

[`scripts/export_houseone_materials.py`](../scripts/export_houseone_materials.py) lädt die Originaldatei, wertet HouseOne mit allen GN-Daten aus, erzeugt eine separate Meshkopie, zentriert XY und setzt den Boden auf Z=0 (genau wie Phase 2). Polygon-Materialindizes bleiben erhalten. Nur **auf dieser Kopie** ersetzt das Skript die fünf benutzten Materialien durch glTF-kompatible `Principled BSDF → Material Output`-Nodes mit Base Color, Metallic 0 und Roughness (bei 1.0 als glTF-Default ausgelassen). Quellwerte: Dach und Balken aus den tatsächlichen **konstanten** evaluierten `RoofColor`/`BeamColor`-Attributen; Putz und Erdgeschosswände aus den originalen Principled-Farb-Defaults; Stein aus dem originalen RGB-Node `Stone/Color`. Die Originalshader haben zwar an diesen Eingängen Links, weshalb Defaults **nur approximative Referenzwerte, nicht das endgültige Shaderergebnis** sind. `PaintColor=(1,1,1)` würde ohne Putz-Shader noch weißer wirken, daher der bereits vorhandene warme Principled-Default. Keine frei gestalteten Ersatzfarben.

Der Export setzt `export_vertex_color='NONE'`: die alten `COLOR_0`–`COLOR_3` sind **keine** fertige Base-Color-Bake, könnten im glTF multipliziert/fehlinterpretiert werden und blähen die Datei auf. Das Skript bricht ab, wenn Dach-/Balkenattribute zwischen Vertices variieren (dann wäre konstantes PBR nicht korrekt). Original-UVs bleiben auf dem Mesh, es findet kein Unwrap statt. Einziger validierter Gebäudetyp: HouseOne; keine spekulative Pipeline für andere GN-Varianten. Das Skript speichert nie eine `.blend`-Datei. GLB-JSON, Materialzahl, fehlende `COLOR_0`, Triangles und Hashes werden nach dem Export überprüft.

## Reproduktion (Repository-Wurzel)

```bash
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/phase3_audit.py
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/export_houseone_materials.py -- --house HouseOne --render
cp tests/materials/phase3/HouseOne_PBR.glb godot-test/assets/HouseOne_Phase3_PBR.glb
godot --headless --path godot-test --editor --import --quit
godot --path godot-test --rendering-driver opengl3 --script res://scripts/phase3_capture.gd -- --output "$PWD/tests/materials/phase3"
```

`--render` ist für den reinen GLB-Export optional. Der Blender-Prozess rendert die **unveränderten Originalshader auf derselben evaluierten Meshkopie** vor dem PBR-Umschalten und die PBR-Kopie mit identischen Cycles-Kameras/Lichtquellen. Godot rendert im grafischen OpenGL-3-Prozess (kein Headless-Screenshot). `tests/materials/phase3/HouseOne_PBR.json`, `tests/materials/phase3_blender.log` und `tests/materials/phase3_godot.log` enthalten Laufbelege. Die beiden GLB-Kopien sind byteidentisch; die Godot-Kopie ist nur ein Importasset. Die bisherigen Baselines bleiben unverändert.

## D: Baking-Entscheidung

Kein Baking-Workflow: die vier Pflichtoberflächen sind mit fünf einfachen PBR-Materialien bereits unterscheidbar. Die vorhandene UVMap allein beweist **keine** überlappungsfreie Bake-UV; weitere Unwraps/Atlanten wären in dieser Phase unnötig und könnten Nähte/Dateigröße verschlechtern. Ein späterer, isolierter **Base-Color-Bake** auf einer weiteren Exportkopie könnte dachziegelweise Töne, Holzmaserung, Steinrauschen sowie Ziegel-/Putzabplatzungen und damit wesentlich mehr Materialtreue bewahren. Vorher UV-Inseln/Überlappungen, Testauflösung, Farbraum, Seams und Godot-Screenshots prüfen; keine Normal-/Metallic-/Roughness-Maps ohne sichtbaren Bedarf.
