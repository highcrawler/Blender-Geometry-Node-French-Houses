# Phase 9K – gespeicherte Stone-/Door-Shader

Quelle: unverändertes 9F-`experiments/wooden_roof_system_09f/three_owned_cottages.blend` (SHA-256 **`38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae`** vor und nach dem Blender-Test). In der 5.2.2-Prozesskopie wurden Material-IDs aus **tatsächlich belegten A-Mesh-Slots** ermittelt und durch Node-/Polygonprüfung bestätigt; Namen dienen nur zur Diagnose. Vollständiges [Audit-JSON](../experiments/stone_door_export_09k/blender_audit.json).

Beide gespeicherten Shader: `Texture Coordinate.Generated → Noise Texture.Vector (Scale 5, Detail 2)`, `Noise.Factor → ColorRamp.Factor → Principled BSDF.Base Color → Material Output.Surface`. Roughness **1**, Metallic **0**; Positionen der ColorRamp **0,24** und **0,78**. Keine Base-Color-Texturen.

| Original-Material | lineare Grundfarbe | Ramp links (linear) | Ramp rechts (linear) | tatsächlich belegtes Mesh / Polygone / Dreiecke |
|---|---|---|---|---|
| `08A_09F_A_stone` | `(0,31;0,29;0,25)` | `(0,2821;0,2639;0,2275)` | `(0,3379;0,3161;0,2725)` | `08A_Sill` / 6 / **12** |
| `08A_09F_A_door` | `(0,25;0,15;0,085)` | `(0,2275;0,1365;0,07735)` | `(0,2725;0,1635;0,09265)` | `08A_Door` / 6 / **12** |

Beide Ramp-Endpunkte liegen ±9 % um ihre Grundfarbe; die tatsächliche Noise-Verteilung ist nicht auf allen Pixeln pauschal ±9 %. Historische Clay- und Oak-Shader wurden nur gelesen und sind unverändert. In der **privaten** A-Exportkopie wurden für Stone und Door neue Principled-Material-IDs mit den obigen *konstanten linearen Grundfarben* und den aus der gespeicherten Szene übernommenen Roughness-/Metallic-Werten erstellt. Clay `(0,47;0,38;0,28)` und Oak `(0,19;0,125;0,077)` wurden exakt nach 9I/9J als unveränderte Exportkonstanten reproduziert. Nur belegte Kopie-Slots dieser vier Materialien werden für den GLB-Export ersetzt; **9K ändert ausschließlich die Stone-/Door-Darstellung gegenüber dem byteidentischen 9J-Referenz-GLB**. Alle übrigen Quellmaterialien, Dachmaterialien und andere Häuser blieben unverändert. Private Kopien wurden anschließend entsorgt; Quell-Material-Nodes/Werte/Links, fremde Meshes, Meshgeometrie, Root, Collections und Auswahl vor/nach geprüft.
