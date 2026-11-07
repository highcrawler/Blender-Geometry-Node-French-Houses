"""Compare GLB geometry payloads independently of Blender and Godot import."""
import json, struct, hashlib
from pathlib import Path
p=Path(__file__).resolve().parent

def load(path):
    raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw)
    assert magic==0x46546c67 and version==2 and length==len(raw)
    offset=12;chunks={}
    while offset<len(raw):
        size,kind=struct.unpack_from('<II',raw,offset);offset+=8
        chunks[kind]=raw[offset:offset+size];offset+=size
    return json.loads(chunks[0x4e4f534a]),chunks[0x004e4942]

def audit(path):
    doc,binary=load(path)
    def value(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0)
        comps={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']]
        width=struct.calcsize('<'+fmt)*comps;stride=v.get('byteStride',width)
        assert not a.get('sparse')
        return tuple(tuple(struct.unpack_from('<'+fmt*comps,binary,start+i*stride)) for i in range(a['count']))
    shapes=[];materials=[];triangles=0
    for node in doc['nodes']:
        if 'mesh' not in node:continue
        mesh=doc['meshes'][node['mesh']]
        prims=[]
        for prim in mesh['primitives']:
            positions=value(prim['attributes']['POSITION']);indices=value(prim['indices']) if 'indices' in prim else tuple((i,) for i in range(len(positions)))
            triangles+=len(indices)//3
            geometry=(positions,indices)
            prims.append(hashlib.sha256(repr(geometry).encode()).hexdigest())
            materials.append((doc['materials'][prim['material']]['name'],len(indices)//3))
        # Node transforms should be preserved (mesh node names may have Blender duplicate suffixes).
        transform=tuple(tuple(round(v,5) for v in node[key]) if key in node else None for key in ('matrix','translation','rotation','scale'))
        shapes.append((tuple(sorted(prims)),transform))
    return {'mesh_count':len(shapes),'triangles':triangles,'shape_and_transform_hash':hashlib.sha256(repr(sorted(shapes,key=str)).encode()).hexdigest(),
            'materials':dict((n,sum(c for name,c in materials if name==n)) for n,_ in materials),'root_nodes':[doc['nodes'][i] for i in doc['scenes'][doc.get('scene',0)]['nodes']]}
a=audit(p/'godot_test/assets/baseline_A.glb');b=audit(p/'godot_test/assets/clay_constant_A.glb')
assert a['mesh_count']==b['mesh_count']==37 and a['triangles']==b['triangles']==14054
assert a['shape_and_transform_hash']==b['shape_and_transform_hash']
assert a['materials'].pop('08A_09F_A_clay')==b['materials'].pop('09I_A_clay_constant')==74
assert a['materials']==b['materials']
(p/'geometry_comparison.json').write_text(json.dumps({'baseline':a,'test':b,'identical_geometry_and_mesh_transforms':True,'clay_triangles':74},indent=2)+'\n')
print('09I_GEOMETRY_PASS',a['shape_and_transform_hash'])
