"""Non-destructive native-house test: blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/build_variants.py -- HouseOne"""
import bpy, json, math, sys, time
from pathlib import Path
from mathutils import Vector

name = sys.argv[-1]
assert name in ('HouseOne', 'HouseTWo', 'HouseThree')
root = Path('tests/variants'); root.mkdir(parents=True, exist_ok=True)
obj = bpy.data.objects[name]
scene = bpy.context.scene
for other in bpy.data.objects:
    other.hide_render = other != obj
obj.hide_render = False
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
start = time.monotonic()
deps = bpy.context.evaluated_depsgraph_get()
eval_obj = obj.evaluated_get(deps)
mesh = eval_obj.to_mesh()
metrics = {'variant': name, 'blender': bpy.app.version_string, 'source': 'GeometryNodesFrenchHous.blend',
           'group': obj.modifiers[0].node_group.name, 'footprint_vertices': len(obj.data.vertices),
           'vertices': len(mesh.vertices), 'faces': len(mesh.polygons), 'triangles': sum(len(p.vertices)-2 for p in mesh.polygons),
           'uv_layers': [v.name for v in mesh.uv_layers], 'materials': [m.name if m else None for m in mesh.materials],
           'dimensions_m': [round(v, 3) for v in obj.dimensions], 'evaluation_seconds': round(time.monotonic()-start, 3)}
eval_obj.to_mesh_clear()
# Keep an editable variant with its original Geometry Nodes modifier; source .blend remains untouched.
bpy.ops.wm.save_as_mainfile(filepath=str((root/(name+'.blend')).resolve()), compress=True)
# Bake evaluated geometry into a standalone mesh and center its XY footprint at ground level.
# This export copy is intentionally separate from the editable GN source object.
try:
    baked = bpy.data.meshes.new_from_object(eval_obj, preserve_all_data_layers=True, depsgraph=deps)
    lo = [min(v.co[i] for v in baked.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in baked.vertices) for i in range(3)]
    offset = Vector(((lo[0]+hi[0])*0.5, (lo[1]+hi[1])*0.5, lo[2]))
    for v in baked.vertices:
        v.co -= offset
    metrics['export_bake_offset_local_m'] = [round(float(x),3) for x in offset]
    baked_obj = bpy.data.objects.new(name+'_GameReady', baked)
    scene.collection.objects.link(baked_obj)
    bpy.ops.object.select_all(action='DESELECT')
    baked_obj.select_set(True)
    bpy.context.view_layer.objects.active = baked_obj
    bpy.ops.export_scene.gltf(filepath=str((root/(name+'.glb')).resolve()), export_format='GLB', use_selection=True,
                              export_animations=False)
    metrics['glb_bytes'] = (root/(name+'.glb')).stat().st_size
    baked_obj.select_set(False)
    bpy.data.objects.remove(baked_obj, do_unlink=True)
except Exception as exc:
    metrics['export_error'] = repr(exc)
# Fresh scene avoids source scene's video-only output restriction; don't save it in editable test file.
render_scene = bpy.data.scenes.new('Still Preview')
render_scene.collection.objects.link(obj)
bpy.context.window.scene = render_scene
scene = render_scene
cam_data = bpy.data.cameras.new('Test Camera'); cam = bpy.data.objects.new('Test Camera', cam_data); scene.collection.objects.link(cam)
center = obj.matrix_world @ Vector((0, 0, obj.dimensions.z * 0.45))
cam.location = center + Vector((12, -15, 12))
cam.rotation_euler = (center-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.type = 'ORTHO'; cam_data.ortho_scale = max(obj.dimensions)*2.0
scene.camera = cam
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'; scene.display.shading.color_type = 'MATERIAL'; scene.display.shading.show_shadows = True
scene.render.resolution_x = 960; scene.render.resolution_y = 720; scene.render.resolution_percentage = 100
scene.render.filepath = str((root/(name+'.png')).resolve()); scene.render.image_settings.file_format = 'PNG'
try:
    bpy.ops.render.render(write_still=True)
    metrics['screenshot_bytes'] = (root/(name+'.png')).stat().st_size
except Exception as exc:
    metrics['render_error'] = repr(exc)
(root/(name+'.json')).write_text(json.dumps(metrics, indent=2))
print('VARIANT_RESULT', json.dumps(metrics))
