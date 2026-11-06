# Phase 9H reproduction: Blender 5.2.2 LTS → Godot 4.7

All commands from repository root. Requires locally installed `blender`, `godot`, a working display/OpenGL3 for screenshots, and Python Pillow for the board. No Pilgrimm checkout, add-on changes or new program installation. Input `experiments/wooden_roof_system_09f/three_owned_cottages.blend` is never saved. The committed Godot project/assets/screenshots allow inspection even without regeneration. The Godot import cache `.godot/` is regenerated locally and intentionally not committed.

```sh
EXP=experiments/native_export_godot_09h
blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$EXP/prepare.py"
for H_TARGET in B C; do
  export H_TARGET
  blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$EXP/single.py"
  blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$EXP/active.py"
done
cd "$EXP/godot_test"
# Godot 4.7 EditorSettings key is blender_path; use your own executable if different.
H_BLENDER=/snap/bin/blender godot --headless --editor --path . --script res://set_blender.gd
# Source-tracked .blend.import settings for active A/B/C specify active_collection_only=true.
godot --headless --editor --path . --import
H_REPORT="$PWD/../godot_audit.json" godot --headless --path . --script res://audit.gd
# Four Godot OpenGL captures under identical light/camera:
for entry in 'cottage_A.glb long_clean_glb' 'single_A.blend long_clean_blend' \
             'cottage_B.glb compact_aged_glb' 'single_B.blend compact_aged_blend'; do
  set -- $entry
  H_ASSET="$1" H_SHOT="$PWD/../screenshots/$2.png" godot --path . --rendering-driver opengl3 --script res://capture.gd
done
H_DUO=1 H_ASSET=cottage_A.glb H_SHOT="$PWD/../screenshots/two_cottages.png" godot --path . --rendering-driver opengl3 --script res://capture.gd
cd ../../..
python experiments/native_export_godot_09h/make_board.py
python experiments/native_export_godot_09h/evaluate.py
```

`capture.gd` also saves a Godot [`test_scene.tscn`](godot_test/test_scene.tscn) with neutral floor, light, camera and two imported GLBs when `H_DUO=1`. Open the project independently with `godot --editor --path experiments/native_export_godot_09h/godot_test`. One-house normalized A/B/C `.blend` copies and active-owner three-house copies are small, deliberately disposable experiment artifacts committed for reproducibility. A system without Blender installed can open **GLB** assets, but cannot reimport `.blend` after clearing `.godot/`.

**Recorded reimport check:** save unchanged disposable `single_A.blend` again with Blender, run `godot --headless --editor --path . --import`, rerun `audit.gd`: complete Godot audit JSON was unchanged. Touch `assets/cottage_A.glb`, reimport and repeat: JSON unchanged. The saved source reference and all 9F/9G fingerprints remain untouched. If Godot displays an RPC connection error then reports a fallback to direct Blender imports, test whether the actual resources import and audit succeeds; this environment did. If `blender_path` is invalid, direct `.blend` import **fails**, do not claim success. `set_blender.gd` writes your **user EditorSettings**; it is optional when Blender is already correctly configured. Blender background add-on startup warnings were environmental and not part of the imported asset.
