# Phase 9A — Result

**TECHNICAL RESULT: PASS**

**VISUAL RESULT: CLEAN+AGED** (with visible limitations)

| Measurement | CLEAN | AGED |
|---|---:|---:|
| Roof triangles (mesh polygons triangulated) | 13,692 | 13,692 |
| Total building triangles | 14,054 | 14,054 |
| Unique building materials | 8 | 8 |
| Generation, single run, excluding render | 51.89 ms | 52.48 ms |
| Shingles / roof objects | 1,137 / 5 | 1,137 / 5 |
| Moss-tinted shingles | 0 | 36 |
| 300-pixel visibility | Courses and staggered seams legible | Courses and staggered seams legible; moss subtle |

Measurements from [machine-readable data](../experiments/wooden_roof_system_09a/measurements.json), on the local run, not benchmark averages. Both state roof geometry signatures and nonroof geometry signatures matched in the Blender build assertions. The test images are genuine Cycles renders; [comparison and all views](PHASE9A_VISUAL_COMPARISON.md). No FPS or LOD measurement was attempted.

**Strengths:** Real overlapping geometry rather than a shader illusion; one mesh for all shingles; deterministic seed; constrained width variation and restrained aging; same parametric roof construction derives its scale from cottage dimensions, making adaptation plausible. CLEAN is warmer and matches the existing timber; AGED retains the same covering structure. Compared with earlier straw iterations, the roof reads more decisively as a constructed, repeating material at game distance; this is a visual judgment, not an identical-camera quantitative benchmark against all old experiments.

**Weaknesses / observed issues:** Regular horizontal lines and planar, grain-free shingle surfaces can evoke manufactured tiles in close-up; strong area lighting lightens the weathered palette to gray. Moss is mostly imperceptible at ~300 px; it does *not* occlude the shingle pattern. The simple two-board ridge lacks finely joined ends. The eave/deck thickness is simplified; independent watertightness and multi-size stress tests have not been run. No UV maps or textures are used, so mapping defects were not observed but textured portability is untested. ~14k triangles per building may need later assessment for mass use; no mass export, LOD or FPS claims are made. Generation durations are single samples.

Answers: (1) Yes, cleaner roof-material readability than the earlier straw trials at the observed game-distance render. (2) Yes, AGED is usable as a state; moss is restrained enough to preserve covering but its age cue is weak at distance. (3) The dimension-based generator is a reasonable starting point for other gabled houses, *not yet proven robust* outside this Long Cottage.

**Exactly one next small step:** evaluate the unchanged roof generator on one additional *parameter set of the same cottage* to check course termination and ridge joins, without introducing another house type.
