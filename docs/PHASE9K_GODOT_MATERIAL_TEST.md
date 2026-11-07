# Phase 9K – nativer GLB-Export / tatsächlicher Godot-4.7-Import

Referenz: byteidentische Kopie des **9J-Long-CLEAN-A-GLB**. Die isolierte 9K-Kopie nutzt Blenders nativen `bpy.ops.export_scene.gltf` mit `export_format='GLB'`, `use_selection=True`, `export_yup=True`, `export_apply=False`, `export_materials='EXPORT'`, `export_cameras=False`, `export_lights=False`, `export_extras=True`. Nur A-Root und 37 private A-Mesh-Kopien selektiert. Godot **4.7 stable**, `scene`-Importer/Standardparameter aus [`.glb.import`](../experiments/stone_door_export_09k/godot_test/assets/stone_door_constant_A.glb.import) (root_scale 1, deduplicate_surfaces=true, materials/extract=0), GL Compatibility/OpenGL3. [Blender-Audit](../experiments/stone_door_export_09k/blender_audit.json) · [Godot-Surface-Messung](../experiments/stone_door_export_09k/godot_audit.json) · [Assertions](../experiments/stone_door_export_09k/material_validation.json) · [GLB-Primitive-Vergleich](../experiments/stone_door_export_09k/geometry_comparison.json).

| Material / Godot-Albedo (sRGB) | 9J-Referenz | 9K-Kandidat | Surfaces / Dreiecke 9K |
|---|---|---|---:|
| Clay | `(0,715240896;0,649956465;0,565728426;1)` | **exakt identisch** | 8 / 74 |
| Weathered Oak | `(0,473120660;0,388572872;0,307485223;1)` | **exakt identisch** | 22 / 264 |
| Stone | `(1;1;1;1)` | `(0,592619359;0,574871063;0,537098706;1)` | 1 / 12 |
| Door | `(1;1;1;1)` | `(0,537098706;0,423582882;0,322726130;1)` | 1 / 12 |

Erwartete sRGB-Werte per `1,055 × linear^(1/2,4) − 0,055` (alle linearen Komponenten oberhalb der sRGB-Knickstelle): Stone `(0,592619373;0,574871017;0,537098730)` aus `(0,31;0,29;0,25)`; Door `(0,537098730;0,423582871;0,322726115)` aus `(0,25;0,15;0,085)`. Importabweichungen <2×10⁻⁵. Alle vier Körpermaterialien haben nun nichtweiße Godot-Albedowerte; **keine Farbkalibrierung**. Stone/Door Roughness **1**, Metallic **0**; alle drei CLEAN-Dachmaterialien (Roughness 0,92, Metallic 0) samt Surfaces/Albedo **Wert für Wert unverändert**. Der vierte CLEAN-Dachslot ist unbenutzt.

**Regression:** beide GLBs **37 Meshes, 39 Surfaces, 14.054 Dreiecke** (13.692 Dach, 362 Körper), keine Nullmaterialflächen. Exportierte Primitive: identische POSITION/INDEX-Payloads und zugehörige Materialzuordnung pro Surface (nur Stone-/Door-Namen normalisiert); Node-Transforms bis 5 Dezimalen gleich, nur minimale glTF-Float-Quaternion-Serialisierung. Blender überprüft exakt Vertexpositionen, Polygon-Vertices, Polygon-Slot-Indizes und Matrixelemente auf Quell-/Kopiermesh. Godot-Bounds identisch: X ±2,89, Y `0…4,528018`, Z ±3,935; A-Root Translation/Rotation `(0,0,0)`, Skalierung `(1,1,1)` und korrekter **Boden-Pivot**. Keine historischen Golden-Meshes überschrieben. Quelle `.blend` SHA-256 vorher/nachher unverändert. Kein neuer Exporter/Writer.
