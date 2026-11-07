"""Read saved A/B/C GLBs, Godot imports, and captures independently of Blender."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
P=Path(__file__).resolve().parent;R=P.parents[1];G=P/'godot_test/assets'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
a=json.loads((P/'assembly_audit.json').read_text());g=json.loads((P/'godot_audit.json').read_text())
source=R/'experiments/wooden_roof_system_09f/three_owned_cottages.blend'
assert a['source_sha256_before']==a['source_sha256_after']==sha(source)
assert a['brace']['original_vertices']==8 and a['brace']['original_triangles']==12
assert abs(sum(x*y for x,y in zip(a['brace']['local_Z_world'],a['brace']['local_Z_world']))-1)<1e-5
assert a['modifiers']['bevel_width_m']==.004 and a['modifiers']['bevel_segments']==3
assert .001<=a['modifiers']['displace_strength_m']<=.003 and a['modifiers']['modifier_applied_before_GLTF']
assert a['shader']['voronoi_feature']=='DISTANCE_TO_EDGE' and a['shader']['dark_is_recessed']
assert a['bake']['resolution']==[512,512] and a['bake']['method']=='Cycles DIFFUSE color-only + NORMAL tangent-space'
ref=R/'experiments/mod02_window_module/godot_test/assets/mod02_B_window_wall.glb'
assert sha(G/'beam_A.glb')==sha(ref)==a['MOD02_reference_sha256']

def parse(path):
 data=path.read_bytes();magic,ver,n=struct.unpack_from('<III',data)
 assert (magic,ver,n)==(0x46546c67,2,len(data))
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 d=json.loads(data[20:20+size]);pos=20+size;size,kind=struct.unpack_from('<II',data,pos);assert kind==0x004e4942
 blob=data[pos+8:pos+8+size]
 def access(i):
  acc=d['accessors'][i];view=d['bufferViews'][acc['bufferView']];start=view.get('byteOffset',0)+acc.get('byteOffset',0)
  f={5121:'B',5123:'H',5125:'I',5126:'f'}[acc['componentType']];dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[acc['type']]
  stride=view.get('byteStride',struct.calcsize('<'+f*dims))
  return tuple(struct.unpack_from('<'+f*dims,blob,start+j*stride) for j in range(acc['count']))
 records={}
 for node in d['nodes']:
  if 'mesh' not in node:continue
  records[node['name']]={'transform':(node.get('translation',[]),node.get('rotation',[]),node.get('scale',[])),
      'prims':[(access(prim['attributes']['POSITION']),access(prim['indices']),d['materials'][prim['material']]['name']) for prim in d['meshes'][node['mesh']]['primitives']]}
 return d,records

records={};docs={}
for label in 'ABC':
 f=G/f'beam_{label}.glb';v=a['variants'][label]
 assert f.stat().st_size==v['glb_bytes'] and sha(f)==v['glb_sha256']
 d,r=parse(f);docs[label]=d;records[label]=r
 assert len(r)==16 and v['mesh_count']==16
 assert v['endpoints_unchanged'] and v['untouched_digest']==a['variants']['A']['untouched_digest']
 assert v['wall_triangles']==204-12+v['brace_triangles']
 assert v['material_count']==len(d['materials']) and v['texture_count']==len(d.get('textures',[]))
 godot=g[f'beam_{label}.glb']
 assert godot['mesh_nodes']==16 and godot['triangles']==v['wall_triangles'] and godot['null_material_surfaces']==0
 assert godot['aperture_probe']=={'center_front_back_hits':0,'off_aperture_front_back_hits':2}
 assert next(x for x in godot['mesh_details'] if x['name']=='ART01_KneeBrace_1')['triangles']==v['brace_triangles']
 assert len(godot['module_pivots'])==3
 assert abs(v['end_plane_z'][0]+a['brace']['length_m']/2)<1e-4
 assert abs(v['end_plane_z'][1]-a['brace']['length_m']/2)<1e-4
assert [a['variants'][s]['brace_vertices'] for s in 'ABC']==[8,216,216]
assert [a['variants'][s]['brace_triangles'] for s in 'ABC']==[12,428,428]
for name in records['A']:
 if name!='ART01_KneeBrace_1':
  assert records['A'][name]==records['B'][name]==records['C'][name],name
assert records['A']['ART01_KneeBrace_1']['transform']==records['B']['ART01_KneeBrace_1']['transform']==records['C']['ART01_KneeBrace_1']['transform']
assert records['B']['ART01_KneeBrace_1']['prims'][0][:2]==records['C']['ART01_KneeBrace_1']['prims'][0][:2]
assert records['A']['ART01_KneeBrace_1']['prims'][0][:2]!=records['B']['ART01_KneeBrace_1']['prims'][0][:2]
for label in 'AB':assert g[f'beam_{label}.glb']['materials']['09J_A_weathered_oak_constant']['albedo_texture']['present']==False
mat=g['beam_C.glb']['materials']['ART_BEAM_C_baked']
assert mat['triangles']==428 and mat['albedo_texture']['width']==mat['normal_texture']['width']==512
assert mat['albedo_texture']['height']==mat['normal_texture']['height']==512 and mat['normal_enabled']
assert mat['albedo_texture']['present'] and mat['normal_texture']['present']
assert set(docs['C']['materials'][i]['name'] for i in range(len(docs['C']['materials'])))=={'09I_A_clay_constant','09J_A_weathered_oak_constant','ART_BEAM_C_baked'}
assert len(docs['C'].get('images',[]))==2
for key in ('bounds_min','bounds_max','root_children','module_pivots'):
 assert g['beam_B.glb'][key]==g['beam_C.glb'][key],key
for name in ('beam_color_512','beam_normal_512'):
 with Image.open(P/'textures'/f'{name}.png') as im:
  assert im.size==(512,512) and len(im.convert('RGB').getcolors(512*512) or [])>16
metrics={}
for engine,views in (('godot',('distance300','side','detail')),('blender',('distance300','side','joint','isolated'))):
 for view in views:
  prefix='godot' if engine=='godot' else 'blender'
  pics=[]
  for label in 'ABC':
   with Image.open(P/'screenshots'/f'{prefix}_{label}_{view}.png') as im:
    assert im.size==(1280,720)
    pics.append(im.convert('RGB'))
  for j,k in ((0,1),(1,2),(0,2)):
   metric=sum(ImageStat.Stat(ImageChops.difference(pics[j],pics[k])).mean)/3
   metrics[f'{engine}_{view}_{"ABC"[j]}{"ABC"[k]}']=round(metric,6)
for f in ('blender.log','godot_import.log','godot_audit.log','godot_capture.log','godot_smoke.log'):
 txt=(P/f).read_text()
 assert not any(x in txt for x in ('Traceback','SCRIPT ERROR','ERROR:','Error: script failed','Parse Error')),f
assert (P/'godot_capture.log').read_text().count('ART_BEAM_CAPTURE')==9
result={'result':'PASS','source_sha256':sha(source),'reference_A_byteidentical_MOD02':True,
        'only_one_brace_mesh_changes':True,'same_B_C_geometry':True,'Godot_color_and_tangent_normal_512_imported':True,
        'brace_vertices':[a['variants'][s]['brace_vertices'] for s in 'ABC'],
        'brace_triangles':[a['variants'][s]['brace_triangles'] for s in 'ABC'],
        'wall_triangles':[a['variants'][s]['wall_triangles'] for s in 'ABC'],
        'glb_bytes':[a['variants'][s]['glb_bytes'] for s in 'ABC'],
        'captured_image_mean_absolute_rgb_0_255':metrics}
(P/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('ART_BEAM_VALIDATION_PASS',result['brace_triangles'],result['glb_bytes'])
