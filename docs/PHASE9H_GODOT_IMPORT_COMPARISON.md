# Phase 9H – measured Godot import comparison

All numbers below were independently measured from **Godot imported `Mesh.surface_get_arrays()` index buffers** in [`audit.gd`](../experiments/native_export_godot_09h/godot_test/audit.gd), not copied into the Godot report from Blender. [Full per-node, per-surface material/triangle, imported bounds and root transform report](../experiments/native_export_godot_09h/godot_audit.json); [asserted concise comparison](../experiments/native_export_godot_09h/evaluation_results.json). Both routes produce identical Godot audit data for each corresponding single-house fixture. The imported **37 per-object triangle-count multiset** and the exact **triangle count per used material** were independently compared against 9G's saved per-object/per-slot source report for A, B and C; all six imports match (the unreferenced CLEAN slot contributes zero).

| Asset | Blender source triangles | GLB Godot meshes / surfaces / triangles | `.blend` Godot meshes / surfaces / triangles | Godot used materials | Ground min Y |
|---|---:|---:|---:|---:|---:|
| Long CLEAN A | 14,054 | 37 / 39 / **14,054** | 37 / 39 / **14,054** | 7 | 0 |
| Compact AGED B | 6,818 | 37 / 40 / **6,818** | 37 / 40 / **6,818** | 8 | 0 |
| Long AGED C (seed 29) | 14,066 | 37 / 40 / **14,066** | 37 / 40 / **14,066** | 8 | 0 |

No imported surface lacks a material. The current native exporter happens to retain 37 mesh nodes; **this is a measured observation, not an exporter contract**. Heights: A/C 4.528 m, B 4.612 m; A/C local X range ±2.89 m, local Z ±3.935 m in Godot; B ±2.34 m and ±2.035 m. Blender +Z maps to Godot +Y; Blender +Y maps to Godot −Z. Imported Building_Root of normalized single assets is at the origin, unit scale, zero rotation. `active_B_three_houses.blend` keeps world root `(35,0,-12)`; `active_C_three_houses.blend` keeps `(-15,0,-8)` and Godot **Y** yaw 0.45 radians. This is correct axis conversion but **not** a locally positioned single-house asset: the one-house `.blend` copy/root normalization is required for B/C. `active_collection_only=true` includes all five roof meshes and excludes foreign houses; default false imported 112 meshes/34,950 triangles (3 houses plus unrelated Cube), cameras and lights.

**Critical material limitation, equally present in both routes:** All four Cottage body materials use Blender `Noise Texture → ColorRamp → Principled Base Color` and have nonwhite original `diffuse_color` (e.g. clay `(0.47,0.38,0.28)`, oak `(0.19,0.125,0.077)`). Godot receives four distinct materials with all-white `albedo=(1,1,1,1)` and original roughness 1: **their procedural color information is lost**, not merely a renderer difference. The body appears white in all real Godot screenshots. No source shader or material was repaired in this experiment. Roof materials use direct Principled constants: all used shingle tones survive glTF→Godot, roughness **0.92**, metallic **0**, CLEAN warm brown, AGED desaturated with green moss. A CLEAN roof fourth material slot has zero source faces and is omitted on import, hence 7 **used** imported materials versus 8 mesh-slot references in Blender; no triangle is lost. The B moss material accounts for **252** imported triangles, C for **396**. The imported roof albedo is a color-space-converted display value (e.g. source linear CLEAN tone 0.29 appears as Godot albedo ≈0.575), not evidence of altered assigned faces. Transparency was not used on these source materials; unsupported alpha workflows **not tested**.

The actual Godot OpenGL-compatibility images for A and B are **byte-identical** between the two routes under the same capture script; this confirms equal visible outcomes here, including the common white-body defect. [A GLB](../experiments/native_export_godot_09h/screenshots/long_clean_glb.png) · [A `.blend`](../experiments/native_export_godot_09h/screenshots/long_clean_blend.png) · [B GLB](../experiments/native_export_godot_09h/screenshots/compact_aged_glb.png) · [B `.blend`](../experiments/native_export_godot_09h/screenshots/compact_aged_blend.png) · [comparison board](../experiments/native_export_godot_09h/screenshots/comparison_board.png) · [two-house Godot scene](../experiments/native_export_godot_09h/screenshots/two_cottages.png). No visual normal inversion or missing roof piece was seen under this camera; this does not prove every viewing angle. Independently, an unchanged `single_A.blend` was resaved/reimported and a GLB timestamp-triggered reimport was performed; complete Godot audit JSON remained identical in each case.

## Decision matrix

| Criterion | native GLB | direct `.blend` |
|---|---|---|
| Successful Godot import | PASS | PASS (configured Blender path; RPC fallback) |
| Full mesh geometry and roof | PASS | PASS with active collection or one-house copy |
| Exact imported triangle totals | PASS | PASS |
| Material face assignments / colors | PARTIAL: roof yes, procedural body white; unused slot dropped | PARTIAL: same defect |
| CLEAN look | PARTIAL: brown roof, white body | PARTIAL: same |
| AGED look and moss | PARTIAL: aged/moss roof yes, white body | PARTIAL: same |
| Ground pivot | PASS after disposable B/C root normalization | PASS with one-house normalized copy; active B/C retain world offset |
| Size / axis / orientation | PASS | PASS; active C yaw maps to Godot Y |
| Foreign houses excluded | PASS selected root+meshes | PASS only if `active_collection_only=true` or one-house file; default FAIL |
| Unchanged reimport | PASS | PASS |
| Extra preparation | selection + root normalization for B/C; body shader mapping unresolved | Blender path + active collection or single copy, normalization for B/C; shader mapping unresolved |
| File sizes | A/B GLB 782,836 / 392,264 bytes | A/B single `.blend` ≈323 / 226 KiB; 3-house active copy ≈503 KiB |
| Handling many houses | PASS via owner selection; one GLB per asset | PARTIAL: active collection is a saved-file state; one file/copy per asset for independent import |
| Automation suitability | PARTIAL pending body material preparation | PARTIAL: background Blender dependency, same material gap |

`NOT TESTED`: Forward+ renderer, alpha/transparency workflows, exported animations, arbitrary scales or new building types. No claim of full visual material fidelity.
