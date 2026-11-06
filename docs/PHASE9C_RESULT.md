# Phase 9C — result

**TECHNICAL RESULT: PARTIAL**

**VISUAL RESULT: ALL PASS** (technical visual inspection only; project-lead artistic approval outstanding)

Exactly six additional valid Cottage inputs were tested alongside Long/Compact. Four pass all existing geometric/count checks; **T03 and T05 FAIL** because the 9A function reports one more shingle row per side than it actually generates near the ridge. All six satisfy the unchanged 9B gable/internal gap limits and the checked mesh-topology/coverage bounds, and show no new relevant visible hole. This does **not** justify calling the entire tested envelope technically PASS while count reporting is wrong. The generator was left unchanged. [Matrix with measurements](PHASE9C_PARAMETER_MATRIX.md) · [geometry and visual evidence](PHASE9C_GEOMETRY_VALIDATION.md) · [future L-/U-roof architecture note](PHASE9C_FUTURE_ROOF_ARCHITECTURE.md) · [reproduction](../experiments/wooden_roof_system_09c/README.md).

Validated input extremes in this **fixed matrix**, not a continuous guarantee: widths 3.0–8.0 m, depths 2.8–9.0 m, wall heights 2.0–3.0 m, nominal pitches 35–60°, six different new seeds. Long and Compact reference meshes match the archived `.blend` files and 9B measurement counts. CLEAN/AGED geometry equality and same-seed replay hold in all eight cases. No previous experiment, Blender addon or IRCSS source file was modified.

**Answers:** (1) All six proposed dimensions and pitches produced geometrically covered roofs; four configurations also pass the complete count/mesh audit. (2) Yes: T03 (5.2 × 2.8 m, 44°) and T05 (5.0 × 5.0 m, 35°) expose the reported-versus-actual last-course discrepancy; T06's 0.10728 m shortest shingle approaches the existing 0.10 m floor. (3) The roof may be *prepared* as a candidate rectangular module only after this measured metadata mismatch is resolved and regressions are run; it is not a proven all-parameter-space module. (4) L-shaped roofs would additionally need plane intersection/valley lines, trimmed rows, transition flashing, and joined ridge/eave topology; no such system exists yet.

**Exactly one next small step:** correct the last-course count metadata in the existing roof function (without changing geometry), then repeat this eight-configuration audit and saved-reference regression.
