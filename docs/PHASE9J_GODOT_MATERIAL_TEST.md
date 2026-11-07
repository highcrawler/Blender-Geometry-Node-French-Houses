# Phase 9J – GLB und Godot 4.7

Referenz A ist **byteidentisch** mit dem Phase-9I-GLB `clay_constant_A.glb`, SHA-256 `bec98bcb935eda5ff720061679326d5678eb291c802fbae08b46c44dfabba622`. Kandidat B stammt aus einer in Blender 5.2.2 erzeugten, separat mit Meshdaten kopierten A-Szene: gleicher Clay-Export wie 9I `(0,47;0,38;0,28)` linear, Roughness 1, Metallic 0; **nur zusätzlich Weathered Oak** als eigenes Principled-Material mit direkter linearer Base Color `(0,19;0,125;0,077)`, Roughness 1, Metallic 0, keine prozeduralen Nodes/Texturen. Stone, Door und Dach-ID-Referenzen unberührt; Kopien nach Export verworfen. Originalobjekte, Originalmaterial-/Mesh-IDs, Node-Typen, Slot-Indizes, Polygon-Vertices, Transformmatrizen, Auswahl, aktives Objekt und Collection-Hierarchie geprüft; Originaldatei-Hash unverändert. [Blender-Messung](../experiments/weathered_oak_export_09j/blender_audit.json).

Nativer `bpy.ops.export_scene.gltf`: `export_format='GLB'`, `use_selection=True`, `export_yup=True`, `export_apply=False`, `export_materials='EXPORT'`, `export_cameras=False`, `export_lights=False`, `export_extras=True`. Selektiert wurden ausschließlich der kopierte A-Root und 37 kopierte A-Meshes. Godot 4.7 stable `scene`-Import mit Standardparametern aus [Import-Descriptor](../experiments/weathered_oak_export_09j/godot_test/assets/oak_constant_A.glb.import): root_scale 1, deduplicate_surfaces=true, generate_lods=true, materials/extract=0; Capture mit GL Compatibility/OpenGL3. [Godot-Audit](../experiments/weathered_oak_export_09j/godot_audit.json), [automatisierte Materialprüfung](../experiments/weathered_oak_export_09j/material_validation.json), [GLB-Geometrievergleich](../experiments/weathered_oak_export_09j/geometry_comparison.json).

| Godot-Messwert | Referenz A / 9I | Kandidat B / 9J |
|---|---:|---:|
| Meshes / Surfaces / Gesamtdreiecke | 37 / 39 / 14.054 | 37 / 39 / 14.054 |
| Dach / Körper | 13.692 / 362 | 13.692 / 362 |
| Oak-Surfaces / Dreiecke | 22 / 264 | 22 / 264 |
| Oak-Albedo (sRGB) | `(1;1;1;1)` | `(0,473120660;0,388572872;0,307485223;1)` |
| Oak-Roughness / Metallic | 1 / 0 | 1 / 0 |
| Clay-Albedo (sRGB) / Surfaces / Dreiecke | `(0,715240896;0,649956465;0,565728426;1)` / 8 / 74 | **exakt identisch** |
| Rootposition/Rotation/Skalierung | `(0,0,0)` / `(0,0,0)` / `(1,1,1)` | identisch |
| Bounds X/Y/Z | X ±2,89; Y 0…4,528018; Z ±3,935 | identisch |

Aus linear `(0,19;0,125;0,077)` ergibt sRGB-Transfer `1,055 × linear^(1/2,4) − 0,055` den erwarteten Wert `(0,473120623;0,388572859;0,307485185)`; gemessene Godot-Abweichung <2e−5. **Keine Farbkalibrierung.** Die übrigen Materialien sind **Wert für Wert** (Albedo, Roughness, Metallic, Oberflächen, Dreiecke) gleich; Stone/Door bleiben weiß, alle drei verwendeten CLEAN-Dachfarben bleiben unverändert, unbenutzter vierter Dachslot weiterhin ohne Fläche.

GLB-A/B-Vergleich: identische primitive POSITION- und INDEX-Payloads, identische Geometrie-/Materialzuordnung pro Surface (Oak-Namen für den Vergleich normalisiert), Node-Transforms auf 5 Dezimalen gleich (glTF-Quaternion-Float-Serialisierung kann ~1e−7 abweichen). Blender prüft zusätzlich **exakte** Mesh-Vertices, Polygonindizes, Slot-Reihenfolge und Polygon-Materialindizes auf der Kopie. Keine Golden-Meshes überschrieben; Dach und Körper vollständig. Root bei `(0,0,0)` und Bodenhöhe `Y=0` bestätigen Pivot/Orientierung; Null-Material-Surfaces 0. Ein Godot-Import und anschließendes erneutes Audit wurden tatsächlich durchgeführt.
