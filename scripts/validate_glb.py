"""Validate exported GLB structure, ground origin and triangle count without external packages."""
import json
import struct
import sys
from pathlib import Path

for filename in sys.argv[1:] or [str(p) for p in Path('tests/variants').glob('*.glb')]:
    data = Path(filename).read_bytes()
    assert data[:4] == b'glTF' and struct.unpack_from('<I', data, 8)[0] == len(data)
    size, kind = struct.unpack_from('<I4s', data, 12)
    assert kind == b'JSON'
    doc = json.loads(data[20:20+size])
    meshes = doc['meshes']
    primitives = [prim for mesh in meshes for prim in mesh['primitives']]
    accessors = doc['accessors']
    triangles = sum(accessors[prim['indices']]['count'] // 3 for prim in primitives)
    mins = [accessors[prim['attributes']['POSITION']]['min'] for prim in primitives]
    maxs = [accessors[prim['attributes']['POSITION']]['max'] for prim in primitives]
    lower = [min(coord[axis] for coord in mins) for axis in range(3)]
    upper = [max(coord[axis] for coord in maxs) for axis in range(3)]
    assert len(meshes) == 1 and triangles > 0
    assert all(prim.get('mode', 4) == 4 and {'POSITION', 'NORMAL', 'TEXCOORD_0'} <= prim['attributes'].keys() for prim in primitives)
    assert abs(lower[1]) < 0.001 and abs(lower[0]+upper[0]) < 0.001 and abs(lower[2]+upper[2]) < 0.001
    assert all('translation' not in node for node in doc.get('nodes', []))
    print(f'{filename}: PASS triangles={triangles} ground_y={lower[1]:.4f} materials={len(doc.get("materials", []))} textures={len(doc.get("textures", []))}')
