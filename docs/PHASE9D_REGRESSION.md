# Phase 9D — eight-configuration regression

[Full machine-readable data and 64-character SHA-256 fingerprints](../experiments/wooden_roof_system_09d/measurements.json) · [reproduction](../experiments/wooden_roof_system_09d/README.md). Eight **unchanged** 9B/9C input configurations, each CLEAN and AGED. All 16 states **PASS**.

| Case (width × depth; wall; pitch; seed) | Courses before → after = observed / side | Shingles | Roof / total triangles | Roof fingerprint prefix (CLEAN = AGED) | Result |
|---|---:|---:|---:|---|---|
| Long (5.1 × 7.3; 2.3; 40°; 23) | 20 → 20 | 1,137 | 13,692 / 14,054 | `d9808450846c` | PASS |
| Compact (4.0 × 3.5; 2.3; 48°; 11) | 18 → 18 | 534 | 6,456 / 6,818 | `c45e8a6a73ff` | PASS |
| T01 (3.0 × 4.3; 2.0; 42°; 31) | 13 → 13 | 464 | 5,616 / 5,978 | `70bb98906f35` | PASS |
| T02 (8.0 × 5.2; 3.0; 42°; 37) | 31 → 31 | 1,302 | 15,672 / 16,034 | `edb9b970610d` | PASS |
| T03 (5.2 × 2.8; 2.4; 44°; 41) | **22 → 21** | 524 | 6,336 / 6,698 | `fbc620c23515` | PASS |
| T04 (5.0 × 9.0; 2.5; 44°; 43) | 21 → 21 | 1,446 | 17,400 / 17,762 | `f2f625151f01` | PASS |
| T05 (5.0 × 5.0; 2.2; 35°; 47) | **19 → 18** | 737 | 8,892 / 9,254 | `46a49d27cd19` | PASS |
| T06 (5.0 × 5.0; 2.8; 60°; 53) | 29 → 29 | 1,179 | 14,196 / 14,558 | `78a0b6d0771c` | PASS |

Verification **for every state**, beyond matching triangle totals: a canonicalized mesh SHA-256 of transformed vertex coordinates and polygon indices agrees between the old and new generators and with the saved 9C measurement fingerprint. An independent per-object inventory of the original/pre-fix and corrected runs matches the **saved 9C `.blend`**: exact mesh-local float32 vertex positions, polygon indices/winding, per-face material-slot indices, shader properties/node links, and flat object hierarchy. Body and roof geometry fingerprints are separately equal. Long and Compact additionally match the saved 9A/9B Blender reference collections. Each corrected state was reproduced with identical seed, metadata and mesh hashes. CLEAN and AGED are mesh-identical per building, with unchanged moss counts and eight materials. Phase-9B checks of closed shingle/deck/ridge solids, positive volumes, nonzero face area, no duplicate shingles, slope coverage, last course reaching the ridge, gable/internal gaps and shingle length all pass with **unchanged** limits (<0.09 m, <0.04 m, >0.10 m). T06 remains 0.10728 m minimum, identical to 9C. This is a finite matrix, not a full parameter-space proof.

## Control renders

Four cases × CLEAN/AGED were rendered with the **exact final Phase-9C iso camera, lighting, samples, resolution and denoising**: [Long CLEAN](../experiments/wooden_roof_system_09d/screenshots/long_clean_iso.png), [Compact CLEAN](../experiments/wooden_roof_system_09d/screenshots/compact_clean_iso.png), [T03 CLEAN](../experiments/wooden_roof_system_09d/screenshots/T03_short_clean_iso.png), [T05 CLEAN](../experiments/wooden_roof_system_09d/screenshots/T05_shallow_clean_iso.png), plus their `aged` counterparts. [CLEAN comparison board](../experiments/wooden_roof_system_09d/comparison_clean.jpg) · [AGED comparison board](../experiments/wooden_roof_system_09d/comparison_aged.jpg). The archived 9C PNGs were **not** overwritten. Pillow RGB pixel comparison of all eight image pairs found **exact equality (0 mean absolute error, 0 maximum channel difference)**: [image_comparison.json](../experiments/wooden_roof_system_09d/image_comparison.json). In this environment no render nondeterminism was observed; pixel equality supplements but does not replace independent geometry/material tests.
