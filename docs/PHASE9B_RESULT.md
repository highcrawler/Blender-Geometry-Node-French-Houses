# Phase 9B — result

**TECHNICAL RESULT: PASS**

**VISUAL RESULT: BOTH PASS** (technical visual assessment; artistic sign-off remains with the project lead)

The exact existing 9A roof functions produced two distinct Cottage proportions without modifications to the generator, addon, materials, moss or archived output. Both parameter sets are supported, with identical CLEAN/AGED geometry per cottage, deterministic seed replay and actual 9A saved-Blender-file Long geometry equality. All 28 required Blender views, three comparison boards, a four-house inspection `.blend`, executable audit and [measurements](../experiments/wooden_roof_system_09b/measurements.json) are in [the 9B experiment](../experiments/wooden_roof_system_09b/). See [geometry audit](PHASE9B_PORTABILITY_AUDIT.md) and [visual comparison](PHASE9B_VISUAL_COMPARISON.md).

| Quantity | Long CLEAN / AGED | Compact CLEAN / AGED |
|---|---:|---:|
| Width × depth | 5.1 × 7.3 m | 4.0 × 3.5 m |
| Pitch | 40° | 48° |
| Courses per slope | 20 | 18 |
| Shingles | 1,137 | 534 |
| Roof triangles | 13,692 | 6,456 |
| Total triangles | 14,054 | 6,818 |
| Unique materials | 8 | 8 |
| Generation CLEAN / AGED, single runs | 48.97 / 47.28 ms | 29.94 / 31.99 ms |

**Answers:** (1) Yes, the same roof works at both tested scales: no new significant uncovered eave, gable or ridge section, and the covering is legible for each. (2) No generator adjustment was made. The 7.5 cm maximum Compact gable-edge residual, a slim dark eave recess and the coarse ridge join are measured/visible limitations, not proven portability regressions requiring changes to the artist-approved Long baseline. (3) It is technically suitable as a *candidate* reusable module for more Cottage proportions, but only these two parameter/seed combinations are validated; do not claim general robustness or an export-ready module yet.

**One next small step:** run the same read-only roof geometry audit on a bounded set of additional *Cottage parameter combinations* to establish the supported dimensional envelope before modularization.
