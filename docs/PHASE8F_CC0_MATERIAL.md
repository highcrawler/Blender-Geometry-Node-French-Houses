# Phase 8F – CC0-Material und technische Umsetzung

Ausgangspunkt: eigenständiger Phase-8D-Branch `experiment/procedural-cottage-thatch-08d`, Commit `e6ec104`, Blender **5.2.2 LTS**. Long Cottage **5,1 × 7,3 m**, Wandhöhe **2,3 m**, Dachneigung **40°**, Seed **23**. Baseline ist **H samt Originalmaterial**, nicht die ältere 8B-Baseline. Im separaten `experiment/cottage-cc0-thatch-08f` werden H und eine **geometrisch identische** zweite Cottage jeweils frisch generiert. Lediglich die fünf vorhandenen H-Dachobjekte in der zweiten Kopie erhalten neue UV-Loop-Koordinaten und **ein** neues Material. Keine neuen Dach-Meshes, Änderungen an Wänden, Balken, Tür oder anderen Generatoren.

## Quelle und Nutzungsrechte

- [Poly Haven: Thatch Roof Angled](https://polyhaven.com/a/thatch_roof_angled), [offizielle CC0-Lizenz](https://polyhaven.com/license), [öffentliche Poly-Haven-API](https://polyhaven.com/our-api). Poly Haven erklärt ausdrücklich kommerzielle Nutzung und Weitergabe für die Website-Assets als erlaubt; Namensnennung ist nicht vorgeschrieben, hier bewusst beigefügt.
- Über den öffentlich lesbaren offiziellen API-Endpunkt `https://api.polyhaven.com/files/thatch_roof_angled` wurden **nur** die vom Anbieter direkt ausgewiesenen `dl.polyhaven.org`-Dateilinks für 2K verwendet; keine Anmeldung, kein Checkout, keine Shop-Quelle. Assetseite nennt JPEG, PNG, EXR, Blend, glTF, MaterialX und ZIP bei verfügbaren Auflösungen 1K–8K. Displacement wurde **nicht** bezogen und nicht zur Geometriegewinnung benutzt.

| Kanal → Principled | Datei in [`textures/`](../experiments/cottage_generator_08f/textures/) | Format/Farbraum | Größe auf Platte / SHA-256 |
|---|---|---|---|
| Base Color | [`thatch_roof_angled_diff_2k.jpg`](../experiments/cottage_generator_08f/textures/thatch_roof_angled_diff_2k.jpg) | 2048², JPEG, **sRGB** | 3.225.496 B / `dd544436986e9be6ae80996fbd132c67b38c81e8ed1b7c4384a961efe87460b7` |
| Normal → Tangent Normal Map → Normal | [`thatch_roof_angled_nor_gl_2k.png`](../experiments/cottage_generator_08f/textures/thatch_roof_angled_nor_gl_2k.png) | 2048², PNG, **Non-Color**, OpenGL (+Y) | 23.572.093 B / `62128242ad200e3aa5aa30d1249d107bee3548e028bee037718dc0aa2e949cc7` |
| Roughness | [`thatch_roof_angled_rough_2k.png`](../experiments/cottage_generator_08f/textures/thatch_roof_angled_rough_2k.png) | 2048², 16-bit Graustufen-PNG, **Non-Color** | 6.847.778 B / `81c9ace60bdeaeb88c1edd08823831958c035763f3ce46eda6b71dc6c8383e65` |

Summe Quelldateien: **33.645.367 B** auf Platte (nicht RAM). Drei 2048²-Images; Roughness nicht versehentlich als sRGB. Principled Metallic **0**, Normal-Strength 1; die drei Bilder sind direkt mit UV-Sockets verbunden. **Keine** zusätzliche Rauschmischung, Farbkorrektur oder Displacement; die dunkle Ausgangsfarbe ist daher ein reales Ergebnis der gewählten Textur.

## UV und Reproduzierbarkeit

Der CC0-Kopie wird ausschließlich die UV-Loop-Ebene `08F_RoofSlope` hinzugefügt; keine Vertexposition, Topologie oder Polygonanzahl ändert sich. Die aufrechte Faserorientierung der Originalbilddatei wird auf **V = Abstand vom First zur Traufe** auf beiden Dachseiten projiziert; U verläuft entlang der Hauslänge. Gemeinsames projektives Kacheln von **0,9 m** statt separatem 0–1-UV pro Bündel, um sichtbare Miniatur-Wiederholung zu vermeiden. Giebel-/Traufschnittflächen und beide First-Endkappen erhalten passende lokale Planar-UV, statt 1D-kollabierter UVs; **11.728 Loops auf fünf Dachobjekten und 0 UV-Flächen mit Nullfläche** geprüft. Dünne Schnittflächen sind trotzdem graphisch sehr dunkel; außerdem wird die reale, gealterte Materialfarbigkeit nicht passend zur stilisierten beige Cottage-Palette umgefärbt. Die 0,9-m-Kachelung ist eine für dieses Haus getestete Skalierung, keine Zusicherung realer Strohhalm-Maße.

Reproduktion vom Repository-Root (Pillow nur für Tafeln):

```sh
blender -b -t 4 -P experiments/cottage_generator_08f/compare.py
python3 experiments/cottage_generator_08f/make_board.py
blender -b experiments/cottage_generator_08f/Cottage_CC0_08F.blend -P experiments/cottage_generator_08f/probe_glb.py
```

`compare.py` prüft die gesamte Geometrie per Objekt-Multimenge **gegen das archivierte 8D-H-`.blend` und zwischen beiden neuen Zuständen**, wiederholt für sämtliche Nicht-Dachobjekte implizit. Beide haben **5.872 Dach-Dreiecke, 6.234 insgesamt, 5 Materialien**. Beide H-Bilder des neuen Renders sind **pixelgenau identisch** mit den entsprechenden Original-8D-H-Renderbildern (ISO, Front, Dach, Traufe und ~300 px). Die Creation-Messung in [`measurements.json`](../experiments/cottage_generator_08f/measurements.json) erfasst je **einen** Generatorlauf, nicht den Materialshader-Lauf, Renderkosten, Blender-RAM oder FPS. `.blend` mit relativen, separat versionierten Texturpfaden: **242.689 B**, nach eigenständigem Blender-Neuöffnen alle drei Pfade gültig.

## Isolierter glTF-Test, keine Godot-Pipeline

Das Skript `probe_glb.py` exportiert **ausschließlich die fünf CC0-Dachobjekte** als temporäre `/tmp/cottage_08f_roof_probe.glb` (nicht eingecheckt) und kontrolliert das GLB-JSON. Ergebnis: **30.813.760 B**, **5.872 Dreiecke**, **1 Material**, **3 Bilder** im Dach-only-Export, `TEXCOORD_0` auf allen Mesh-Primitives, `baseColorTexture`, `normalTexture`, `metallicRoughnessTexture` und `metallicFactor=0`. Der Export beweist eine prinzipiell unterstützte glTF-PBR-Verschaltung, **keinen** Godot-Lauf, keine Spiel-FPS, keine ideale Texturgröße und keine Freigabe der dunklen Gestaltung. Ein allgemeiner Export-Workflow wurde nicht gebaut.
