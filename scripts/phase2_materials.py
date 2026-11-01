"""Reproducible HouseOne material and reduction experiment (Blender 5.2.2).
Run from repository root: blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/phase2_materials.py
Does not save or modify the source .blend or Phase-1 baseline.
"""
import bpy
import hashlib
import json
import math
import time
from pathlib import Path
from mathutils import Vector

ROOT = Path.cwd()
OUT = ROOT / 'tests/materials'
for folder in ('blender', 'godot', 'exports'):
    (OUT / folder).mkdir(parents=True, exist_ok=True)
source = ROOT / 'GeometryNodesFrenchHous.blend'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
obj = bpy.data.objects['HouseOne']
source_scene = bpy.context.scene
modifier = next(m for m in obj.modifiers if m.type == 'NODES')
inputs = modifier.properties.inputs
socket_data = {}
for item in modifier.node_group.interface.items_tree:
    if item.item_type != 'SOCKET' or item.in_out != 'INPUT' or item.name == 'Input':
        continue
    v = getattr(inputs, item.identifier).value
    if hasattr(v, '__len__') and not isinstance(v, str):
        v = list(v)
    elif isinstance(v, bpy.types.ID):
        v = v.name
    socket_data[item.name] = {'identifier': item.identifier, 'value': v,
                              'default': list(item.default_value) if hasattr(item.default_value, '__len__') and not isinstance(item.default_value, str) else str(item.default_value)}
assert socket_data['SpawnIVY']['value'] is True
assert socket_data['High Polz Plants']['value'] is True

# Traverse material subgroups to distinguish image nodes elsewhere in source from image nodes actually used here.
def describe_tree(tree, seen=None):
    seen = set() if seen is None else seen
    if tree is None or tree.as_pointer() in seen:
        return []
    seen.add(tree.as_pointer())
    found = []
    for n in tree.nodes:
        found.append({'tree': tree.name, 'node': n.name, 'type': n.bl_idname,
                      'attribute': getattr(n, 'attribute_name', None),
                      'image': getattr(getattr(n, 'image', None), 'name', None)})
        if n.type == 'GROUP':
            found.extend(describe_tree(n.node_tree, seen))
    return found

manifest = {'source': str(source.relative_to(ROOT)), 'source_sha256': source_hash,
            'blender_version': bpy.app.version_string, 'object': obj.name,
            'actual_modifier_inputs': socket_data,
            'source_file_images': [{'name': i.name, 'packed': bool(i.packed_file), 'filepath': i.filepath} for i in bpy.data.images if i.source == 'FILE'],
            'materials': {}, 'variants': {}}

# Evaluate once in each state; keep export mesh separate from GN object and offset only the export copy.
def bake():
    deps = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(deps)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=deps)
    mesh.calc_loop_triangles()
    return mesh

for variant in ('BASELINE', 'REDUCED'):
    bpy.context.window.scene = source_scene
    if variant == 'REDUCED':
        # Existing per-object modifier sockets; never change the shared GenerateHouse node group.
        inputs.Socket_12.value = False  # SpawnIVY
        inputs.Socket_14.value = False  # High Polz Plants
        obj.update_tag()
        bpy.context.view_layer.update()
    start_eval = time.monotonic()
    mesh = bake()
    eval_seconds = time.monotonic() - start_eval
    counts = {m.name: {'faces': 0, 'triangles': 0} for m in mesh.materials if m}
    for face in mesh.polygons:
        material = mesh.materials[face.material_index]
        if material:
            counts[material.name]['faces'] += 1
            counts[material.name]['triangles'] += len(face.vertices) - 2
    if variant == 'BASELINE':
        for mat in mesh.materials:
            if mat:
                manifest['materials'][mat.name] = describe_tree(mat.node_tree)
    report = {'modifier_inputs': {key: getattr(inputs, val['identifier']).value if isinstance(getattr(inputs, val['identifier']).value, (bool, int, float, str)) else str(getattr(inputs, val['identifier']).value) for key, val in socket_data.items()},
              'vertices': len(mesh.vertices), 'faces': len(mesh.polygons),
              'triangles': len(mesh.loop_triangles),
              'materials': [m.name for m in mesh.materials if m],
              'material_counts': counts, 'evaluation_seconds': round(eval_seconds, 3),
              'attributes': [{'name': a.name, 'domain': a.domain, 'type': a.data_type} for a in mesh.attributes]}
    lo = Vector(tuple(min(v.co[i] for v in mesh.vertices) for i in range(3)))
    hi = Vector(tuple(max(v.co[i] for v in mesh.vertices) for i in range(3)))
    offset = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    report['local_bake_offset'] = list(offset)
    report['local_dimensions'] = list(hi - lo)
    for v in mesh.vertices:
        v.co -= offset
    baked = bpy.data.objects.new('HouseOne_' + variant, mesh)
    bpy.context.scene.collection.objects.link(baked)
    bpy.ops.object.select_all(action='DESELECT')
    baked.select_set(True)
    bpy.context.view_layer.objects.active = baked
    path = OUT / 'exports' / (variant + '.glb')
    export_start = time.monotonic()
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_animations=False)
    report['export_seconds'] = round(time.monotonic() - export_start, 3)
    report['glb_bytes'] = path.stat().st_size
    report['glb_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()

    # Fresh scene avoids the source scene's video-only output restrictions.
    baked.select_set(False)
    bpy.context.scene.collection.objects.unlink(baked)
    scene = bpy.data.scenes.new('Material_' + variant)
    scene.collection.objects.link(baked)
    bpy.context.window.scene = scene
    # Physically based CPU Cycles shading of the UNCHANGED material nodes. No new building materials.
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new('Neutral_World_' + variant)
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.65, 0.68, 0.72, 1)
    bg.inputs['Strength'].default_value = 0.8
    scene.view_settings.view_transform = 'AgX'
    cam_data = bpy.data.cameras.new('Comparison_Ortho')
    cam = bpy.data.objects.new('Comparison_Ortho', cam_data)
    scene.collection.objects.link(cam)
    cam_data.type = 'ORTHO'
    scene.camera = cam
    light_data = bpy.data.lights.new('Comparison_Area', 'AREA')
    light = bpy.data.objects.new('Comparison_Area', light_data)
    scene.collection.objects.link(light)
    light.location = (2, -3, 12)
    light_data.energy = 1800
    light_data.shape = 'DISK'
    light_data.size = 9
    views = {
        'iso': ((12, -15, 12), (0, 0, 3.7), 15),
        'front': ((16, 0, 5.2), (0, 0, 3.7), 12),
        'facade': ((11, -5, 4.8), (0, -0.4, 4.2), 6),
    }
    view_report = {}
    for view, (location, target, scale) in views.items():
        cam.location = location
        cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cam_data.ortho_scale = scale
        output = OUT / 'blender' / (variant.lower() + '_' + view + '.png')
        scene.render.filepath = str(output)
        render_start = time.monotonic()
        bpy.ops.render.render(write_still=True, scene=scene.name)
        view_report[view] = {'camera': location, 'target': target, 'ortho_scale': scale,
                             'png_bytes': output.stat().st_size, 'render_seconds': round(time.monotonic() - render_start, 2)}
        (OUT / 'measurements.json').write_text(json.dumps(manifest, indent=2))
    report['views'] = view_report
    manifest['variants'][variant] = report
    (OUT / 'measurements.json').write_text(json.dumps(manifest, indent=2))
    print('PHASE2_VARIANT', variant, report['triangles'], report['glb_bytes'], flush=True)
print('PHASE2_DONE', flush=True)
