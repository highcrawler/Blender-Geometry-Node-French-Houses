# Phase 9D — result

**TECHNICAL RESULT: PASS**

The canonical 9A `roof_geometry` now returns the number of **created courses per roof side**. T03 returns 21 instead of 22; T05 returns 18 instead of 19. The other six configurations return their unchanged correct values. [Minimal fix and root cause](PHASE9D_ROWCOUNT_FIX.md) · [full regression and control renders](PHASE9D_REGRESSION.md).

All eight exact Cottage configurations pass the corrected full audit, for both CLEAN and AGED. Old versus new vertex geometry, topology, per-face material indices and shader values match, as do stored Phase-9C Blender meshes and body/roof fingerprints; triangle and shingle counts and moss selections have not changed. Eight genuine Cycles control renders are RGB pixel-identical to their untouched 9C source images. The saved 9A/9B Long/Compact reference meshes also agree. No phase-9A/9B/9C measured outputs or screenshots were overwritten. Blender 5.2.2 LTS; no FPS/export claim.

**Remaining limits:** only eight combinations are audited, not every possible Cottage size/seed. T06's shortest shingle remains 0.10728 m, close to the unchanged >0.10 m test bound; the narrow eave shadow and simplified ridge remain Phase-9A baseline characteristics. Historical 9C FAIL is preserved as pre-fix evidence. No new roof variant, material system, nonrectangular geometry or export integration was introduced.

**Answers:** (1) Yes, T03/T05 metadata counts are corrected to 21/18, observed directly in generated rows on each side. (2) Yes, all sixteen roof meshes are geometrically identical to Phase 9C; independently compared saved `.blend` vertex/face/material inventories confirm this. (3) Yes, all eight configurations × two states pass the complete unchanged geometric limits, with the corrected audit-only expected row range. (4) Yes, as a **candidate rectangular-roof module for a later milestone**, not a guarantee over all parameters or support for L-/U-shaped roofs.

**Exactly one next small step:** freeze the accepted rectangular roof interface and its eight-case regression contract in a short design specification; do not implement a new roof feature in this phase.
