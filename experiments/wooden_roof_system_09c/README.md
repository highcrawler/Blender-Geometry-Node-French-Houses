# Phase 9C – reproducible bounded validation

From repository root, Blender **5.2.2** (Pillow only for the contact sheets):

```sh
ROOF09C_AUDIT_ONLY=1 blender -b -t 4 -P experiments/wooden_roof_system_09c/validate.py
blender -b -t 4 -P experiments/wooden_roof_system_09c/validate.py
python experiments/wooden_roof_system_09c/make_boards.py
```

The first command produces measurements without rendering. The second runs the identical measurements, renders six CLEAN front images, CLEAN+AGED isometrics for all six and both regression references, and four CLEAN problem-area close-ups; it also saves the sixteen-model inspection `.blend`. The last command assembles four boards from the saved Cycles PNGs. Do not change the threshold constants in the 9B audit: 0.09 m at the gable, 0.04 m between adjacent shingles. Six cases are fixed in `config.json`; no unbounded search occurs.

The script loads unchanged 9A roof function definitions and unchanged 9B geometry-audit functions from their Python AST without executing their top-level scripts (which write into their archived output directories). The 9B strict audit is applied to both references. For the six new cases, its assertions are transformed into recorded failures; an extra recording-only step recognizes the number of *actually produced* rows when 9A's reported `ceil` count differs, so coverage can still be measured. Neither generator nor source audit thresholds are changed. Seed replay, state-geometry equality and saved `.blend` reference fingerprint tests are always executed. All eight configurations use distinct seeds.

A nonzero rendered visual failure must be assessed from the PNGs; the automated PASS/FAIL flags refer to geometric checks and reported metadata, not artistic approval. The run does not modify Phase 8, 9A or 9B outputs.
