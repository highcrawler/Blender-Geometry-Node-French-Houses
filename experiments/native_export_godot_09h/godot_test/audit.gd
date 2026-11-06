extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var names: PackedStringArray = ["cottage_A.glb", "single_A.blend", "cottage_B.glb", "single_B.blend", "cottage_C.glb", "single_C.blend", "active_A_three_houses.blend", "active_B_three_houses.blend", "active_C_three_houses.blend"]
	var results: Dictionary = {}
	for file_name: String in names:
		var path: String = "res://assets/" + file_name
		var packed: PackedScene = load(path) as PackedScene
		if packed == null:
			results[file_name] = {"error": "load failed"}
			continue
		var scene: Node3D = packed.instantiate() as Node3D
		if scene == null:
			results[file_name] = {"error": "not a Node3D scene"}
			continue
		root.add_child(scene)
		var mesh_nodes: Array[Node] = scene.find_children("*", "MeshInstance3D", true, false)
		var tris: int = 0
		var surfaces: int = 0
		var mats: Dictionary = {}
		var mesh_details: Array[Dictionary] = []
		var bounds_min: Vector3 = Vector3(INF, INF, INF)
		var bounds_max: Vector3 = Vector3(-INF, -INF, -INF)
		var null_material_surfaces: int = 0
		for node: Node in mesh_nodes:
			var obj: MeshInstance3D = node as MeshInstance3D
			var mesh: Mesh = obj.mesh
			if mesh == null:
				continue
			var obj_tris: int = 0
			for si: int in range(mesh.get_surface_count()):
				var ar: Array = mesh.surface_get_arrays(si)
				var indices: PackedInt32Array = ar[Mesh.ARRAY_INDEX] as PackedInt32Array
				var vertices: PackedVector3Array = ar[Mesh.ARRAY_VERTEX] as PackedVector3Array
				for vertex: Vector3 in vertices:
					var point: Vector3 = obj.global_transform * vertex
					bounds_min = bounds_min.min(point)
					bounds_max = bounds_max.max(point)
				var ntri: int = indices.size() / 3 if indices.size() > 0 else vertices.size() / 3
				tris += ntri
				obj_tris += ntri
				surfaces += 1
				var mat: Material = obj.get_active_material(si)
				if mat == null:
					null_material_surfaces += 1
				else:
					var mat_name: String = mat.resource_name
					if mat_name.is_empty():
						mat_name = "<unnamed>"
					if not mats.has(mat_name):
						var info: Dictionary = {"triangles":0,"surfaces":0,"class":mat.get_class()}
						if mat is StandardMaterial3D:
							var std_mat: StandardMaterial3D = mat as StandardMaterial3D
							info["albedo"] = [std_mat.albedo_color.r, std_mat.albedo_color.g, std_mat.albedo_color.b, std_mat.albedo_color.a]
							info["roughness"] = std_mat.roughness
							info["metallic"] = std_mat.metallic
						mats[mat_name] = info
					var current: Dictionary = mats[mat_name]
					current["triangles"] = int(current["triangles"]) + ntri
					current["surfaces"] = int(current["surfaces"]) + 1
			mesh_details.append({"name":obj.name,"triangles":obj_tris,"surfaces":mesh.get_surface_count(),"position":[obj.global_position.x,obj.global_position.y,obj.global_position.z]})
		var children: Array[Dictionary] = []
		for child: Node in scene.get_children():
			if child is Node3D:
				var n: Node3D = child as Node3D
				children.append({"name":n.name,"position":[n.position.x,n.position.y,n.position.z],"rotation":[n.rotation.x,n.rotation.y,n.rotation.z],"scale":[n.scale.x,n.scale.y,n.scale.z]})
		results[file_name] = {"mesh_nodes":mesh_nodes.size(),"triangles":tris,"surfaces":surfaces,"materials":mats,"null_material_surfaces":null_material_surfaces,"bounds_min":[bounds_min.x,bounds_min.y,bounds_min.z],"bounds_max":[bounds_max.x,bounds_max.y,bounds_max.z],"root_children":children,"mesh_details":mesh_details}
		root.remove_child(scene)
		scene.free()
	var out: String = OS.get_environment("H_REPORT")
	if out.is_empty():
		out = "res://../godot_audit.json"
	var f: FileAccess = FileAccess.open(out, FileAccess.WRITE)
	if f == null:
		push_error("Cannot write report " + out)
	else:
		f.store_string(JSON.stringify(results, "  "))
		f.close()
	print("09H_AUDIT ", out)
	quit()
