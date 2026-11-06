# Phase 9G – ground pivot and transforms

The Phase-9E/9F Cottage contract is supporting-footprint XY center, ground Z=0 at the building root's local origin. This is an **explicit validated Cottage convention**, not a geometry-bounds estimate. The collector uses `pivot_local=(0,0,0)`, `pivot_world=root.matrix_world @ pivot_local` and computes `export_local_matrix=T(-pivot_local) @ root.matrix_world.inverted() @ mesh.matrix_world` **without applying it**. Copies of each mesh's local and world matrices and the export-local transform are available per record in [`collection_results.json`](../experiments/cottage_geometry_collector_09g/collection_results.json).

| House | Root location | Z yaw (rad) | Local ground pivot | World ground pivot |
|---|---|---:|---|---|
| A | (0, 0, 0) | 0 | (0, 0, 0) | (0, 0, 0) |
| B | (35, 12, 0) | 0 | (0, 0, 0) | (35, 12, 0) |
| C | (-15, 8, 0) | ≈ 0.45 | (0, 0, 0) | (-15, 8, 0) |

All roots are unparented with unit scale, no X/Y tilt, finite translations/yaw, invertible world matrices. Their parented mesh world matrices are recorded; world-to-export-local cancels C's yaw and B/C translations. The test checks the homogeneous export transform on each mesh, correct world pivot, and reopens the saved Phase-9F reference to check persisted transforms and local hashes. No mesh was moved or duplicated.

A future barn/workshop with another pivot convention or an L-shaped supporting footprint needs its own explicitly supplied and validated footprint/pivot contract; this release does not derive one from an arbitrary bounding box. GLB coordinate convention, export realization, Godot import and pivot round-trip remain untested until a later export milestone.
