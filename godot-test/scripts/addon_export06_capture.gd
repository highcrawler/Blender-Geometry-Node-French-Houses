extends SceneTree

func _initialize() -> void:
    _run.call_deferred()

func _collect(node: Node, result: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        result.append(node as MeshInstance3D)
    for child: Node in node.get_children():
        _collect(child, result)

func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2 or args[0] != "--output":
        quit(2)
        return
    var out_dir: String = args[1]
    root.size = Vector2i(1280, 900)
    root.msaa_3d = Viewport.MSAA_4X
    var packed: PackedScene = load("res://scenes/addon_export06.tscn") as PackedScene
    if packed == null:
        push_error("Phase6 test scene did not load")
        quit(3)
        return
    var scene: Node3D = packed.instantiate() as Node3D
    root.add_child(scene)
    current_scene = scene
    var camera: Camera3D = scene.get_node("Camera3D") as Camera3D
    camera.look_at(Vector3(6, 4, 0), Vector3.UP)
    var report: Dictionary[String, Dictionary] = {}
    var expected: Dictionary[String, int] = {"House3": 106735, "House5": 378786}
    for label: String in expected:
        var house: Node3D = scene.get_node(label) as Node3D
        var nodes: Array[MeshInstance3D] = []
        _collect(house, nodes)
        var triangles: int = 0
        var surfaces: int = 0
        var materials: Array[Dictionary] = []
        var body: AABB = AABB()
        var found_body: bool = false
        var bounds: AABB = AABB()
        for instance: MeshInstance3D in nodes:
            var mesh: Mesh = instance.mesh
            bounds = instance.get_aabb()
            if not instance.transform.is_equal_approx(Transform3D.IDENTITY):
                push_error("Unexpected world offset inside imported mesh")
                quit(3)
                return
            for index: int in mesh.get_surface_count():
                var count: int = mesh.surface_get_array_index_len(index) / 3
                triangles += count
                surfaces += 1
                var pbr: BaseMaterial3D = mesh.surface_get_material(index) as BaseMaterial3D
                if pbr == null or pbr.albedo_texture != null:
                    push_error("Missing PBR material or unexpected texture dependency")
                    quit(3)
                    return
                materials.append({"name": pbr.resource_name, "triangles": count,
                    "albedo": [pbr.albedo_color.r, pbr.albedo_color.g, pbr.albedo_color.b, pbr.albedo_color.a]})
                if pbr.resource_name == "MBG_PBR_GroundFloorWalls":
                    var arrays: Array = mesh.surface_get_arrays(index)
                    var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
                    body = AABB(vertices[0], Vector3.ZERO)
                    for vertex: Vector3 in vertices:
                        body = body.expand(vertex)
                    found_body = true
        if nodes.size() != 1 or surfaces != 12 or triangles != expected[label] or not found_body:
            push_error("Geometry/material completeness assertion failed: " + label)
            quit(3)
            return
        if absf(body.position.y) > 0.00001 or absf(body.get_center().x) > 0.01 or absf(body.get_center().z) > 0.01:
            push_error("Supporting body is not centered on its floor pivot")
            quit(3)
            return
        var desired_position: Vector3 = Vector3.ZERO if label == "House3" else Vector3(12, 0, -2)
        if not house.position.is_equal_approx(desired_position) or not house.scale.is_equal_approx(Vector3.ONE):
            push_error("Imported root placement or scale mismatch")
            quit(3)
            return
        report[label] = {"triangles": triangles, "surfaces": surfaces, "meshes": nodes.size(),
            "position": [house.position.x, house.position.y, house.position.z],
            "scale": [house.scale.x, house.scale.y, house.scale.z],
            "aabb": str(bounds), "supporting_body_aabb": str(body), "materials": materials,
            "pivot_pass": true, "no_internal_offsets": true}
    # Both independent imported scenes share one visible test scene.
    for frame: int in 15:
        await process_frame
    await RenderingServer.frame_post_draw
    var image: Image = root.get_texture().get_image()
    if image.save_png(out_dir.path_join("godot_two_houses.png")) != OK:
        quit(3)
        return
    # Move only House5, independently of House3, then prove that placement too.
    var other: Node3D = scene.get_node("House5") as Node3D
    other.position = Vector3(14, 0, -4)
    (scene.get_node("Pivot5X") as Node3D).position = Vector3(14, 0.02, -4)
    (scene.get_node("Pivot5Z") as Node3D).position = Vector3(14, 0.02, -4)
    (scene.get_node("House5Label") as Label3D).position = Vector3(14, 0.35, 1)
    (scene.get_node("House5Label") as Label3D).text = "House 5 moved | (14, 0, -4)"
    if not (scene.get_node("House3") as Node3D).position.is_zero_approx():
        push_error("Moving House5 affected House3")
        quit(3)
        return
    for frame: int in 8:
        await process_frame
    await RenderingServer.frame_post_draw
    image = root.get_texture().get_image()
    if image.save_png(out_dir.path_join("godot_house5_moved.png")) != OK:
        quit(3)
        return
    var file: FileAccess = FileAccess.open(out_dir.path_join("godot_measurements.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    print("PHASE6_GODOT_PASS ", JSON.stringify(report))
    quit(0)
