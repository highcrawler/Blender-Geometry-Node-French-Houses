# EXPERIMENT 08A – Cottage Prototype 01

Run from the **repository root**, with Blender 5.2.2:

```sh
blender -b -t 2 -P experiments/cottage_generator_08a/test_parameters.py
blender -b -t 2 -P experiments/cottage_generator_08a/build_examples.py
```

Second command regenerates `Cottage_Prototype_01.blend`, `measurements.json` and nine actual Blender Workbench PNG renders in `screenshots/`. It may create a local `.blend1` backup on subsequent runs; delete that backup before committing. The image rendering does not load or modify the IRCSS `.blend` file. Change `variants.json` for alternative examples or import `Cottage, generate` from `cottage.py` within Blender Python. The generated `.blend` contains all three independent collections and five Blender procedural materials per variant. Screenshot camera settings are fixed per view family (three ISO and three front); the side-by-side image has a common camera. View `docs/PHASE8A_*` for limitations and measurements.
