# Experiment 08C – Roof construction spike

Blender 5.2.2, from the repository root:

```sh
blender -b -t 4 -P experiments/cottage_generator_08c/compare.py
python3 experiments/cottage_generator_08c/make_board.py  # Pillow, only for arranging existing PNGs
```

Single Long Cottage configuration in `long.json`: 5.1 × 7.3 m, wall 2.3 m, pitch 40°, seed 23. The test calls the unchanged 8B cottage generator three times; `roofs.py` replaces **only** roof-tagged objects for A or B. This does **not** change the generator's default. It compares baseline mesh coordinates to the saved 8B `.blend` (loaded read-only), verifies deterministic replays, shell topology, unchanged non-roof coordinates and building height, then renders all views in Blender. Failures print a Python traceback; Blender may still return exit code 0, so require the final `08C_PASS` line.

Outputs: `screenshots/` contains **15 individual genuine Blender frames** (ISO/front/side/detail in Cycles 16 spp, monochrome roof-only silhouette in Workbench) plus `all_three.png` (a lossless side-by-side layout of the identical-lighting ISO Blender frames; the layout itself is not a Blender render); `Roof_Construction_Spike.blend` has the three collections displayed side by side; `baseline_meshes.blend`, `variant_a_meshes.blend`, `variant_b_meshes.blend` are separately saved collection resources; `measurements.json` records measured creation times, topology and byte counts. The 8A/8B artifacts and source scripts are untouched. The raw mesh payload byte count is only an explicit XYZ-float32 + triangulated-index-uint32 **lower bound**, not full Blender RAM. Saved collection file sizes are actual disk bytes, not memory usage. Render times/FPS are not benchmarked.
