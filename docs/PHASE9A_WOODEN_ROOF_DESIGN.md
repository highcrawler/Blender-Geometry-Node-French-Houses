# Phase 9A — Wooden roof design

Baseline: `f4f3651`, Blender 5.2.2; isolated branch `experiment/wooden-roof-system-09a`. Only the Long Cottage (`5.1 × 7.3 m`, wall `2.3 m`, pitch `40°`, seed `23`) is used. Existing addon, IRCSS source and all Phase-8 experiments remain untouched.

`experiments/wooden_roof_system_09a/build.py` calls the original cottage generator, removes only objects marked `role=roof`, then adds two thin closed deck slabs, one combined mesh of 1,137 individual closed wooden shingles and two closed overlapping ridge planks. Twenty courses with 0.185 m exposure and ~0.315 m shingle length give ~41% overlap. Shingle width is seeded, bounded ~0.205–0.335 m; alternating course offset and small cut/length perturbations break repetition. Each shingle contributes 12 triangles. The single combined shingle mesh avoids 1,137 Blender objects. Thin tapered shingle ends and the underdeck make the roof edge tangible without fibers or texture-only tricks.

CLEAN and AGED use precisely the same vertex/face coordinates (asserted), the same cottage and the same number of material slots. Only four roof-material palettes/face indices change: warm natural brown versus weathered desaturated wood. A muted moss-tinted fourth material appears on 36 of 1,137 shingles (~3.2%) in selected damp/shaded edge and ridge courses on one slope; no moss geometry or green carpet. All shaders are rough, nonmetallic, solid colors. No external textures, UV maps or image dependencies: UV mapping issues are not applicable to this version. The roof is not a new building type or settlement feature.

Reproduction from repository root (Blender 5.2.2, Python Pillow for board):

```sh
blender -b -t 4 -P experiments/wooden_roof_system_09a/build.py
python experiments/wooden_roof_system_09a/make_board.py
```

The build generates twelve actual Cycles PNGs (12 samples, denoised, identical camera/light per state), `measurements.json`, and a reusable `.blend` with the two houses spaced apart after rendering. The comparison board composites existing renders; the native 480×360 `iso_300` renders are not upscaled. Run time is machine-dependent and measured generation time excludes rendering and saving. No FPS inference is made.
