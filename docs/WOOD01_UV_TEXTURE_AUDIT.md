# WOOD-01 – Quelle, UV-Richtung, Kosten

**Poly Haven [Rough Wood](https://polyhaven.com/a/rough_wood)**: CC0, Autor **Rob Tuytel**, überprüft über [Asset-Info](../experiments/wood_beam_material_01/textures/polyhaven_asset_info.json) und die [Poly-Haven-Datei-API](../experiments/wood_beam_material_01/textures/polyhaven_files_api.json). A/B/C sind dieselben 37 A-Meshes; nur 16 Fachwerkbalken (192 der 264 Oak-Dreiecke) bekommen in B/C ein anderes Material, die übrigen 72 Oak-Dreiecke einschließlich der Türteile bleiben konstant. Das komplette B-Originalbild [1K-Diffuse](../experiments/wood_beam_material_01/textures/rough_wood_diffuse_1k.jpg) zeigt deutlich mehrere alte **aneinanderstoßende Planken**, dunkle Längsfugen und sogar kurze Querstöße. Dies sind physische Board-Joints in der Textur, **nicht** eine plausible Eigenschaft eines monolithischen Fachwerkbalkens. Die getestete U-Teilstrecke `0,32…0,48` ist kein sicheres Entfugen: sie schneidet nahe der Bildmitte durch eine Längsfuge; dunkle Schnittkanten erscheinen auf einzelnen Balken. Die Kappen verwenden eine 0…1-Projektion und können das gesamte Plankenbild zeigen. B ist deshalb in dieser Form **nicht für massive Balken geeignet**.

Die ursprünglichen Balken besitzen keine UV-Schicht. Nur die isolierten Meshkopien bekommen eine UV-Schicht: Querschnitt lokale X/Y, **V-Achse entlang lokaler +Z-Balkenlänge**. Da die Objekte mit dem Balken als +Z-Achse rotiert sind, bleibt die Maserung bei vertikalen, horizontalen und diagonalen Balken längs ausgerichtet, ohne Weltprojektion. Side-Faces projizieren eine ihrer lokalen X/Y-Koordinaten als U; Kappen projizieren X/Y. V spannt `L / 1,5 m` pro Balken auf; Repeat bei >1. B nutzt U=`0,32+0,16·(Querschnittsfraktion)`, C U=`0…1`. [16 explizite Achsen/Längen/UV-Spans pro Variante](../experiments/wood_beam_material_01/blender_audit.json), [Godot-UV-Counts pro Mesh](../experiments/wood_beam_material_01/godot_audit.json).

| Typ (Stichprobe) | lokale Breite / Länge | Welt-Längsvektor (Blender XYZ) | V-Spanne | B-Texel/phys. Meter quer / längs |
|---|---|---|---:|---:|
| CornerPost senkrecht | 0,16 / 2,14 m | `(0,0,1)` | 1,427 | 1.024 / 683 |
| SideWallPlate waagerecht | 0,13 / 7,30 m | `(0,1,0)` | 4,867 | 1.260 / 683 |
| SideBrace diagonal | 0,09 / 1,535 m | `(0,±0,410,0,912)` | 1,023 | 1.820 / 683 |
| GableRafter diagonal | 0,115 / 3,329 m | `(0,766,0,0,643)` | 2,219 | 1.425 / 683 |

**Prüfergebnis UV:** Richtung und meterbasierte Längsdichte sind korrekt. Die Querdichte von B schwankt mit der Balkendicke und ist höher als die Längsdichte (ca. **1,5–2,7×**); auf langen Platten wiederholt sich das Bild bis ~4,9-mal. C hat 512 px auf nur 0,09–0,16 m Querschnitt versus 512/1,5 ≈341 px/m in Längsrichtung: **~9–17× anisotrop**, sehr feine Streifen und Verblassen bei ~300 px Gebäudehöhe. Kein Beleg für ein sauber austariertes Produktions-UV/LOD. Kappen sowie Nähte sind im Detail weiter zu verbessern. Keine gestreckte oder quer stehende Holzmaserung auf getesteten Seitenflächen; sichtbare Texturprobleme liegen vor allem in Brettfugen, UV-Maßstab und Kontrast.

| Textur / exportiertes GLB | Bytes |
|---|---:|
| B Diffuse 1024² JPEG | 567.074 |
| B Normal GL 1024² PNG | 1.910.586 |
| B Rough 1024² JPEG | 195.056 |
| C Color-Only Bake 512² PNG | 232.435 |
| A GLB (9K-Referenz) | 783.288 |
| B GLB inkl. eingebetteter Maps | 3.964.744 (**+3.181.456**) |
| C GLB inkl. eingebetteter Map | 1.021.584 (**+238.296**) |

Godot-Importcache-Größe ist system-/importabhängig, hier gemessen **5.746.169 Bytes insgesamt** für alle drei GLBs; dies ist kein Runtime-VRAM-Messwert. Theoretischer *uncompressed* RGBA8-Mip-Budget-Richtwert für B 3×1024²: ~**16 MiB** bei vollen Mips, C 512²: ~**1,33 MiB**, ohne plattformspezifische GPU-Kompression, Kopien oder geänderte Kanäle. Die importierten Godot-Texture2D-Formate sind `CompressedTexture2D`; tatsächlicher VRAM wurde **nicht gemessen**. [Automatischer Kostenbericht](../experiments/wood_beam_material_01/validation.json).
