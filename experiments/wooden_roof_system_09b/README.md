# Phase 9B reproduction

From repository root with Blender **5.2.2** and Pillow (for boards):

```sh
ROOF09B_AUDIT_ONLY=1 blender -b -t 4 -P experiments/wooden_roof_system_09b/audit.py
blender -b -t 4 -P experiments/wooden_roof_system_09b/audit.py
python experiments/wooden_roof_system_09b/make_boards.py
```

The audit script extracts and executes only the four unchanged function definitions from `../wooden_roof_system_09a/build.py` using Python AST. It does **not** import/execute 9A's top-level build (which would overwrite the archived 9A assets). It runs the original Cottage generator for the two configurations in `config.json`. Every run first asserts archive mesh equality against the saved Phase-9A `.blend`, CLEAN/AGED topology equality, deterministic replays and closed-shingle geometry. Audit-only produces `measurements.json` without rendering. Normal mode generates 28 real Cycles PNGs, updated measurements and the four-model inspection `.blend`; the boards are assembled from these PNGs afterward. The 9A tree remains read-only.

The 9A build and board scripts were also replayed in a temporary external directory with their 9A config and original cottage generator linked read-only; they produced all 12 renders, a board and the original triangle/shingle totals. Nothing in Phase 9A was overwritten.
