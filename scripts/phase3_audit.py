"""Read-only HouseOne shader, evaluated mesh and baseline GLB audit."""
import bpy
import json
import struct
from collections import Counter
from pathlib import Path

obj = bpy.data.objects['HouseOne']
deps = bpy.context.evaluated_depsgraph_get()
mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.calc_loop_triangles()
audit = {'mesh': {'slots': [m.name if m else None for m in mesh.materials],
                  'faces_per_slot': dict(Counter(p.material_index for p in mesh.polygons)),
                  'triangles_per_slot': dict(Counter(t.material_index for t in mesh.loop_triangles)),
                  'colors': {}, 'uv_layers': [x.name for x in mesh.uv_layers]}, 'materials': {}}
for name in ('RoofColor', 'PaintColor', 'BeamColor'):
    attr = mesh.attributes.get(name)
    if attr:
        samples = [list(attr.data[i].color) for i in sorted({0, len(attr.data)//2, len(attr.data)-1})]
        audit['mesh']['colors'][name] = {'type': attr.data_type, 'domain': attr.domain, 'samples': samples}
for material in mesh.materials:
    if not material:
        continue
    tree = material.node_tree
    shader = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')
    audit['materials'][material.name] = {'principled': {k: {'default': list(s.default_value) if hasattr(s.default_value, '__len__') else s.default_value,
                                                            'links': [f'{l.from_node.name}.{l.from_socket.name}' for l in s.links]}
                                                      for k in ('Base Color', 'Roughness', 'Metallic') for s in [shader.inputs[k]]},
                                         'rgb_nodes': {n.name: list(n.outputs['Color'].default_value) for n in tree.nodes if n.type == 'RGB'},
                                         'group_inputs': {n.name: {s.name: list(s.default_value) if hasattr(s.default_value, '__len__') else s.default_value for s in n.inputs if s.name in ('Color', 'Base Color', 'Roughness')} for n in tree.nodes if n.type == 'GROUP'},
                                         'image_nodes': [n.name for n in tree.nodes if n.type == 'TEX_IMAGE']}
path = Path('tests/materials/exports/BASELINE.glb')
blob = path.read_bytes()
assert blob[:4] == b'glTF'
json_size, json_type = struct.unpack_from('<I4s', blob, 12)
assert json_type == b'JSON'
gltf = json.loads(blob[20:20+json_size])
audit['glb'] = {'bytes': len(blob), 'materials': [{'name': m.get('name'), 'pbr': m.get('pbrMetallicRoughness')} for m in gltf.get('materials', [])],
                'images': gltf.get('images', []), 'textures': gltf.get('textures', []),
                'primitives': [{'material': p.get('material'), 'attributes': list(p['attributes'])} for mesh in gltf['meshes'] for p in mesh['primitives']]}
out = Path('tests/materials/phase3_audit.json')
out.write_text(json.dumps(audit, indent=2))
print('PHASE3_AUDIT', out, json.dumps(audit['glb']))
