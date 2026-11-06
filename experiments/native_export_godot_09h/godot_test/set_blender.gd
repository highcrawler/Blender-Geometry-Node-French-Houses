extends SceneTree

func _initialize() -> void:
	var settings: EditorSettings = EditorInterface.get_editor_settings()
	const KEY: String = "filesystem/import/blender/blender_path"
	print("BLENDER_SETTING_BEFORE ", settings.get_setting(KEY))
	var executable: String = OS.get_environment("H_BLENDER")
	if executable.is_empty():
		executable = "/snap/bin/blender"
	settings.set_setting(KEY, executable)
	print("BLENDER_SETTING_AFTER ", settings.get_setting(KEY))
	quit()
