# Phase 8F: Poly Haven CC0 Thatch auf 8D H

Quellen und Lizenz: [Thatch Roof Angled](https://polyhaven.com/a/thatch_roof_angled) von Poly Haven, [CC0](https://polyhaven.com/license). Die drei unter `textures/` versionierten Original-2K-Bilder stammen direkt von `dl.polyhaven.org` (offiziell unter `https://api.polyhaven.com/files/thatch_roof_angled` ausgewiesen). Exakte URLs, Prüfsummen und Farbräume: [`PHASE8F_CC0_MATERIAL.md`](../../docs/PHASE8F_CC0_MATERIAL.md). Keine Registrierung, kein Checkout. Die vorhandenen 8D-H-Meshes werden nicht umgebaut; nur das CC0-Dach erhält eine UV-Layer und drei Image-Texture-Nodes statt des H-Shaders.

Vom Repo-Root mit Blender **5.2.2**, danach Python/Pillow:

```sh
blender -b -t 4 -P experiments/cottage_generator_08f/compare.py
python3 experiments/cottage_generator_08f/make_board.py
blender -b experiments/cottage_generator_08f/Cottage_CC0_08F.blend -P experiments/cottage_generator_08f/probe_glb.py
```

Erwarte `08F_PASS`, fünf `08F_BOARD_PASS` und `08F_GLB_PROBE_PASS`. Blender kann trotz Python-Traceback Exitcode 0 liefern: Marker und Fehlerausgabe prüfen. Das GLB wird **nur** in `/tmp/` abgelegt. [`measurements.json`](measurements.json) enthält Geometrie- und Texturwerte; `screenshots/` enthält zehn originale Blender-Renderings und fünf lediglich nebeneinander angeordnete Vergleichstafeln. Die 8D-Quellen werden nur importiert/gelesen und nicht verändert. Die `.blend` referenziert Bilddateien relativ (`//textures/`), daher `.blend` und `textures/` zusammen behalten. Der fehlende Qualitätssprung und die zu dunkle Textur sind dokumentierte Ergebnisse, keine Aufforderung zu einem weiteren Materialversuch.
