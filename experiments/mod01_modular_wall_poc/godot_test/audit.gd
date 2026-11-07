extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _texture_info(tex: Texture2D) -> Dictionary:
	if tex == null:
		return {"present":false}
	return {"present":true,"width":tex.get_width(),"height":tex.get_height(),"class":tex.get_class()}

func _run() -> void:
	var names: PackedStringArray = ["mod01_A_art01_wall.glb", "mod01_B_three_modules.glb"]
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
			var obj_min: Vector3 = Vector3(INF, INF, INF)
			var obj_max: Vector3 = Vector3(-INF, -INF, -INF)
			var uv_count: int = 0
			var uv_min: Vector2 = Vector2(INF, INF)
			var uv_max: Vector2 = Vector2(-INF, -INF)
			for si: int in range(mesh.get_surface_count()):
				var ar: Array = mesh.surface_get_arrays(si)
				if ar[Mesh.ARRAY_TEX_UV] != null:
					var uvs: PackedVector2Array = ar[Mesh.ARRAY_TEX_UV]
					for uv: Vector2 in uvs:
						uv_min = uv_min.min(uv)
						uv_max = uv_max.max(uv)
					uv_count += uvs.size()
				var indices: PackedInt32Array = ar[Mesh.ARRAY_INDEX] as PackedInt32Array
				var vertices: PackedVector3Array = ar[Mesh.ARRAY_VERTEX] as PackedVector3Array
				for vertex: Vector3 in vertices:
					var point: Vector3 = obj.global_transform * vertex
					bounds_min = bounds_min.min(point)
					bounds_max = bounds_max.max(point)
					obj_min = obj_min.min(point)
					obj_max = obj_max.max(point)
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
							info["albedo_texture"] = _texture_info(std_mat.albedo_texture)
							info["normal_texture"] = _texture_info(std_mat.normal_texture)
							info["normal_enabled"] = std_mat.normal_enabled
							info["roughness_texture"] = _texture_info(std_mat.roughness_texture)
						mats[mat_name] = info
					var current: Dictionary = mats[mat_name]
					current["triangles"] = int(current["triangles"]) + ntri
					current["surfaces"] = int(current["surfaces"]) + 1
			mesh_details.append({"name":obj.name,"triangles":obj_tris,"surfaces":mesh.get_surface_count(),"position":[obj.global_position.x,obj.global_position.y,obj.global_position.z],"uv_count":uv_count,"uv_min":[uv_min.x,uv_min.y] if uv_count > 0 else [],"uv_max":[uv_max.x,uv_max.y] if uv_count > 0 else [],"world_min":[obj_min.x,obj_min.y,obj_min.z],"world_max":[obj_max.x,obj_max.y,obj_max.z],"owner_parent":obj.get_parent().name})
		var children: Array[Dictionary] = []
		for child: Node in scene.get_children():
			if child is Node3D:
				var n: Node3D = child as Node3D
				children.append({"name":n.name,"position":[n.position.x,n.position.y,n.position.z],"rotation":[n.rotation.x,n.rotation.y,n.rotation.z],"scale":[n.scale.x,n.scale.y,n.scale.z]})
		var module_pivots: Array[Dictionary] = []
		for candidate: Node in scene.find_children("*", "Node3D", true, false):
			if candidate.name.begins_with("MOD01_Bay_") and candidate.name.ends_with("_Pivot"):
				var n3d: Node3D = candidate as Node3D
				module_pivots.append({"name":n3d.name,"global_position":[n3d.global_position.x,n3d.global_position.y,n3d.global_position.z],"local_position":[n3d.position.x,n3d.position.y,n3d.position.z],"basis_x":[n3d.global_basis.x.x,n3d.global_basis.x.y,n3d.global_basis.x.z],"basis_y":[n3d.global_basis.y.x,n3d.global_basis.y.y,n3d.global_basis.y.z],"basis_z":[n3d.global_basis.z.x,n3d.global_basis.z.y,n3d.global_basis.z.z]})
		results[file_name] = {"module_pivots":module_pivots,"mesh_nodes":mesh_nodes.size(),"triangles":tris,"surfaces":surfaces,"materials":mats,"null_material_surfaces":null_material_surfaces,"bounds_min":[bounds_min.x,bounds_min.y,bounds_min.z],"bounds_max":[bounds_max.x,bounds_max.y,bounds_max.z],"root_children":children,"mesh_details":mesh_details}
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
	print("MOD01_AUDIT ", out)
	quit()
