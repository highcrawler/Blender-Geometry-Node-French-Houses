extends SceneTree

# godot --path godot-test --script res://scripts/phase4_capture.gd -- --output ABSOLUTE_DIRECTORY
func _initialize() -> void:
    _run.call_deferred()

func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2 or args[0] != "--output":
        push_error("Expected --output ABSOLUTE_DIRECTORY")
        quit(2)
        return
    var out_dir: String = args[1]
    if DirAccess.make_dir_recursive_absolute(out_dir) != OK:
        push_error("Cannot create screenshot directory")
        quit(2)
        return
    root.size = Vector2i(960, 720)
    var scene: Node3D = (load("res://scenes/material_comparison.tscn") as PackedScene).instantiate() as Node3D
    root.add_child(scene)
    current_scene = scene
    # Reduce the Phase-2 comparison rig's high fill/sun energy to avoid clipping
    # the now-present albedo colors; keep camera/geometry/background identical.
    var sun: DirectionalLight3D = scene.get_node("NeutralSun") as DirectionalLight3D
    sun.light_energy = 0.65
    var environment: WorldEnvironment = scene.get_node("NeutralEnvironment") as WorldEnvironment
    environment.environment.ambient_light_energy = 0.35
    var old_house: Node3D = scene.get_node("House") as Node3D
    scene.remove_child(old_house)
    old_house.queue_free()
    var asset: PackedScene = load("res://assets/HouseOne_Phase4.glb") as PackedScene
    if asset == null:
        push_error("Phase4 GLB not imported")
        quit(2)
        return
    var house: Node3D = asset.instantiate() as Node3D
    scene.add_child(house)
    var meshes: Array[MeshInstance3D] = []
    _collect_meshes(house, meshes)
    var triangles: int = 0
    var surfaces: int = 0
    for instance: MeshInstance3D in meshes:
        var mesh: Mesh = instance.mesh
        for index: int in mesh.get_surface_count():
            surfaces += 1
            triangles += mesh.surface_get_array_index_len(index) / 3
            var material: Material = mesh.surface_get_material(index)
            if material is BaseMaterial3D:
                var pbr: BaseMaterial3D = material as BaseMaterial3D
                if pbr.albedo_texture:
                    print("PHASE4_GODOT_TEXTURE %s size=%s" % [material.resource_name, pbr.albedo_texture.get_size()])
                print("PHASE4_GODOT_MATERIAL %s color=%s roughness=%s metallic=%s" % [material.resource_name, pbr.albedo_color, pbr.roughness, pbr.metallic])
    print("PHASE4_GODOT_IMPORT meshes=%d surfaces=%d triangles=%d" % [meshes.size(), surfaces, triangles])
    if meshes.size() != 1 or surfaces != 5 or triangles != 50944:
        push_error("Imported geometry differs from HouseOne baseline")
        quit(3)
        return
    var camera: Camera3D = scene.get_node("ComparisonCamera") as Camera3D
    var viewpoints: Dictionary = {
        "iso": {"eye": Vector3(12, 12, 15), "target": Vector3(0, 3.7, 0), "scale": 15.0},
        "front": {"eye": Vector3(16, 5.2, 0), "target": Vector3(0, 3.7, 0), "scale": 12.0},
        "facade": {"eye": Vector3(11, 4.8, 5), "target": Vector3(0, 4.2, 0.4), "scale": 6.0},
    }
    for view: String in ["iso", "front", "facade"]:
        var settings: Dictionary = viewpoints[view]
        camera.position = settings["eye"]
        camera.look_at(settings["target"], Vector3.UP)
        camera.size = settings["scale"] * 720.0 / 960.0 # Blender ortho_scale is horizontal at this aspect
        for frame: int in 6:
            await process_frame
        await RenderingServer.frame_post_draw
        var path: String = out_dir.path_join("godot_pbr_" + view + ".png")
        var image: Image = root.get_texture().get_image()
        var err: Error = image.save_png(path)
        if err != OK:
            push_error("Screenshot failed: %s (%d)" % [path, err])
            quit(3)
            return
        print("PHASE4_GODOT_SCREENSHOT %s %dx%d" % [path, image.get_width(), image.get_height()])
    quit(0)

func _collect_meshes(node: Node, result: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        result.append(node as MeshInstance3D)
    for child: Node in node.get_children():
        _collect_meshes(child, result)
