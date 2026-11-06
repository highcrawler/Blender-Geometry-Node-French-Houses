# Phase 9D: reproduction (Blender 5.2.2 LTS)

From repository root:

```sh
ROOF09D_AUDIT_ONLY=1 blender -b -t 4 -P experiments/wooden_roof_system_09d/regress.py
blender -b -t 4 -P experiments/wooden_roof_system_09d/regress.py
python experiments/wooden_roof_system_09d/compare_images.py
```

The first command tests eight exact 9B/9C configurations × CLEAN/AGED, reading **both** the pre-fix 9A source from Git commit `de11f7e` and the corrected canonical 9A source, plus the archived 9C Blender file and measurements. It writes `measurements.json` and fails if any regression is detected. The second additionally generates eight genuine Cycles control renders and a four-case `.blend` inspection scene. The third compares the rendered RGB pixels with untouched 9C PNGs and produces two comparison boards and `image_comparison.json` (requires Pillow). None of these commands execute the 9A/9B/9C top-level scripts or overwrite their output artifacts.

`regress.py` reuses the 9B geometry-audit function from its AST, changing **only its test-side expected row count** from `ceil(slope/step)` to the maximum row ID actually found. All existing gap/size/topology assertions and numeric limits remain unchanged. This is necessary because the historical 9B audit predates the skip rule discovered in 9C; the generator fix itself is in `../wooden_roof_system_09a/build.py`. The 9C archive remains a read-only evidence source, not rewritten to say PASS.
