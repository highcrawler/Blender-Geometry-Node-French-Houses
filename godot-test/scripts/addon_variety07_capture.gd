extends SceneTree

func _initialize() -> void:
    _run.call_deferred()

func _collect(node: Node, meshes: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        meshes.append(node as MeshInstance3D)
    for child: Node in node.get_children():
        _collect(child, meshes)

func _picture(path: String) -> Error:
    for frame: int in 12:
        await process_frame
    await RenderingServer.frame_post_draw
    return root.get_texture().get_image().save_png(path)

func _run() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
    if args.size() != 2 or args[0] != "--output":
        quit(2)
        return
    var out_dir: String = args[1]
    var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(out_dir.path_join("integration.json"))) as Dictionary
    var specs: Dictionary = source["presets"]
    root.size = Vector2i(1440, 960)
    root.msaa_3d = Viewport.MSAA_4X
    var packed: PackedScene = load("res://scenes/addon_variety07.tscn") as PackedScene
    if packed == null:
        push_error("Variety test scene did not load")
        quit(3)
        return
    var scene: Node3D = packed.instantiate() as Node3D
    root.add_child(scene)
    current_scene = scene
    var camera: Camera3D = scene.get_node("Camera3D") as Camera3D
    camera.look_at(Vector3(0, 4, 12), Vector3.UP)
    var report: Dictionary[String, Dictionary] = {}
    var placements: Dictionary[String, Vector3] = {"Compact": Vector3.ZERO, "Narrow": Vector3(0, 0, 11), "Wide": Vector3(0, 0, 24)}
    for label: String in placements:
        var spec: Dictionary = specs[label.to_upper()]
        var house: Node3D = scene.get_node(NodePath(label)) as Node3D
        var meshes: Array[MeshInstance3D] = []
        _collect(house, meshes)
        var triangles: int = 0
        var surfaces: int = 0
        var body: AABB = AABB()
        var found_body: bool = false
        var foundation: AABB = AABB()
        var found_foundation: bool = false
        var bounds: AABB = AABB()
        var material_details: Array[Dictionary] = []
        if not house.position.is_equal_approx(placements[label]) or not house.scale.is_equal_approx(Vector3.ONE):
            push_error("Root placement/scale mismatch: " + label)
            quit(3)
            return
        for node: MeshInstance3D in meshes:
            if not node.transform.is_equal_approx(Transform3D.IDENTITY):
                push_error("Unexpected internal world offset: " + label)
                quit(3)
                return
            var mesh: Mesh = node.mesh
            bounds = node.get_aabb()
            for index: int in mesh.get_surface_count():
                var count: int = mesh.surface_get_array_index_len(index) / 3
                triangles += count
                surfaces += 1
                var mat: BaseMaterial3D = mesh.surface_get_material(index) as BaseMaterial3D
                if mat == null or mat.albedo_texture != null:
                    push_error("Missing PBR material/unexpected texture dependency")
                    quit(3)
                    return
                material_details.append({"name": mat.resource_name, "triangles": count, "albedo": str(mat.albedo_color)})
                if mat.resource_name == "MBG_PBR_GroundFloorWalls":
                    var arrays: Array = mesh.surface_get_arrays(index)
                    var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
                    body = AABB(vertices[0], Vector3.ZERO)
                    for vertex: Vector3 in vertices:
                        body = body.expand(vertex)
                        if absf(vertex.y) < .0001:
                            foundation = foundation.expand(vertex) if found_foundation else AABB(vertex, Vector3.ZERO)
                            found_foundation = true
                    found_body = true
        var expected_export: Dictionary = spec["export"]
        if meshes.size() != 1 or triangles != int(expected_export["triangles"]) or surfaces != int(spec["materials"]) or not found_body:
            push_error("Geometry completeness mismatch: " + label)
            quit(3)
            return
        # GroundFloorWalls also contains upper walls/gable details. Do not use
        # their complete AABB as a proxy for the actual supporting footprint.
        if not found_foundation or absf(body.position.y) > .00001 or absf(foundation.get_center().x) > .0001 or absf(foundation.get_center().z) > .0001:
            push_error("Supporting footprint floor pivot mismatch: " + label)
            quit(3)
            return
        # Supporting walls can extend slightly beyond the input quad. Width is
        # Blender Y -> Godot Z, depth is Blender X -> Godot X, not a scale factor.
        var width: float = float(spec["width"])
        var depth: float = float(spec["depth"])
        if absf(foundation.size.z - width) > .0001 or absf(foundation.size.x - depth) > .0001:
            push_error("Building proportions do not match its input footprint")
            quit(3)
            return
        report[label] = {"result": "PASS", "input_width": width, "input_depth": depth,
            "height_above_floor": bounds.end.y, "body_width": body.size.z, "body_depth": body.size.x,
            "triangles": triangles, "surfaces": surfaces, "meshes": meshes.size(), "pivot_y": body.position.y,
            "body_center_xz": [body.get_center().x, body.get_center().z],
            "foundation_center_xz": [foundation.get_center().x, foundation.get_center().z],
            "foundation_width": foundation.size.z, "foundation_depth": foundation.size.x,
            "position": [house.position.x, house.position.y, house.position.z],
            "aabb": str(bounds), "materials": material_details, "no_internal_offset": true}
    if float(report["Wide"]["body_width"]) < 1.9 * float(report["Narrow"]["body_width"]):
        push_error("Wide and Narrow are not distinctly proportioned")
        quit(3)
        return
    if float(report["Narrow"]["body_depth"]) < 1.4 * float(report["Compact"]["body_depth"]):
        push_error("Narrow is not distinctly deeper than Compact")
        quit(3)
        return
    if await _picture(out_dir.path_join("godot_three_presets.png")) != OK:
        quit(3)
        return
    camera.position = Vector3(35, 13, 12)
    camera.look_at(Vector3(0, 4, 12), Vector3.UP)
    if await _picture(out_dir.path_join("godot_three_fronts.png")) != OK:
        quit(3)
        return
    # Independent placement: only Narrow moves; the other roots remain fixed.
    var narrow: Node3D = scene.get_node("Narrow") as Node3D
    narrow.position = Vector3(3, 0, 10)
    for suffix: String in ["X", "Z"]:
        (scene.get_node(NodePath("Narrow" + suffix)) as Node3D).position = Vector3(3, .02, 10)
    (scene.get_node("NarrowLabel") as Label3D).position = Vector3(7.7, .35, 10)
    (scene.get_node("NarrowLabel") as Label3D).text = "Narrow moved independently"
    if not (scene.get_node("Compact") as Node3D).position.is_zero_approx() or not (scene.get_node("Wide") as Node3D).position.is_equal_approx(Vector3(0, 0, 24)):
        push_error("Moving Narrow affected another building")
        quit(3)
        return
    if await _picture(out_dir.path_join("godot_narrow_moved.png")) != OK:
        quit(3)
        return
    var file: FileAccess = FileAccess.open(out_dir.path_join("godot_measurements.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    print("PHASE7_GODOT_PASS ", JSON.stringify(report))
    quit(0)
