extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	var world: Node3D = Node3D.new()
	world.name = "CottageNativeComparison"
	root.add_child(world)
	var environment: WorldEnvironment = WorldEnvironment.new()
	var env: Environment = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.47, 0.58, 0.68)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.9,0.9,0.9)
	env.ambient_light_energy = 0.75
	environment.environment = env
	world.add_child(environment)
	environment.owner = world
	var ground: MeshInstance3D = MeshInstance3D.new()
	var plane: PlaneMesh = PlaneMesh.new()
	plane.size = Vector2(40,40)
	ground.mesh = plane
	var ground_mat: StandardMaterial3D = StandardMaterial3D.new()
	ground_mat.albedo_color = Color(0.38,0.43,0.39)
	ground.material_override = ground_mat
	ground.position.y = -0.015
	world.add_child(ground)
	ground.owner = world
	var light: DirectionalLight3D = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-48,-32,-12)
	light.light_energy = 1.2
	world.add_child(light)
	light.owner = world
	var camera: Camera3D = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 13.5
	camera.position = Vector3(9,7.5,10)
	world.add_child(camera)
	camera.owner = world
	camera.look_at(Vector3(0,1.8,0))
	if OS.get_environment("J_VIEW") == "distance300":
		camera.size = 18.0
	elif OS.get_environment("J_VIEW") == "detail":
		camera.position = Vector3(5,3.4,7)
		camera.size = 5.2
		camera.look_at(Vector3(0,1.3,2))
	camera.current = true
	var asset: String = OS.get_environment("H_ASSET")
	var file_name: String = "res://assets/" + asset
	var packed: PackedScene = load(file_name) as PackedScene
	if packed == null:
		push_error("Cannot load " + file_name)
		quit(1)
		return
	var instance: Node3D = packed.instantiate() as Node3D
	world.add_child(instance)
	instance.owner = world
	for i: int in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	var out: String = OS.get_environment("H_SHOT")
	var image: Image = root.get_texture().get_image()
	var err: Error = image.save_png(out)
	print("09K_CAPTURE ", asset, " ", out, " error=", err, " size=",image.get_width(),"x",image.get_height())
	quit(0 if err == OK else 1)
