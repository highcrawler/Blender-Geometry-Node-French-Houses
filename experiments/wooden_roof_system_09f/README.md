# Phase 9F reproduction — Blender 5.2.2 LTS

From repository root, with Blender's bundled Python and Pillow on the host:

```sh
blender -b -t 4 -P experiments/wooden_roof_system_09f/verify.py
python experiments/wooden_roof_system_09f/compare_images.py
blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend \
  -P experiments/wooden_roof_system_09f/reopen.py
```

Inspect each Blender log for `Traceback`: Blender may exit with status 0 even after a Python assertion. `verify.py` regenerates eight archived 9B/9C Cottage parameter sets × CLEAN/AGED using the new roof module and thin adapter, runs the existing 9B geometry audit with its 9D test-side observed-row correction, matches the complete 9D geometry fingerprints and archived 9C `.blend` material/vertex inventories, tests seed/order/ownership/error isolation and produces eight true Cycles controls. It then saves a three-house `.blend` and overview PNG after temporary B-only mutation/restore. `compare_images.py` compares 9F against the **unmodified** 9D PNGs in RGB, writing `image_comparison.json` and two contact sheets. `reopen.py` independently reloads the saved scene and writes `reopen_result.json`. Tests never execute 9A/9B/9C/9D top-level scripts or overwrite their reference files.

Import path: the repository root is placed on `sys.path`, so `from roof.wooden_rect import RoofSpec, RoofResult, build_rectangular_roof` works inside Blender. The test-only Cottage adapter adds `experiments/cottage_generator_08a` to `sys.path` for the historical `cottage.py`; **`roof` imports neither Cottage nor IRCSS nor the Blender add-on**. This is not an add-on registration or an exporter.
