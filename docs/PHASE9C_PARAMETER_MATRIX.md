# Phase 9C — fixed parameter matrix

Supported limits, read from `Cottage.validate()` in the unchanged cottage generator: width **3–8 m**, depth **2.8–9 m**, wall height **2–3 m**, roof pitch **35–60°**, seed nonnegative 32-bit integer. Exactly six new valid configurations, no parameter substitutions or search; reference Long and Compact remain unchanged.

| Case / focus | Width × depth m | Wall m | Pitch | Seed | Courses reported / observed per side | Shingles | Roof / total triangles | Generation CLEAN ms | Gable gap m | Internal gap m | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| T01 narrow | 3.0 × 4.3 | 2.0 | 42° | 31 | 13 / 13 | 464 | 5,616 / 5,978 | 35.88 | 0.05519 | 0.02310 | PASS |
| T02 wide | 8.0 × 5.2 | 3.0 | 42° | 37 | 31 / 31 | 1,302 | 15,672 / 16,034 | 65.24 | 0.06812 | 0.02366 | PASS |
| T03 short | 5.2 × 2.8 | 2.4 | 44° | 41 | **22 / 21** | 524 | 6,336 / 6,698 | 43.83 | 0.08093 | 0.02285 | **FAIL: row count** |
| T04 long | 5.0 × 9.0 | 2.5 | 44° | 43 | 21 / 21 | 1,446 | 17,400 / 17,762 | 98.37 | 0.06727 | 0.02334 | PASS |
| T05 shallow | 5.0 × 5.0 | 2.2 | 35° | 47 | **19 / 18** | 737 | 8,892 / 9,254 | 71.54 | 0.08324 | 0.02318 | **FAIL: row count** |
| T06 steep | 5.0 × 5.0 | 2.8 | 60° | 53 | 29 / 29 | 1,179 | 14,196 / 14,558 | 89.15 | 0.07205 | 0.02318 | PASS |

All six use eight unique building materials in CLEAN and in AGED, with identical mesh geometry/counts per state. Duration is one local run per state, excluding rendering, **not** a benchmark. AGED timings and every raw metric are in [measurements.json](../experiments/wooden_roof_system_09c/measurements.json). Limits for this test remain **gable <0.09 m** and **internal <0.04 m**; all six satisfy these bounds. T03/T05 FAIL solely because the returned `courses` field disagrees with the actually built rows: a real consistency bug, not an adjusted acceptance threshold. The final generated course nonetheless reaches 0.025 m beyond the ridge center under its cap in all six tests. Neither the parameters nor the generator were changed.

| Existing regression | Width × depth m | Wall m | Pitch | Seed | Courses | Shingles | Roof / total triangles | Gable / internal gap m | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Long | 5.1 × 7.3 | 2.3 | 40° | 23 | 20 | 1,137 | 13,692 / 14,054 | 0.06680 / 0.02361 | PASS; saved 9A mesh equal |
| Compact | 4.0 × 3.5 | 2.3 | 48° | 11 | 18 | 534 | 6,456 / 6,818 | 0.07511 / 0.02216 | PASS; saved 9B mesh equal |
