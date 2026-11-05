"""Optional isolated GLB proof, not a Godot test. Run with saved 08F .blend.

blender -b experiments/cottage_generator_08f/Cottage_CC0_08F.blend \\
  -P experiments/cottage_generator_08f/probe_glb.py

Writes only to OS temp, never to the repository.
"""
import bpy
import json
import struct
import tempfile
from pathlib import Path

roof = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('role') == 'roof'
        and o.location.y > 4]
assert len(roof) == 5
bpy.ops.object.select_all(action='DESELECT')
for obj in roof:
    obj.select_set(True)
bpy.context.view_layer.objects.active = roof[0]
path = Path(tempfile.gettempdir()) / 'cottage_08f_roof_probe.glb'
bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True)
data = path.read_bytes()
assert data[:4] == b'glTF' and struct.unpack_from('<I', data, 8)[0] == len(data)
json_length = struct.unpack_from('<I', data, 12)[0]
glb = json.loads(data[20:20+json_length])
triangles = sum(glb['accessors'][prim['indices']]['count']//3
                for mesh in glb['meshes'] for prim in mesh['primitives'])
assert triangles == 5872 and len(glb['materials']) == 1 and len(glb['images']) == 3
assert all('TEXCOORD_0' in prim['attributes']
           for mesh in glb['meshes'] for prim in mesh['primitives'])
mat = glb['materials'][0]
assert 'normalTexture' in mat
assert 'baseColorTexture' in mat['pbrMetallicRoughness']
assert 'metallicRoughnessTexture' in mat['pbrMetallicRoughness']
assert mat['pbrMetallicRoughness']['metallicFactor'] == 0
print('08F_GLB_PROBE_PASS', json.dumps(dict(triangles=triangles,
    images=len(glb['images']), materials=len(glb['materials']), bytes=len(data))), flush=True)
