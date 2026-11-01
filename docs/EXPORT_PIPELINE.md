# Blender → GLB → Godot: geprüfter Pfad

## Reproduktion

```bash
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/build_variants.py -- HouseOne
cp tests/variants/HouseOne.glb godot-test/assets/HouseOne.glb
godot --headless --path godot-test --editor --import --quit
godot --headless --path godot-test --script res://scripts/validate_import.gd
python3 scripts/validate_glb.py
```

Das Skript speichert zuerst eine editierbare `.blend` mit unangetastetem `GenerateHouse`-Modifikator. Anschließend wertet es den GN-Modifikator über den Depsgraph aus (`bpy.data.meshes.new_from_object(..., preserve_all_data_layers=True)`): Das Exportobjekt ist ein eigenständiges, realisiertes Mesh ohne GN-Modifikator. Es verschiebt nur dessen Vertices um die XY-Mitte und die minimale lokale Z-Höhe; damit liegt der Export am Boden mit zentriertem Ursprung und Identitätstransformation, unabhängig von den ursprünglichen Szenenkoordinaten. **Das ist eine Exportkopie, kein Eingriff in den Generator.** Export: Blender glTF-Operator im GLB-Modus, `use_selection=True`, Animationen deaktiviert. Die editierbare Szene wird vor dem temporären Exportobjekt gespeichert.

## Beobachtete Daten

| Haus | Mesh-Vertices | Flächen | Dreiecke | GLB-Bytes |
|---|---:|---:|---:|---:|
| HouseOne | 27.919 | 20.003 | 50.944 | 4.277.728 |
| HouseTWo | 25.326 | 18.253 | 45.926 | 3.797.324 |
| HouseThree | 52.567 | 38.223 | 93.818 | 8.141.508 |

GLB-JSON-Inspektion: je **ein Mesh, ein Node, fünf Dreiecks-Primitives, fünf Materialien**, Attribute `POSITION`, `NORMAL`, `TEXCOORD_0`, `COLOR_0` bis `COLOR_3`. **Keine eingebetteten Bilder/Texturen** (`images=0`, `textures=0`). Blender-Ausgangsmesh hat eine `UVMap`; der erste von sechs Materialslots ist leer und wird nicht als eigenständiges glTF-Material ausgegeben. Die ursprünglichen Blender-Prozeduralshader sind somit nicht als identische Game-Engine-Materialien nachgewiesen. Vor Produktion Farben/Baking, Shaderersatz und UV-Qualität visuell in Godot prüfen. Keine Kollisionsmeshes oder LODs enthalten.

Ein separat kopierter, identischer `HouseOne.glb` liegt in `godot-test/assets/`. Godot **4.7.stable.official** importierte die Szene headless erfolgreich (`--editor --import`: Exit 0); die unabhängige Laufzeitprüfung meldete `GODOT_IMPORT meshes=1 surfaces=5 triangles=50944` (Exit 0). `scripts/validate_glb.py` prüft zusätzlich bei allen drei Dateien GLB-Länge, Dreieckattribute, Normalen, UV, symmetrische X/Z-Grenzen, Grundebene `Y=0` und fehlende Node-Translation. Das beweist Mesh-/Index-Import und lässt noch keine Aussage über sichtbare Materialtreue im Godot-Renderer zu. Die ursprüngliche Blender-Szene hat abweichende weit verschobene Objektkoordinaten; genau deshalb korrigiert der Export die Kopie und exportiert ohne Node-Translation. Blender verwendet Z-up und glTF/Godot Y-up; die glTF-Achsumwandlung übernimmt der Exporter.

## Nächste Schritte für einen produktionsreifen Export

1. Sichtbare Referenzansichten mit Material in Blender und Godot vergleichen; Shader-/Attributfarben gegebenenfalls in PBR-Texturen backen und auf UV-Überlappungen prüfen.
2. Automatisierte Bounding-Box-/Ground-Plane-Prüfung im Godot-Import, Normalen-/Backface- und Kollisionskontrolle ergänzen.
3. Instanzen bei weiteren Gruppen (`HousesOnCurves` insbesondere) explizit vollständig realisieren und Dreieckszahl gegen Export zählen; dieser Audit validiert nur die drei einzelnen `GenerateHouse`-Objekte.
4. Parametrisierte Detailstufen, Mesh-Zusammenführung und Kompression erst nach visueller Qualitätskontrolle und Zielplattform-Budgets einführen.
