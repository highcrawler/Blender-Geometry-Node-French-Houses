# Godot 4.7 background import evidence

Environment: `godot --headless --editor --path godot_test --import` (from project directory, `--path .`). Blender configured via `filesystem/import/blender/blender_path=/snap/bin/blender`; no binary installed or upgraded.

1. **Initial configuration failure** (before test scene creation): `ERROR: Blender path is invalid or not set, check your Editor Settings. Cannot configure blender path in headless mode.` The same bootstrap attempt also had `Cannot open file 'res://test_scene.tscn'` because the test scene had not been created yet. This was corrected before the measured imports; these are not asset defects.
2. **After correcting executable path:** `ERROR: Unexpected status during RPC connection: 4`, then `Failed to connect to Blender via RPC, switching to direct imports of .blend files.` The importer produced `.scn` resources; the runtime Godot audit loaded their real meshes and surfaces. RPC success is **not** claimed.
3. **Subsequent imports** after configuring `active_collection_only=true` for A/B/C, plus unchanged `single_A.blend` resave/reimport and timestamp-triggered GLB reimport, all had **zero `ERROR:` lines**. The full pre/post Godot audit dictionaries matched after each reimport. A Godot runtime smoke of `test_scene.tscn` had zero script/import errors.
4. Both four individual screenshots and the two-building view were captured from Godot's actual viewport using `--rendering-driver opengl3` and `Image.save_png()`. The 2×2 comparison board only resizes/arranges these real images; it does not synthesize geometry.

Machine-checkable counts and material data: [`godot_audit.json`](godot_audit.json), [`evaluation_results.json`](evaluation_results.json). Import cache under `godot_test/.godot/` is disposable and ignored.
