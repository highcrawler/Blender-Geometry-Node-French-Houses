extends SceneTree

func _initialize() -> void:
    var packed: PackedScene = load("res://assets/HouseOne.glb") as PackedScene
    if packed == null:
        push_error("GLB did not import as PackedScene")
        quit(1)
        return
    var root: Node = packed.instantiate()
    get_root().add_child(root)
    var meshes: Array[MeshInstance3D] = []
    _collect_meshes(root, meshes)
    var surfaces: int = 0
    var triangles: int = 0
    for node: MeshInstance3D in meshes:
        for index: int in range(node.mesh.get_surface_count()):
            surfaces += 1
            var arrays: Array = node.mesh.surface_get_arrays(index)
            if arrays[Mesh.ARRAY_INDEX] != null:
                triangles += (arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).size() / 3
    print("GODOT_IMPORT meshes=%d surfaces=%d triangles=%d" % [meshes.size(), surfaces, triangles])
    quit(0 if meshes.size() > 0 and triangles > 0 else 1)

func _collect_meshes(node: Node, found: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        found.append(node as MeshInstance3D)
    for child: Node in node.get_children():
        _collect_meshes(child, found)
