# Phase 3 – Ergebnis

**Abnahme: PASS für einen reproduzierbaren, unterscheidbaren HouseOne-Farbexport; visuelle Originaltreue: PARTIAL.** In Godot sind Dach (rot), Fachwerk/Holz (grau-braun), Putz (hell) und Naturstein (beige/helle Steine) sichtbar getrennt. Keine grundlegende Geometrieänderung. Der ursprüngliche fleckige/prozedurale Look ist damit **nicht** rekonstruiert; insbesondere Holz ist zu hell. Weder Texture Baking noch ein neues LOD-/Optimierungsverfahren wurden implementiert.

- Original `GeometryNodesFrenchHous.blend` SHA-256 vor und nach Export: `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5`. `GenerateHouse`, ursprüngliche `tests/variants/HouseOne.blend` und alle Phase-1/2-Tests unverändert; nur neuer Experiment-Branch `experiment/material-export-03`. Ausgangsbranch `experiment/material-export-02`. Änderungen allein auf temporärer evaluierter Exportkopie im Blender-Prozess, `.blend` wird nicht gespeichert.
- Ursache: Die ursprünglichen glTF-Materialien enthielten **keinen `baseColorFactor` und keine `baseColorTexture`**; Blender-Shadergruppen und GN-Attribut-Verknüpfungen für Base Color sind nicht direkt glTF-kompatibel. Die Mesh-/Materialzuordnung und mehrere COLOR-Kanäle waren vorhanden. Technisches Audit: [`PHASE3_MATERIAL_EXPORT.md`](PHASE3_MATERIAL_EXPORT.md), [`phase3_audit.json`](../tests/materials/phase3_audit.json).
- Lösung: fünf einfache Principled-BSDF-Materialien auf der ausgewerteten Meshkopie; nachweislich im GLB vorhandene `baseColorFactor`-Werte, Metallic 0, Roughness 0.877 (Dach) / 1.0 (übrige, glTF-Default). `export_vertex_color='NONE'`, weil vorhandene Kanäle nicht das finale Shaderergebnis enthalten. Alle fünf Mesh-Slots/Primitives korrekt gebunden. Vorgehen: [`scripts/export_houseone_materials.py`](../scripts/export_houseone_materials.py); Reproduktionsbefehle: [`PHASE3_MATERIAL_EXPORT.md`](PHASE3_MATERIAL_EXPORT.md#reproduktion-repository-wurzel).

| Kennzahl | Phase-2-BASELINE | Phase-3-PBR | Differenz |
|---|---:|---:|---:|
| GLB-Dateigröße | 4.277.724 Bytes | 2.424.884 Bytes | −1.852.840 Bytes (−43,31 %) |
| Materialien / Primitives | 5 / 5 | 5 / 5 | 0 / 0 |
| Vertices / Faces / Triangles | 27.919 / 20.003 / 50.944 | 27.919 / 20.003 / 50.944 | 0 / 0 / 0 |
| Images / Textures | 0 / 0 | 0 / 0 | 0 / 0 |
| `baseColorFactor` | 0/5 explizit | 5/5 explizit und verschieden | +5 |
| `COLOR_0`–`COLOR_3` | vorhanden | nicht exportiert | 4 unnötige Kanäle entfernt |

Die geringere GLB-Größe folgt überwiegend dem bewussten Ausschluss der **nicht direkt nutzbaren** Color-Kanäle; kein Polygonoptimierungserfolg. Mögliche künftige Verwendung dieser GN-Attribute benötigt eigenen Vertex-Color-Mapping-Test. Auch die im Source vorhandene UVMap bleibt erhalten; sie beweist keine bakefähigen, überlappungsfreien UVs.

**Nachweisbilder:** [Dreiervergleich Iso](../tests/materials/phase3/comparison_iso.png), [Front](../tests/materials/phase3/comparison_front.png), [Fassade](../tests/materials/phase3/comparison_facade.png) und [Einzelbilder/Beobachtungen](PHASE3_VISUAL_COMPARISON.md). Echte Blender-Cycles- und grafische Godot-OpenGL-3-Screenshots; Kameras entsprechend transformiert, aber Lighting/Tonemapping nicht pixelidentisch. Godot-Importprotokoll: [`tests/materials/phase3_godot.log`](../tests/materials/phase3_godot.log). Exportstatistik und Materialfaktoren: [`tests/materials/phase3/HouseOne_PBR.json`](../tests/materials/phase3/HouseOne_PBR.json).

**Nächste Gebäude:** Je Gebäude erst evaluierte Slots, GN-Attribute/Variabilität und effektive Shaderfarbpfade prüfen. Nicht blind HouseOne-Farbwerte auf andere Häuser übertragen: Skript verweigert absichtlich andere Objektnamen und variable Dach-/Holzattribute. Für höhere Originaltreue danach **optional** isoliertes Base-Color-Baking mit kontrollierten UVs, Seams, Farbraum und Bildvergleich evaluieren; kein automatischer Bake/Atlas ohne Nachweis. Kein Merge nach `main`.
