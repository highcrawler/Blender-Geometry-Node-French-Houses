"""Reversible HouseOne PBR export; run from repository root:
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/export_houseone_materials.py -- --house HouseOne
Never saves the source file or changes its Geometry Nodes group.
"""
import argparse
import bpy
import hashlib
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path
from mathutils import Vector

args = argparse.ArgumentParser()
args.add_argument('--house', default='HouseOne')
args.add_argument('--output', default='tests/materials/phase3/HouseOne_PBR.glb')
args.add_argument('--render', action='store_true', help='Render original and PBR copy from identical cameras')
opts = args.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
if opts.house != 'HouseOne':
    raise ValueError('Validated only for HouseOne; other buildings require a separate material audit')
root = Path.cwd()
source = root / 'GeometryNodesFrenchHous.blend'
if Path(bpy.data.filepath).resolve() != source.resolve():
    raise ValueError('Open the original source .blend from the repository root')
output = (root / opts.output).resolve()
if output == source or output.suffix.lower() != '.glb':
    raise ValueError('Output must be a separate .glb path')
output.parent.mkdir(parents=True, exist_ok=True)
obj = bpy.data.objects[opts.house]
deps = bpy.context.evaluated_depsgraph_get()
mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.calc_loop_triangles()
counts = Counter(mesh.materials[p.material_index].name for p in mesh.loop_triangles)
assert len(mesh.loop_triangles) == 50944 and set(counts) == {'Roof', 'GroundFloorWalls', 'UpperFloorsPaint', 'Beam', 'Stone'}, counts
original_materials = {m.name: m for m in mesh.materials if m}

def original_color(name):
    """Take actual evaluated GN attribute values, rather than shared node-group defaults."""
    attr = mesh.attributes.get(name)
    if attr is None or attr.data_type not in ('FLOAT_COLOR', 'BYTE_COLOR'):
        raise ValueError('Missing evaluated color attribute: ' + name)
    first = tuple(attr.data[0].color)
    if any(max(abs(a-b) for a, b in zip(first, entry.color)) > 1e-5 for entry in attr.data):
        raise ValueError('Variable color attribute needs vertex-color export: ' + name)
    return first

def principled(name):
    return next(n for n in original_materials[name].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

colors = {
    'Roof': original_color('RoofColor'),
    'Beam': original_color('BeamColor'),
    'UpperFloorsPaint': tuple(principled('UpperFloorsPaint').inputs['Base Color'].default_value),
    'GroundFloorWalls': tuple(principled('GroundFloorWalls').inputs['Base Color'].default_value),
    'Stone': tuple(original_materials['Stone'].node_tree.nodes['Color'].outputs['Color'].default_value),
}
roughness = {name: float(principled(name).inputs['Roughness'].default_value) for name in colors}
lo = Vector(tuple(min(v.co[i] for v in mesh.vertices) for i in range(3)))
hi = Vector(tuple(max(v.co[i] for v in mesh.vertices) for i in range(3)))
offset = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
for vertex in mesh.vertices:
    vertex.co -= offset
baked = bpy.data.objects.new(opts.house + '_PBR_export_copy', mesh)
bpy.context.scene.collection.objects.link(baked)

# Export only the evaluated duplicate. Material slots and polygon indices remain in place.
for slot in mesh.materials:
    if slot is None or slot.name not in colors:
        continue
    original = slot.name
    mat = bpy.data.materials.new(original + '_PBR')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value = colors[original]
    shader.inputs['Metallic'].default_value = 0.0
    shader.inputs['Roughness'].default_value = roughness[original]
    output_node = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(shader.outputs['BSDF'], output_node.inputs['Surface'])
    for index, existing in enumerate(mesh.materials):
        if existing and existing.name == original:
            mesh.materials[index] = mat
bpy.ops.object.select_all(action='DESELECT')
baked.select_set(True)
bpy.context.view_layer.objects.active = baked
bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True,
                          export_animations=False, export_vertex_color='NONE')
blob = output.read_bytes()
size, chunk = struct.unpack_from('<I4s', blob, 12)
assert blob[:4] == b'glTF' and chunk == b'JSON'
gltf = json.loads(blob[20:20+size])
materials = gltf['materials']
primitives = [p for m in gltf['meshes'] for p in m['primitives']]
assert len(materials) == 5 and len(primitives) == 5
assert all('baseColorFactor' in m['pbrMetallicRoughness'] for m in materials)
assert all('COLOR_0' not in p['attributes'] for p in primitives)
assert sum(counts.values()) == 50944
report = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'blender': bpy.app.version_string,
          'house': opts.house, 'export': str(output.relative_to(root)), 'glb_bytes': len(blob),
          'glb_sha256': hashlib.sha256(blob).hexdigest(), 'vertices': len(mesh.vertices),
          'faces': len(mesh.polygons), 'triangles': len(mesh.loop_triangles),
          'material_triangles': dict(counts), 'material_count': len(materials),
          'original_linear_colors': colors, 'roughness': roughness,
          'mesh_slot_names': [m.name if m else None for m in mesh.materials],
          'offset': list(offset), 'glb_materials': materials,
          'glb_primitives': [{'material': p.get('material'), 'attributes': list(p['attributes'])} for p in primitives],
          'glb_images': len(gltf.get('images', [])), 'glb_textures': len(gltf.get('textures', []))}
report_path = output.with_suffix('.json')
report_path.write_text(json.dumps(report, indent=2))
print('PHASE3_EXPORT', report_path, 'bytes', len(blob), 'triangles', len(mesh.loop_triangles), flush=True)

if opts.render:
    # Same baked mesh, camera, lights and Cycles settings for original/PBR renders.
    scene = bpy.data.scenes.new('Phase3_Comparison')
    scene.collection.objects.link(baked)
    bpy.context.window.scene = scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world = bpy.data.worlds.new('Phase3_NeutralWorld')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.65, 0.68, 0.72, 1)
    bg.inputs['Strength'].default_value = 0.8
    scene.view_settings.view_transform = 'AgX'
    camera_data = bpy.data.cameras.new('Comparison_Ortho')
    camera = bpy.data.objects.new('Comparison_Ortho', camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = 'ORTHO'
    scene.camera = camera
    light_data = bpy.data.lights.new('Comparison_Area', 'AREA')
    light = bpy.data.objects.new('Comparison_Area', light_data)
    scene.collection.objects.link(light)
    light.location = (2, -3, 12)
    light_data.energy, light_data.shape, light_data.size = 1800, 'DISK', 9
    views = {'iso': ((12, -15, 12), (0, 0, 3.7), 15),
             'front': ((16, 0, 5.2), (0, 0, 3.7), 12),
             'facade': ((11, -5, 4.8), (0, -0.4, 4.2), 6)}
    for variant in ('original', 'pbr'):
        if variant == 'original':
            for i, mat in enumerate(mesh.materials):
                if mat and mat.name.endswith('_PBR'):
                    mesh.materials[i] = original_materials[mat.name[:-4]]
        else:
            for i, mat in enumerate(mesh.materials):
                if mat and mat.name in original_materials:
                    mesh.materials[i] = bpy.data.materials[mat.name + '_PBR']
        for view, (eye, target, scale) in views.items():
            camera.location = eye
            camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
            camera_data.ortho_scale = scale
            scene.render.filepath = str(output.parent / ('blender_' + variant + '_' + view + '.png'))
            bpy.ops.render.render(write_still=True, scene=scene.name)
            print('PHASE3_BLENDER_SCREENSHOT', scene.render.filepath, flush=True)
