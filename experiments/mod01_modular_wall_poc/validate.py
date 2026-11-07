"""Independent ART wall reference, native GLB, Godot pivots, module seams and photos."""
import hashlib,json,struct
from collections import Counter
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
P=Path(__file__).resolve().parent;R=P.parents[1];assets=P/'godot_test/assets';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
s=json.loads((P/'assembly_audit.json').read_text());godot=json.loads((P/'godot_audit.json').read_text())
union=json.loads((P/'surface_union.json').read_text())
assert union['result']=='PASS' and union['faces_triangles']==28 and union['nonmanifold_or_open_union_edges']==0 and union['duplicate_coplanar_triangles']==0 and not union['mesh_datablocks_welded']
source=R/'experiments/wooden_roof_system_09f/three_owned_cottages.blend'
assert s['source_sha256_before']==s['source_sha256_after']==sha(source)
assert s['shared_frame']['mesh_count']==9 and s['shared_frame']['triangles']==108
assert s['shared_frame']['fingerprint_before']==s['shared_frame']['fingerprint_after']==s['opening_test']['frame_sha_before_after']
assert s['opening_test']['frame_same_object_ids'] and s['opening_test']['connector_and_pivot_roundtrip']
assert [x['id'] for x in s['instances']]==['MOD01_Bay_1','MOD01_Bay_2','MOD01_Bay_3']
assert [x['triangles'] for x in s['instances']]==[10,8,10]
assert [(x['assembled_cap_left'],x['assembled_cap_right']) for x in s['instances']]==[(True,False),(False,False),(False,True)]
assert s['standalone_module']['closed_caps']==2 and s['standalone_module']['triangles']==12
assert all(x['type']=='WALL_PLAIN' and x['height_m']==s['wall_measurement']['height'] and x['thickness_m']==s['wall_measurement']['thickness'] for x in s['instances'])
assert all(x['materials']=={'infill':'09I_A_clay_constant'} for x in s['instances'])
assert s['A']['materials']==s['B']['materials']==['09I_A_clay_constant','09J_A_weathered_oak_constant']
A=assets/'mod01_A_art01_wall.glb';B=assets/'mod01_B_three_modules.glb';assert sha(A)==s['A']['glb_sha256'] and sha(B)==s['B']['glb_sha256']
ref=R/'experiments/art01_medieval_timber_frame/godot_test/assets/art01_B_timber_frame.glb';assert sha(ref)==s['reference_glb_sha256']

def load(path):
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert (magic,version,length)==(0x46546c67,2,len(raw))
 chunks={};offset=12
 while offset<len(raw):
  size,kind=struct.unpack_from('<II',raw,offset);offset+=8;chunks[kind]=raw[offset:offset+size];offset+=size
 doc=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942]
 def accessor(idx):
  a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0)
  fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];width=struct.calcsize('<'+fmt*n);stride=v.get('byteStride',width)
  return tuple(tuple(struct.unpack_from('<'+fmt*n,binary,start+i*stride)) for i in range(a['count']))
 records=[]
 for node in doc['nodes']:
  if 'mesh' not in node:continue
  for prim in doc['meshes'][node['mesh']]['primitives']:
   xyz=accessor(prim['attributes']['POSITION']);inds=accessor(prim['indices']);material=doc['materials'][prim['material']]['name']
   records.append({'name':node['name'],'position':node.get('translation',[]),'rotation':node.get('rotation',[]),'scale':node.get('scale',[]),
                   'xyz':xyz,'indices':inds,'material':material,'triangles':len(inds)//3})
 return doc,records
ref_doc,ref_r=load(ref);A_doc,A_r=load(A);B_doc,B_r=load(B)
assert len(ref_r)==43 and len(A_r)==10 and len(B_r)==12
assert {m['name']:m for m in A_doc['materials']}=={m['name']:m for m in B_doc['materials']}
for m in A_doc['materials']:
 assert m==next(z for z in ref_doc['materials'] if z['name']==m['name'])

def is_frame(row):
 name=row['name'];return name.startswith('ART01_') or (name.startswith(('08A_CornerPost','08A_SideWallPlate')) and row['position'] and row['position'][0]>2)

def signature(row):
 # Actual native GLB POSITION/indices payload, original material and world-parent-relative transform.
 return (row['xyz'],row['indices'],row['material'],tuple(round(x,5) for x in row['position']),tuple(round(x,5) for x in row['rotation']))
frame_ref=[r for r in ref_r if is_frame(r)]
assert len(frame_ref)==9
frame_A=[r for r in A_r if is_frame(r)];frame_B=[r for r in B_r if is_frame(r)]
assert len(frame_A)==len(frame_B)==9
assert Counter(signature(r) for r in frame_ref)==Counter(signature(r) for r in frame_A)==Counter(signature(r) for r in frame_B)
ref_clay=[r for r in ref_r if r['name'].startswith('08A_SideClay') and r['xyz'] and max(v[0] for v in r['xyz'])>2]
A_clay=[r for r in A_r if r['material']=='09I_A_clay_constant'];B_clay=[r for r in B_r if r['material']=='09I_A_clay_constant']
assert len(ref_clay)==len(A_clay)==1 and signature(ref_clay[0])==signature(A_clay[0])
assert len(B_clay)==3 and [r['triangles'] for r in sorted(B_clay,key=lambda r:r['name'])]==[10,8,10]
assert sum(r['triangles'] for r in frame_B)==108 and sum(r['triangles'] for r in B_r)==136
# Visible plaster geometry: every assembled piece has the same front/back height and thickness;
# interval endpoints touch, internal end caps absent by explicit assembly contract.
GA=godot['mod01_A_art01_wall.glb'];GB=godot['mod01_B_three_modules.glb']
assert (GA['mesh_nodes'],GA['triangles'],GA['surfaces'],GA['null_material_surfaces'])==(10,120,10,0)
assert (GB['mesh_nodes'],GB['triangles'],GB['surfaces'],GB['null_material_surfaces'])==(12,136,12,0)
assert GA['bounds_min']==GB['bounds_min'] and GA['bounds_max']==GB['bounds_max']
assert GA['root_children']==GB['root_children'] and GA['root_children'][0]['position']==[0,0,0]
assert not GA['module_pivots'] and len(GB['module_pivots'])==3
assert GA['materials']['09J_A_weathered_oak_constant']==GB['materials']['09J_A_weathered_oak_constant']
for key in ('albedo','roughness','metallic','albedo_texture','normal_texture','normal_enabled','roughness_texture'):
 assert GA['materials']['09I_A_clay_constant'][key]==GB['materials']['09I_A_clay_constant'][key],key
assert GA['materials']['09I_A_clay_constant']['triangles']==12 and GB['materials']['09I_A_clay_constant']['triangles']==28
old=next(x for x in GA['mesh_details'] if x['name'].startswith('08A_SideClay'))
meshes=sorted((x for x in GB['mesh_details'] if x['name'].startswith('MOD01_Bay_')),key=lambda x:x['world_min'][2],reverse=True)
assert len(meshes)==3 and len({x['owner_parent'] for x in meshes})==3
for i,m in enumerate(meshes):
 assert m['owner_parent']==f'MOD01_Bay_{i+1}_Pivot'
 for axis in ('world_min','world_max'):
  assert abs(m[axis][0]-old[axis][0])<5e-5 and abs(m[axis][1]-old[axis][1])<5e-5
 if i<2:assert abs(m['world_min'][2]-meshes[i+1]['world_max'][2])<1e-5
assert abs(meshes[0]['world_max'][2]-old['world_max'][2])<1e-5
assert abs(meshes[-1]['world_min'][2]-old['world_min'][2])<1e-5
for i,pivot in enumerate(sorted(GB['module_pivots'],key=lambda x:x['name'])):
 assert pivot['name']==f'MOD01_Bay_{i+1}_Pivot'
 assert abs(pivot['global_position'][0]-s['wall_measurement']['x_center'])<1e-5
 assert abs(pivot['global_position'][1]-s['wall_measurement']['bottom'])<1e-5
 assert abs(pivot['global_position'][2]+s['instances'][i]['world_mount'][1])<1e-5 # Blender +Y → Godot -Z
image_metrics={}
for engine in ('blender','godot'):
 for view in ('side','iso','detail','distance300'):
  prefix='' if engine=='blender' else 'godot_'
  with Image.open(P/'screenshots'/f'{prefix}A_{view}.png') as img_a,Image.open(P/'screenshots'/f'{prefix}B_{view}.png') as img_b:
   assert img_a.size==img_b.size==(1280,720)
   delta=ImageChops.difference(img_a.convert('RGB'),img_b.convert('RGB'))
   mae=sum(ImageStat.Stat(delta).mean)/3
   assert mae<0.2,(engine,view,mae)
   image_metrics[f'{engine}_{view}']={'mean_absolute_rgb_difference_0_255':mae}
for name in ('single_plain','three_separate','shared_frame','middle_removed','middle_restored','comparison_board','module_proof_board'):
 with Image.open(P/'screenshots'/f'{name}.png') as image:assert image.width>=1280
for f in ('blender.log','godot_import.log','godot_audit.log','godot_capture.log'):
 assert not any('Traceback' in line or 'SCRIPT ERROR' in line or 'ERROR:' in line for line in (P/f).read_text().splitlines()),f
report={'result':'PASS','architecture':'three real module pivot nodes and three owned mesh nodes + one shared frame','source_sha256':sha(source),
        'reference_art01_glb_sha256':sha(ref),'art01_reference_frame_9_meshes_exact_native_payloads':True,
        'art01_reference_wall_clay_exact_native_payload':True,'frame_same_A_B':True,
        'module_world_bay_bounds':[{k:x[k] for k in ('name','world_min','world_max','owner_parent','triangles')} for x in meshes],
        'no_coplanar_internal_clay_caps':True,'middle_module_remove_reinstall_frame_unchanged':True,
        'mesh_count':[10,12],'triangle_count':[120,136],'material_count':2,'surface_count':[10,12],
        'bounds':{'min':GA['bounds_min'],'max':GA['bounds_max']},'pivot':[0,0,0],
        'image_metrics':image_metrics,'glb_bytes':{'A':A.stat().st_size,'B':B.stat().st_size}}
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOD01_TECHNICAL_PASS',report['mesh_count'],report['triangle_count'],'side_blender_mae',image_metrics['blender_side']['mean_absolute_rgb_difference_0_255'])
