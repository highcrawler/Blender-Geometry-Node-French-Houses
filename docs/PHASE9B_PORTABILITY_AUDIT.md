# Phase 9B — portability / geometry audit

Base `ca28be3`; Blender 5.2.2. Both proposed parameter sets pass `Cottage.validate()` without substitution. The test extracts the *unchanged* Phase-9A `roof_geometry`, `roof_material`, `tri` and `signature` function definitions from 9A `build.py`, with `p` set to each cottage. It does not execute the 9A script's top-level render/build, copy its generator or edit its files. [Script and reproduction](../experiments/wooden_roof_system_09b/README.md) · [full measured data](../experiments/wooden_roof_system_09b/measurements.json).

| Quantity (CLEAN/AGED geometry identical) | Long | Compact |
|---|---:|---:|
| Body width × depth | 5.1 × 7.3 m | 4.0 × 3.5 m |
| Wall height / configured pitch / seed | 2.3 m / 40° / 23 | 2.3 m / 48° / 11 |
| Deck width × depth (including eave) | 5.78 × 7.80 m | 4.68 × 4.00 m |
| Ridge height | 4.43970 m | 4.52123 m |
| Slope length of deck | 3.65628 m | 3.29601 m |
| Courses per slope | 20 | 18 |
| Shingles per course, observed range | 27–30 | 14–16 |
| Shingles total | 1,137 | 534 |
| Roof triangles | 13,692 | 6,456 |
| Total building triangles | 14,054 | 6,818 |
| Unique building materials | 8 | 8 |
| Generation CLEAN (one run, no render) | 48.97 ms | 29.94 ms |
| Generation AGED (one run, no render) | 47.28 ms | 31.99 ms |

The ridge is derived from the nominal pitch measured at the wall line. The deck begins 0.34 m outside the wall and 0.10 m below wall height; therefore its effective face pitch differs slightly from the nominal configured 40°/48° on *both* buildings. This is unchanged Phase-9A behavior, not a compact-specific hardcoded position. Course exposure is 0.185 m, ordinary shingle length ~0.315 m (~41% nominal overlap), widths 0.205–0.335 m. Each final upper course passes the centerline by 0.025 m under the two-plank cap. Shortest final shingle length: Long 0.16628 m, Compact 0.17601 m; neither is a degenerate sliver.

Geometric tests on **each of four generated states**: 8 vertices and 6 quads per shingle; every shingle edge shared by exactly two faces; positive signed volume of each shingle, deck and ridge plank; no zero-area faces or duplicate identical shingles; side-gable boundary residual max 0.06680 m (Long) / 0.07511 m (Compact), both below the explicit 0.09 m limit; internal interval gap max 0.02361 / 0.02216 m (includes small intentional seam/cut variation), below 0.04 m. The deck runs continuously to both eaves and gable edges, and the last course reaches the cap. The intentional course overlap is excluded from duplicate/overlap faults. These checks establish topological closure and coverage bounds, **not** a self-intersection-free union of all intentionally overlapping solids; no FPS or export conclusions are inferred.

Regression: the generated Long CLEAN roof **and** nonroof meshes matched geometry fingerprints of the saved Phase-9A `.blend` collection. Long per-state materials, moss counts (0/36), course, shingle and triangle counts match Phase-9A measurements. Replays with the same input and seed reproduce roof and nonroof hashes for both cottages/states; CLEAN/AGED share the roof and nonroof geometry hashes within each cottage. Compact construction did not alter Long. Independently, unmodified 9A build and board scripts ran in a temporary external directory and reproduced 1,137 shingles, 13,692 roof triangles and all 12 images without writing to 9A outputs.

**Limits:** one seed per size, no stress-test sweep over all supported dimensions; generation times are single noisy local measurements. A narrow dark shadow line between deck edge and shingle tips and a slightly uneven, simple ridge cap are already visible on the unchanged Long baseline. Compact shows no new relevant opening, but a ~7.5 cm maximum local gable-edge residual is measurable and deserves attention in future size sweeps. No generator correction was justified for these two configurations.
