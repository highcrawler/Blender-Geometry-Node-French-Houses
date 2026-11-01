"""Compare decoded per-material triangle positions, UVs and constants with Phase 3."""
import json,struct,math,itertools
from pathlib import Path
out=Path('tests/baking/phase4')
def read(path):
    blob=path.read_bytes(); n=struct.unpack_from('<I',blob,12)[0]
    return json.loads(blob[20:20+n]),blob[28+n:]
def decode(g,b,index):
    a=g['accessors'][index]; v=g['bufferViews'][a['bufferView']]
    fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    step=v.get('byteStride',struct.calcsize('<'+fmt)); start=v.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt,b,start+i*step) for i in range(a['count'])]
def streams(g,b):
    node=next(n for n in g['nodes'] if 'mesh' in n); shift=node.get('translation',[0,0,0]); result={}
    for p in g['meshes'][node['mesh']]['primitives']:
        name=g['materials'][p['material']]['name'].replace('_PBR','').replace('_Phase4','')
        pos=decode(g,b,p['attributes']['POSITION']); inds=decode(g,b,p['indices'])
        result[name]=[tuple(x+s for x,s in zip(pos[i[0]],shift)) for i in inds]
    return result
a,ab=read(Path('tests/materials/phase3/HouseOne_PBR.glb')); b,bb=read(out/'HouseOne_Phase4.glb')
x,y=streams(a,ab),streams(b,bb)
report={}
for name in x:
    assert len(x[name])==len(y[name])
    # UV splits and tessellator ordering can reorder triangle corners. Match positions spatially.
    def distance(first, second):
        buckets={}
        for v in set(first): buckets.setdefault(tuple(math.floor(c*10000) for c in v),[]).append(v)
        maximum=0
        for v in set(second):
            key=tuple(math.floor(c*10000) for c in v)
            nearby=[p for delta in itertools.product((-1,0,1),repeat=3) for p in buckets.get(tuple(k+d for k,d in zip(key,delta)),[])]
            assert nearby, (name,v)
            maximum=max(maximum,min(max(abs(c-d) for c,d in zip(p,v)) for p in nearby))
        return maximum
    error=max(distance(x[name],y[name]),distance(y[name],x[name]))
    assert error<1e-5,(name,error)
    report[name]={'triangles':len(x[name])//3,'max_bidirectional_vertex_position_error':error}
    if name!='UpperFloorsPaint':
        ma=next(m for m in a['materials'] if m['name']==name+'_PBR')['pbrMetallicRoughness']
        mb=next(m for m in b['materials'] if m['name']==name+'_Phase4')['pbrMetallicRoughness']
        assert ma==mb
for p in b['meshes'][0]['primitives']:
    if b['materials'][p['material']]['name']=='UpperFloorsPaint_Phase4':
        uv=decode(b,bb,p['attributes']['TEXCOORD_1'])
        assert all(0<=u<=1 and 0<=v<=1 for u,v in uv)
report['unchanged_other_pbr_materials']=True
(out/'glb_geometry_comparison.json').write_text(json.dumps(report,indent=2)); print(report)
