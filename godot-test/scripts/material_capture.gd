extends SceneTree

# Run after --editor --import with a graphical rendering driver (not --headless).
# godot --path godot-test --script res://scripts/material_capture.gd -- --output /absolute/path/tests/materials/godot
func _initialize() -> void:
    _run.call_deferred()

func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2 or args[0] != "--output":
        push_error("Expected --output ABSOLUTE_DIRECTORY")
        quit(2)
        return
    var out_dir: String = args[1]
    var err: Error = DirAccess.make_dir_recursive_absolute(out_dir)
    if err != OK:
        push_error("Cannot create screenshot directory: %s" % out_dir)
        quit(2)
        return
    root.size = Vector2i(960, 720)
    var packed: PackedScene = load("res://scenes/material_comparison.tscn") as PackedScene
    if packed == null:
        push_error("Comparison scene not loaded")
        quit(2)
        return
    var scene: Node3D = packed.instantiate() as Node3D
    root.add_child(scene)
    current_scene = scene
    var original_house: Node3D = scene.get_node("House") as Node3D
    var camera: Camera3D = scene.get_node("ComparisonCamera") as Camera3D
    var viewpoints: Dictionary = {
        "iso": {"eye": Vector3(12, 12, 15), "target": Vector3(0, 3.7, 0), "scale": 15.0},
        "front": {"eye": Vector3(16, 5.2, 0), "target": Vector3(0, 3.7, 0), "scale": 12.0},
        "facade": {"eye": Vector3(11, 4.8, 5), "target": Vector3(0, 4.2, 0.4), "scale": 6.0},
    }
    for variant: String in ["BASELINE", "REDUCED"]:
        var house: Node3D
        if variant == "BASELINE":
            house = original_house
        else:
            scene.remove_child(original_house)
            original_house.queue_free()
            var asset: PackedScene = load("res://assets/HouseOne_Phase2_REDUCED.glb") as PackedScene
            if asset == null:
                push_error("Reduced GLB not loaded")
                quit(2)
                return
            house = asset.instantiate() as Node3D
            house.name = "House"
            scene.add_child(house)
        var meshes: Array[MeshInstance3D] = []
        _collect_meshes(house, meshes)
        var triangles: int = 0
        var surface_count: int = 0
        var material_names: PackedStringArray = PackedStringArray()
        for mesh_instance: MeshInstance3D in meshes:
            var mesh: Mesh = mesh_instance.mesh
            for surface: int in mesh.get_surface_count():
                surface_count += 1
                triangles += mesh.surface_get_array_index_len(surface) / 3
                var material: Material = mesh.surface_get_material(surface)
                material_names.append(material.resource_name if material != null else "<null>")
        print("PHASE2_GODOT_IMPORT variant=%s meshes=%d surfaces=%d triangles=%d materials=%s" % [variant, meshes.size(), surface_count, triangles, material_names])
        for view: String in ["iso", "front", "facade"]:
            var settings: Dictionary = viewpoints[view]
            camera.position = settings["eye"]
            camera.look_at(settings["target"], Vector3.UP)
            camera.size = settings["scale"]
            for frame: int in 6:
                await process_frame
            await RenderingServer.frame_post_draw
            var image: Image = root.get_texture().get_image()
            var path: String = out_dir.path_join(variant.to_lower() + "_" + view + ".png")
            var save_error: Error = image.save_png(path)
            if save_error != OK:
                push_error("Screenshot save failed: %s (%d)" % [path, save_error])
                quit(3)
                return
            print("PHASE2_GODOT_SCREENSHOT %s %dx%d" % [path, image.get_width(), image.get_height()])
    quit(0)

func _collect_meshes(node: Node, result: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        result.append(node as MeshInstance3D)
    for child: Node in node.get_children():
        _collect_meshes(child, result)
