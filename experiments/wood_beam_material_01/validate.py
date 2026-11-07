"""Independent GLB triangle/UV and Godot 4.7 import regression for WOOD-01."""
import hashlib,json,struct
from collections import Counter
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((P/'blender_audit.json').read_text());g=json.loads((P/'godot_audit.json').read_text())
assets=P/'godot_test/assets';source=R/'experiments/wooden_roof_system_09f/three_owned_cottages.blend'
assert b['source_sha256_before']==b['source_sha256_after']==sha(source)
assert b['reference_09k_sha256']==sha(assets/'beam_A_baseline.glb')==sha(R/'experiments/stone_door_export_09k/godot_test/assets/stone_door_constant_A.glb')
assert b['baked']['success'] and b['baked']['resolution']==[512,512]
assert len(b['beams']['B'])==len(b['beams']['C'])==16
for variant in ('B','C'):
 for name,x in b['beams'][variant].items():
  assert x['local_bounds_m'][2]>x['local_bounds_m'][0] and x['local_bounds_m'][2]>x['local_bounds_m'][1]
  assert abs(x['longitudinal_uv_span']-x['local_bounds_m'][2]/1.5)<1e-4
  assert sum(q*q for q in x['long_axis_world'])>.999
vertical=[x for n,x in b['beams']['B'].items() if 'CornerPost' in n];horizontal=[x for n,x in b['beams']['B'].items() if 'WallPlate' in n];diagonal=[x for n,x in b['beams']['B'].items() if 'Brace' in n or 'Rafter' in n]
assert vertical and horizontal and diagonal
assert all(abs(x['long_axis_world'][2])>.999 for x in vertical)
assert all(abs(x['long_axis_world'][2])<.01 for x in horizontal)
assert all(.4<abs(x['long_axis_world'][2])<.95 for x in diagonal)

def load(path):
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert (magic,version,length)==(0x46546c67,2,len(raw));parts={};offset=12
 while offset<len(raw):
  size,kind=struct.unpack_from('<II',raw,offset);offset+=8;parts[kind]=raw[offset:offset+size];offset+=size
 return json.loads(parts[0x4e4f534a]),parts[0x004e4942]

def mesh_data(path):
 doc,binary=load(path)
 def accessor(index):
  a=doc['accessors'][index];view=doc['bufferViews'][a['bufferView']];start=view.get('byteOffset',0)+a.get('byteOffset',0)
  fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];width=struct.calcsize('<'+fmt*count);stride=view.get('byteStride',width)
  return [tuple(struct.unpack_from('<'+fmt*count,binary,start+i*stride)) for i in range(a['count'])]
 records=[];material_tris=Counter();uv_beams=0
 for n in doc['nodes']:
  if 'mesh' not in n:continue
  all_prims=[]
  for prim in doc['meshes'][n['mesh']]['primitives']:
   pos=accessor(prim['attributes']['POSITION']);inds=[a[0] for a in accessor(prim['indices'])] if 'indices' in prim else list(range(len(pos)))
   assert len(inds)%3==0
   triangles=tuple(sorted(tuple(sorted((pos[inds[i]],pos[inds[i+1]],pos[inds[i+2]]))) for i in range(0,len(inds),3)))
   name=doc['materials'][prim['material']]['name'];normalized='09J_A_weathered_oak_constant' if name.startswith('WOOD01_') else name
   material_tris[name]+=len(inds)//3
   if name.startswith('WOOD01_'):
    assert 'TEXCOORD_0' in prim['attributes'] and len(accessor(prim['attributes']['TEXCOORD_0']))==len(pos)
    uv_beams+=1
   all_prims.append((triangles,normalized))
  transform=tuple(tuple(round(x,4) for x in n.get(k,[])) for k in ('translation','rotation','scale','matrix'))
  records.append((tuple(sorted(all_prims,key=str)),transform))
 return doc,sorted(records,key=str),dict(material_tris),uv_beams
files={'A':'beam_A_baseline.glb','B':'beam_B_roughwood.glb','C':'beam_C_procedural.glb'}
parsed={v:mesh_data(assets/name) for v,name in files.items()};base_doc,geometry,base_m,_=parsed['A']
assert len(geometry)==37 and sum(base_m.values())==14054
for variant in ('B','C'):
 doc,other,m,uv=parsed[variant];assert other==geometry,(variant,'geometry/transform/assigned material difference')
 assert uv==16 and m['09J_A_weathered_oak_constant']==72 and m[f'WOOD01_{variant}_'+('rough_wood_PBR' if variant=='B' else 'wave_baked')]==192
 assert all(m.get(k)==v for k,v in base_m.items() if k!='09J_A_weathered_oak_constant')
 refmat={x['name']:x for x in base_doc['materials']};othermat={x['name']:x for x in doc['materials']}
 for k in refmat.keys()-{'09J_A_weathered_oak_constant'}:assert refmat[k]==othermat[k]
 wood=othermat[f'WOOD01_{variant}_'+('rough_wood_PBR' if variant=='B' else 'wave_baked')]
 pbr=wood['pbrMetallicRoughness'];assert 'baseColorTexture' in pbr
 assert ('normalTexture' in wood)==(variant=='B') and ('metallicRoughnessTexture' in pbr)==(variant=='B')
assert len(g)==3
for variant,name in files.items():
 data=g[name];assert (data['mesh_nodes'],data['triangles'],data['surfaces'],data['null_material_surfaces'])==(37,14054,39,0)
 assert data['root_children'][0]['position']==[0,0,0] and data['root_children'][0]['scale']==[1,1,1]
 assert data['bounds_min']==g[files['A']]['bounds_min'] and data['bounds_max']==g[files['A']]['bounds_max']
 if variant!='A':
  mat=data['materials'][f'WOOD01_{variant}_'+('rough_wood_PBR' if variant=='B' else 'wave_baked')]
  assert mat['surfaces']==16 and mat['triangles']==192 and mat['albedo_texture']['present'] and mat['albedo_texture']['width']==(1024 if variant=='B' else 512)
  assert mat['normal_enabled']==(variant=='B') and mat['normal_texture']['present']==(variant=='B') and mat['roughness_texture']['present']==(variant=='B')
  for material_name,reference in g[files['A']]['materials'].items():
   if material_name=='09J_A_weathered_oak_constant':
    assert data['materials'][material_name]['triangles']==72 and data['materials'][material_name]['surfaces']==6
    assert {k:v for k,v in data['materials'][material_name].items() if k not in ('triangles','surfaces')}=={k:v for k,v in reference.items() if k not in ('triangles','surfaces')}
   else:assert data['materials'][material_name]==reference,material_name
  assert sum(not x['uv_count'] for x in data['mesh_details'])>=1
  assert sum(x['uv_count']>0 for x in data['mesh_details'])==16
for name in ('rough_wood_diffuse_1k.jpg','rough_wood_normal_gl_1k.png','rough_wood_rough_1k.jpg','procedural_baked_512.png'):
 with Image.open(P/'textures'/name) as image:assert image.size==(512,512) if name.startswith('procedural') else image.size==(1024,1024)
photos={f'{v}_{view}':P/'screenshots'/f'godot_{v}_{view}.png' for v in 'ABC' for view in ('detail','distance300')}
for path in photos.values():
 with Image.open(path) as img:assert img.size==(1280,720)
costs={'source_texture_bytes':{x.name:x.stat().st_size for x in sorted((P/'textures').glob('*')) if x.suffix in ('.jpg','.png')},'glb_bytes':{v:(assets/f).stat().st_size for v,f in files.items()},'glb_delta_vs_A_bytes':{v:(assets/f).stat().st_size-(assets/files['A']).stat().st_size for v,f in files.items()},'godot_import_cache_bytes':sum(x.stat().st_size for x in (P/'godot_test/.godot/imported').glob('*') if x.is_file())}
report={'result':'PASS','source_unchanged':True,'baseline_09k_byteidentical':True,'triangle_payloads_transform_and_material_assignment_identical':True,'mesh_count':37,'triangles':14054,'surfaces':39,'beam_meshes':16,'beam_triangles':192,'uv_orientations':{'vertical':len(vertical),'horizontal':len(horizontal),'diagonal':len(diagonal)},'pbr_textures_imported':True,'procedural_bake_imported':True,'costs':costs,'hashes':{'source':sha(source),**{v:sha(assets/f) for v,f in files.items()}},'godot_images':{k:str(v.relative_to(P)) for k,v in photos.items()}}
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('WOOD01_TECHNICAL_PASS',json.dumps(costs))
