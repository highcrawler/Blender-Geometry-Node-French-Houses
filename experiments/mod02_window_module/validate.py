"""Independent saved-GLB/Godot/topology/image gate for MOD-02."""
from pathlib import Path
from collections import Counter
from PIL import Image,ImageChops,ImageStat
import hashlib,json,struct
P=Path(__file__).resolve().parent;R=P.parents[1];assets=P/'godot_test/assets'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((P/'assembly_audit.json').read_text())
top=json.loads((P/'topology.json').read_text())
g=json.loads((P/'godot_audit.json').read_text())
assert top['result']=='PASS' and top['open_assembled_edges']==top['duplicate_assembled_triangles']==top['opening_center_ray_hits_front_back_plaster']==0
assert top['assembled_plaster_triangles']==48 and top['assembled_edge_multiplicities']=={'2':72}
assert top['standalone_window_plaster_triangles']==32 and top['front_back_and_reveal_winding_correct']
source=R/'experiments/wooden_roof_system_09f/three_owned_cottages.blend'
assert sha(source)==audit['source_sha256_before']==audit['source_sha256_after']
assert audit['frame_before']==audit['frame_after_swap']==audit['frame_after_swap_back']
assert audit['frame_member_count']==9 and audit['frame_member_triangles']==108
assert all(audit['swap_back'].values()) and audit['swap_back']['restored_type']=='WALL_PLAIN'
assert audit['window_contract']['type']=='WALL_WINDOW' and audit['window_contract']['owned_meshes']==['MOD01_Bay_2_Infill','MOD01_Bay_2_left_jamb','MOD01_Bay_2_right_jamb','MOD01_Bay_2_head','MOD01_Bay_2_sill']
assert audit['window_contract']['connectors_local']==audit['standalone_contract']['connectors_local']
assert audit['window_contract']['world_mount']==audit['standalone_contract']['world_mount']
assert [audit['window_contract']['assembled_cap_left'],audit['window_contract']['assembled_cap_right']]==[False,False]
assert [audit['standalone_contract']['assembled_cap_left'],audit['standalone_contract']['assembled_cap_right']]==[True,True]
assert audit['window_contract']['triangles']==28 and audit['standalone_contract']['triangles']==32
assert audit['window_contract']['wood_part_triangles']==48
assert len(audit['window_part_objects'])==4 and len({x['name'] for x in audit['window_part_objects']})==4
ref=R/'experiments/mod01_modular_wall_poc/godot_test/assets/mod01_B_three_modules.glb'
paths={v:assets/name for v,name in (('A','mod02_A_three_plain.glb'),('B','mod02_B_window_wall.glb'),('C','mod02_C_window_only.glb'))}
assert sha(ref)==sha(paths['A'])==audit['mod01_reference_glb_sha256']
for v,path in paths.items():
 assert sha(path)==audit['variants'][v]['glb_sha256'] and path.stat().st_size==audit['variants'][v]['glb_bytes']

def parse(path):
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert (magic,version,length)==(0x46546c67,2,len(raw))
 size,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
 doc=json.loads(raw[20:20+size]);offset=20+size
 n,kind=struct.unpack_from('<II',raw,offset);assert kind==0x004e4942
 binary=raw[offset+8:offset+8+n]
 def accessor(i):
  a=doc['accessors'][i];view=doc['bufferViews'][a['bufferView']];start=view.get('byteOffset',0)+a.get('byteOffset',0)
  f={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  stride=view.get('byteStride',struct.calcsize('<'+f*width));return tuple(tuple(struct.unpack_from('<'+f*width,binary,start+k*stride)) for k in range(a['count']))
 result=[]
 for node in doc['nodes']:
  if 'mesh' not in node:continue
  for prim in doc['meshes'][node['mesh']]['primitives']:
   result.append((node['name'],accessor(prim['attributes']['POSITION']),accessor(prim['indices']),
                  doc['materials'][prim['material']]['name'],node.get('translation',[]),node.get('rotation',[])))
 return doc,result

docs={};records={}
for v,path in paths.items():docs[v],records[v]=parse(path)
assert [len(records[v]) for v in ('A','B','C')]==[12,16,5]
assert [x[0] for x in records['A'][:9]]==[x[0] for x in records['B'][:9]]
assert records['A'][:9]==records['B'][:9], 'shared nine frame native-GLB vertex/index/material/transform changed'
for name in ('MOD01_Bay_1_Infill','MOD01_Bay_3_Infill'):
 assert next(x for x in records['A'] if x[0]==name)==next(x for x in records['B'] if x[0]==name)
assert all({m['name'] for m in docs[v]['materials']}=={'09I_A_clay_constant','09J_A_weathered_oak_constant'} for v in docs)
GA,GB,GC=[g['mod02_'+name+'.glb'] for name in ('A_three_plain','B_window_wall','C_window_only')]
for variant,go in (('A',GA),('B',GB),('C',GC)):
 expected={'A':(12,136,12),'B':(16,204,16),'C':(5,80,5)}[variant]
 assert (go['mesh_nodes'],go['triangles'],go['surfaces'])==expected
 assert go['null_material_surfaces']==0 and len(go['materials'])==2
 assert go['aperture_probe']['center_front_back_hits']==(2 if variant=='A' else 0)
 assert go['aperture_probe']['off_aperture_front_back_hits']==2
 assert len(go['module_pivots'])==(1 if variant=='C' else 3)
 for pivot in go['module_pivots']:
  assert abs(pivot['global_position'][0]-2.55)<1e-4 and abs(pivot['global_position'][1]-.25)<1e-5
assert GA['bounds_min']==GB['bounds_min'] and GA['bounds_max']==GB['bounds_max']
assert GA['root_children']==GB['root_children'] and GA['root_children'][0]['position']==[0,0,0]
assert GB['materials']['09I_A_clay_constant']['triangles']==48
assert GB['materials']['09J_A_weathered_oak_constant']['triangles']==156
assert GC['materials']['09I_A_clay_constant']['triangles']==32
assert GC['materials']['09J_A_weathered_oak_constant']['triangles']==48
for mat in GA['materials']:
 for v in (GB,GC):
  for field in ('albedo','roughness','metallic','albedo_texture','normal_texture','roughness_texture'):
   assert GA['materials'][mat][field]==v['materials'][mat][field]
assert {d['name']:d for d in GA['mesh_details'] if d['name'] in [r[0] for r in records['A'][:9]]}=={d['name']:d for d in GB['mesh_details'] if d['name'] in [r[0] for r in records['B'][:9]]}
assert next(x for x in GB['mesh_details'] if x['name']=='MOD01_Bay_2_Infill')['owner_parent']=='MOD01_Bay_2_Pivot'
assert all(next(x for x in GB['mesh_details'] if x['name']=='MOD01_Bay_2_'+s)['owner_parent']=='MOD01_Bay_2_Pivot' for s in ('left_jamb','right_jamb','head','sill'))
for f in ('blender.log','godot_import.log','godot_audit.log','godot_capture.log'):
 text=(P/f).read_text()
 assert not any(word in text for word in ('Traceback','SCRIPT ERROR','ERROR:','Error: script failed','Parse Error')),f
assert (P/'godot_capture.log').read_text().count('MOD02_CAPTURE')==14
image_metrics={}
for engine in ('blender','godot'):
 for view in ('side','iso','detail','distance300'):
  prefix='' if engine=='blender' else 'godot_'
  with Image.open(P/'screenshots'/f'{prefix}A_{view}.png') as a,Image.open(P/'screenshots'/f'{prefix}B_{view}.png') as b:
   assert a.size==b.size==(1280,720)
   mae=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
   assert mae>.01,(engine,view,mae)
   image_metrics[engine+'_'+view]={'mean_absolute_rgb_difference_0_255':round(mae,5)}
with Image.open(P/'screenshots/A_side.png') as a,Image.open(P/'screenshots/A_restored.png') as b:
 restored_pixel_equal=ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
assert restored_pixel_equal
for name in ('B_window_front','B_window_oblique','B_reveal_detail','C_single_front','C_single_oblique','C_single_back','godot_B_window_front','godot_B_window_oblique','godot_B_reveal_detail','godot_C_single_front','godot_C_single_oblique','godot_C_single_back'):
 with Image.open(P/'screenshots'/f'{name}.png') as image:assert image.size==(1280,720)
for name in ('comparison_board','module_proof_board'):
 with Image.open(P/'screenshots'/f'{name}.png') as image:assert image.width>=1280
result={'result':'PASS','source_sha256':sha(source),'A_byteidentical_MOD01_reference':True,
        'frame_native_glb_payload_9_meshes_identical_A_B':True,'neighbor_infill_native_glb_payloads_identical_A_B':True,
        'true_aperture_Godot_triangle_rays':{v:go['aperture_probe'] for v,go in (('A',GA),('B',GB),('C',GC))},
        'correctly_oriented_sealed_reveals':True,'shared_frame_and_neighbors_unchanged_on_swap_back':True,
        'restored_wall_Blender_pixels_identical_to_A':restored_pixel_equal,
        'mesh_count':[12,16,5],'triangle_count':[136,204,80],'surface_count':[12,16,5],
        'material_count':2,'main_wall_bounds':{'min':GA['bounds_min'],'max':GA['bounds_max']},
        'image_metrics':image_metrics,'glb_bytes':{v:paths[v].stat().st_size for v in paths}}
(P/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('MOD02_TECHNICAL_PASS',result['mesh_count'],result['triangle_count'],'A_restore_identical',restored_pixel_equal)
