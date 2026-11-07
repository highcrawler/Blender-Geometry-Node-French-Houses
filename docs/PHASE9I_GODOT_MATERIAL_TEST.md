# 9I – nativer Export, Godot-Import, Regression

Testobjekt Long Cottage A CLEAN (5,1 × 7,3 m, Wand 2,3 m, Dach 40°, Seed 23). In einem **eigenen** Godot-4.7-Projekt wurden eine unveränderte 9H-A-GLB-Kopie und die 9I-GLB geladen. Export: Blender 5.2.2 `bpy.ops.export_scene.gltf(filepath=…, export_format='GLB', use_selection=True, export_yup=True, export_apply=False, export_materials='EXPORT', export_cameras=False, export_lights=False, export_extras=True)`. Nur der kopierte A-Root und seine 37 kopierten Meshes ausgewählt; keine fremden Gebäude exportiert. Godot 4.7 stable, GL Compatibility/OpenGL3, `scene`-Importer, Standardparameter aus [import descriptor](../experiments/clay_material_export_09i/godot_test/assets/clay_constant_A.glb.import), u.a. root_scale 1, deduplicate_surfaces=true, generate_lods=true, extract materials=0. [Audit](../experiments/clay_material_export_09i/godot_audit.json), [Validierung](../experiments/clay_material_export_09i/material_validation.json), [vollständiger GLB-Vergleich](../experiments/clay_material_export_09i/geometry_comparison.json).

| Prüfung | Baseline 9H | 9I |
|---|---:|---:|
| Meshes / Surfaces / Dreiecke | 37 / 39 / 14.054 | 37 / 39 / 14.054 |
| Dach / Körper Dreiecke | 13.692 / 362 | 13.692 / 362 |
| Clay Surfaces / Dreiecke | 8 / 74 | 8 / 74 |
| Clay Albedo in Godot `StandardMaterial3D` | (1, 1, 1, 1) | (0,71524090; 0,64995646; 0,56572843; 1) |
| Clay Roughness / Metallic | 1 / 0 | 1 / 0 |
| Bounds Y / Rootposition | 0 bis 4,528018 / (0,0,0) | identisch |

**Farbraum:** Blender Principled linear `(0,47; 0,38; 0,28)` → glTF `baseColorFactor` in sRGB → Godot Material-Albedo `(0,71524090; 0,64995646; 0,56572843)`. Berechnet mit sRGB-Transferfunktion `1,055 × linear^(1/2,4) − 0,055`, erwartete `(0,715240884; 0,649956455; 0,565728433)`; Fehler unter 2e−5. Daher ist der scheinbare RGB-Zahlenunterschied **kein Farbverlust**, keine Kalibrierung gerechtfertigt. Die beobachtete Bildabweichung wird nicht durch Korrektur des Materialwerts maskiert.

Alle übrigen sechs verwendeten Materialeinträge einschließlich der drei CLEAN-Dachmaterialien haben exakt dieselben Godot-Albedo/Roughness/Metallic/Surface-/Dreieckswerte wie die Baseline; die drei anderen Körperfarben sind erwartungsgemäß **weiterhin weiß**. Das CLEAN-Dach hat einen weiteren unbenutzten Slot ohne importierte Polygone. Kein Dach-/Körperverlust, bounds X ±2,89; Z ±3,935, Y≥0; A-Root Translation/Rotation `(0,0,0)`, Scale `(1,1,1)`; Import-Achsen stimmen mit 9H überein. GLB-Primitiven vergleichen exportierte POSITION- und INDEX-Werte exakt, zugehörige Node-Matrizen/Translationen/Rotationen bis fünf Dezimalstellen (maximale beobachtete Quaternion-Serialisierungsabweichung ~6e−8); Meshgeometrie und Positionsindizes stimmen überein. Polygon-Indizes und Material-Slot-Indizes wurden vorher im Blender-Kopiervorgang exakt verglichen. Kein neues Golden-Mesh.

Godot wurde nach dem letzten Export erneut mittels `audit.gd` ausgeführt; `validate.py` prüft auch Originaldatei-Hash und identische Dachmaterialwerte. Der unabhängige 9H-Baseline-GLB ist die eingefrorene Importreferenz. `Godot`-Screenshots: [weiß](../experiments/clay_material_export_09i/screenshots/baseline_godot.png), [konstanter Clay](../experiments/clay_material_export_09i/screenshots/constant_godot.png).
