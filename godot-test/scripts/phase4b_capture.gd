extends SceneTree

func _initialize() -> void:
    _run.call_deferred()

func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2 or args[0] != "--output":
        quit(2)
        return
    var out_dir: String = args[1]
    root.size = Vector2i(640, 480)
    var scene: Node3D = (load("res://scenes/material_comparison.tscn") as PackedScene).instantiate() as Node3D
    root.add_child(scene)
    current_scene = scene
    (scene.get_node("NeutralSun") as DirectionalLight3D).light_energy = 0.65
    (scene.get_node("NeutralEnvironment") as WorldEnvironment).environment.ambient_light_energy = 0.35
    var old: Node3D = scene.get_node("House") as Node3D
    scene.remove_child(old)
    old.queue_free()
    var camera: Camera3D = scene.get_node("ComparisonCamera") as Camera3D
    var viewpoints: Dictionary[String, Dictionary] = {
        "iso": {"eye": Vector3(12, 12, 15), "target": Vector3(0, 3.7, 0), "scale": 15.0},
        "front": {"eye": Vector3(16, 5.2, 0), "target": Vector3(0, 3.7, 0), "scale": 12.0},
        "side": {"eye": Vector3(0, 5.2, 16), "target": Vector3(0, 3.7, 0), "scale": 12.0},
        "facade": {"eye": Vector3(11, 4.8, 5), "target": Vector3(0, 4.2, 0.4), "scale": 6.0},
    }
    var results: Dictionary[String, Dictionary] = {}
    for label: String in ["phase4", "phase4b"]:
        var file: String = "HouseOne_Phase4.glb" if label == "phase4" else "HouseOne_Phase4B.glb"
        var packed: PackedScene = load("res://assets/" + file) as PackedScene
        if packed == null:
            push_error("GLB not imported: " + file)
            quit(3)
            return
        var house: Node3D = packed.instantiate() as Node3D
        scene.add_child(house)
        var meshes: Array[MeshInstance3D] = []
        _collect(house, meshes)
        var triangles: int = 0
        var surfaces: int = 0
        var texture_count: int = 0
        var details: Array[Dictionary] = []
        var bounds: AABB = meshes[0].global_transform * meshes[0].get_aabb()
        for instance: MeshInstance3D in meshes:
            bounds = bounds.merge(instance.global_transform * instance.get_aabb())
            var mesh: Mesh = instance.mesh
            for index: int in mesh.get_surface_count():
                surfaces += 1
                var count: int = mesh.surface_get_array_index_len(index) / 3
                triangles += count
                var pbr: BaseMaterial3D = mesh.surface_get_material(index) as BaseMaterial3D
                var detail: Dictionary = {"material": pbr.resource_name, "triangles": count}
                if pbr.albedo_texture:
                    texture_count += 1
                    detail["texture_size"] = str(pbr.albedo_texture.get_size())
                    detail["uv1_scale"] = str(pbr.uv1_scale)
                    if pbr.albedo_texture.get_size() != Vector2(1024, 1024):
                        push_error("Texture dimension mismatch")
                        quit(3)
                        return
                details.append(detail)
        var expected: int = 50944 if label == "phase4" else 154602
        var expected_surfaces: int = 5 if label == "phase4" else 12
        if triangles != expected or surfaces != expected_surfaces or meshes.size() != 1 or texture_count != 1:
            push_error("Geometry/material/texture assertion failed")
            quit(3)
            return
        results[label] = {"meshes": meshes.size(), "surfaces": surfaces, "triangles": triangles, "texture_count": texture_count, "aabb": str(bounds), "materials": details}
        print("PHASE4B_GODOT_IMPORT ", label, " ", JSON.stringify(results[label]))
        for view: String in viewpoints:
            var settings: Dictionary = viewpoints[view]
            camera.position = settings["eye"]
            camera.look_at(settings["target"], Vector3.UP)
            camera.size = settings["scale"] * 480.0 / 640.0
            for frame: int in 8:
                await process_frame
            await RenderingServer.frame_post_draw
            var path: String = out_dir.path_join("godot_" + label + "_" + view + ".png")
            var image: Image = root.get_texture().get_image()
            if image.save_png(path) != OK:
                quit(3)
                return
            print("PHASE4B_GODOT_SCREENSHOT ", path)
        scene.remove_child(house)
        house.queue_free()
        await process_frame
    var report: FileAccess = FileAccess.open(out_dir.path_join("godot_measurements.json"), FileAccess.WRITE)
    report.store_string(JSON.stringify(results, "  "))
    quit(0)

func _collect(node: Node, result: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        result.append(node as MeshInstance3D)
    for child: Node in node.get_children():
        _collect(child, result)
