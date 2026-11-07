"""Independent glTF payload, Godot import, joint, screenshot and source checks."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[1];assets=P/'godot_test/assets';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
a=json.loads((P/'geometry_audit.json').read_text());probe=json.loads((P/'baseline_geometry.json').read_text());g=json.loads((P/'godot_audit.json').read_text())
source=R/'experiments/wooden_roof_system_09f/three_owned_cottages.blend'
assert a['source_sha256_before']==a['source_sha256_after']==probe['source_sha256']==sha(source)
ref=R/'experiments/stone_door_export_09k/godot_test/assets/stone_door_constant_A.glb'
A=assets/'art01_A_baseline.glb';B=assets/'art01_B_timber_frame.glb'
assert sha(A)==sha(ref)==a['A']['sha256']
assert sha(B)==a['B']['sha256']
assert a['unmodified_source_meshes_verified']==34
assert a['removed_existing_braces']==['08A_SideBrace.002','08A_SideBrace.003'] and a['moved_existing_plate']=='08A_SideWallPlate.001'
assert len(a['new_members'])==6 and sum(x['triangles'] for x in a['new_members'])==72
assert (a['net_extra_meshes'],a['net_extra_triangles'])==(4,48)

def load(path):
 raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert(magic,version,length)==(0x46546c67,2,len(raw))
 sections={};off=12
 while off<len(raw):
  n,kind=struct.unpack_from('<II',raw,off);off+=8;sections[kind]=raw[off:off+n];off+=n
 return json.loads(sections[0x4e4f534a]),sections[0x004e4942]

def items(path):
 doc,binary=load(path)
 def accessor(index):
  aa=doc['accessors'][index];v=doc['bufferViews'][aa['bufferView']];start=v.get('byteOffset',0)+aa.get('byteOffset',0)
  count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[aa['type']];fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[aa['componentType']]
  width=struct.calcsize('<'+fmt*count);stride=v.get('byteStride',width)
  return tuple(tuple(struct.unpack_from('<'+fmt*count,binary,start+i*stride)) for i in range(aa['count']))
 nodes={}
 for node in doc['nodes']:
  if 'mesh' not in node:continue
  prims=[]
  for prim in doc['meshes'][node['mesh']]['primitives']:
   pos=accessor(prim['attributes']['POSITION']);ind=accessor(prim['indices']) if 'indices' in prim else tuple((i,) for i in range(len(pos)))
   prims.append((pos,ind,doc['materials'][prim['material']]['name']))
  nodes[node['name']]=(node,tuple(prims))
 return doc,nodes
adoc,an=items(A);bdoc,bn=items(B)
assert adoc['materials']==bdoc['materials'] and len(adoc['materials'])==7
assert len(an)==37 and len(bn)==41
removed={n for n,(obj,_) in an.items() if n.startswith('08A_SideBrace') and obj.get('translation',[0])[0]>0}
assert len(removed)==2 and all(n not in bn for n in removed)
added=set(bn)-set(an);assert added=={x['name'] for x in a['new_members']}
assert len(an.keys() & bn.keys())==35
plate_name=next(n for n in an if n.startswith('08A_SideWallPlate') and an[n][0].get('translation',[0])[0]>0)
changed=[]
for name in an.keys() & bn.keys():
 old,old_p=an[name];new,new_p=bn[name]
 assert old_p==new_p,('positions/indices/surface material changed',name)
 for prop in ('translation','rotation','scale','matrix'):
  av=old.get(prop,[]);bv=new.get(prop,[]);assert len(av)==len(bv)
  if av:
   diff=max(abs(x-y) for x,y in zip(av,bv))
   if name==plate_name and prop=='translation':
    assert abs(bv[0]-av[0]-.065)<2e-5 and max(abs(x-y) for x,y in zip(av[1:],bv[1:]))<2e-5
    changed.append(name)
   else:assert diff<2e-5,(name,prop,diff)
assert changed==[plate_name]
for n in added:
 node,prims=bn[n];assert len(prims)==1 and len(prims[0][1])==36 and prims[0][2]=='09J_A_weathered_oak_constant'
assert [adoc['nodes'][i]['name'] for i in adoc['scenes'][0]['nodes']]==[bdoc['nodes'][i]['name'] for i in bdoc['scenes'][0]['nodes']]

G_A=g['art01_A_baseline.glb'];G_B=g['art01_B_timber_frame.glb']
assert (G_A['mesh_nodes'],G_A['triangles'],G_A['surfaces'],G_A['null_material_surfaces'])==(37,14054,39,0)
assert (G_B['mesh_nodes'],G_B['triangles'],G_B['surfaces'],G_B['null_material_surfaces'])==(41,14102,43,0)
assert G_A['bounds_min']==G_B['bounds_min'] and G_A['bounds_max']==G_B['bounds_max']
assert G_A['root_children']==G_B['root_children'] and G_A['root_children'][0]['position']==[0,0,0]
assert len(G_A['materials'])==len(G_B['materials'])==7
for name,val in G_A['materials'].items():
 if name=='09J_A_weathered_oak_constant':
  assert val['triangles']==264 and val['surfaces']==22
  assert G_B['materials'][name]['triangles']==312 and G_B['materials'][name]['surfaces']==26
  assert {k:v for k,v in val.items() if k not in ('triangles','surfaces')}=={k:v for k,v in G_B['materials'][name].items() if k not in ('triangles','surfaces')}
 else:assert val==G_B['materials'][name],name
ma={x['name']:x for x in G_A['mesh_details']};mb={x['name']:x for x in G_B['mesh_details']}
assert len(ma)==37 and len(mb)==41
removed_g={n for n,x in ma.items() if n.startswith('08A_SideBrace') and x['world_min'][0]>2.0}
assert len(removed_g)==2 and all(n not in mb for n in removed_g)
new_g={n:x for n,x in mb.items() if n.startswith('ART01_')}
assert len(new_g)==6 and sum(x['triangles'] for x in new_g.values())==72
for name in ma.keys() & mb.keys():
 if 'SideWallPlate' in name and ma[name]['world_min'][0]>2:
  assert abs(mb[name]['world_min'][0]-ma[name]['world_min'][0]-.065)<2e-5
 else:
  assert ma[name]['triangles']==mb[name]['triangles']
  for axis in ('world_min','world_max'):
   assert max(abs(x-y) for x,y in zip(ma[name][axis],mb[name][axis]))<2e-5,(name,axis)
for key in ('MidRail','SideSill'):
 bbox=new_g['ART01_'+key]
 assert bbox['world_min'][0]>2.5 and bbox['world_max'][0]<2.71
stone_top=a['measured_wall']['stone_sill_top'];sill=new_g['ART01_SideSill']
assert abs(sill['world_min'][1]-stone_top)<1e-5
rail=new_g['ART01_MidRail']
post1=new_g['ART01_IntermediatePost_1'];post2=new_g['ART01_IntermediatePost_2']
assert rail['world_max'][0]<post1['world_max'][0]-.005 # front faces not coplanar

def overlaps(x,y):return all(x['world_min'][i]<y['world_max'][i] and y['world_min'][i]<x['world_max'][i] for i in range(3))
plate=next(x for n,x in mb.items() if n.startswith('08A_SideWallPlate') and x['world_min'][0]>2.5)
for post in (post1,post2):assert overlaps(post,sill) and overlaps(post,rail) and overlaps(post,plate)
for i,post in enumerate((post1,post2),1):
 brace=new_g[f'ART01_KneeBrace_{i}']
 assert overlaps(brace,post) and overlaps(brace,plate)
 assert brace['world_min'][1]>rail['world_max'][1]+.08 # not crossing mid-rail
for v in ('A','B'):
 for view in ('side','iso','detail','distance300'):
  for engine in ('godot','blender'):
   with Image.open(P/'screenshots'/f'{engine}_{v}_{view}.png') as im:assert im.size==(1280,720)
for f in ('blender.log','godot_import.log','godot_audit.log','godot_capture.log'):
 assert not any('ERROR' in line or 'Traceback' in line for line in (P/f).read_text().splitlines()),f
report={'result':'PASS','baseline_glb_byteidentical_9k':True,'source_sha256':sha(source),'mesh_counts':[37,41],'triangle_counts':[14054,14102],'roof_triangles_unchanged':13692,'body_triangles':[362,410],'surface_counts':[39,43],'materials':7,'removed_brace_meshes':sorted(removed),'repositioned_wall_plate':plate_name,'added_meshes':sorted(added),'net_additional_meshes':4,'net_additional_triangles':48,'unchanged_glb_meshes_position_indices_material_assignment':34,'joint_intersection_checks':'new posts overlap sill, recessed rail and top plate; braces overlap posts and top plate, do not cross rail','side_positive_x':True,'ground_pivot':[0,0,0],'identical_global_bounds':True,'screenshot_count':16,'glb_bytes':{'A':A.stat().st_size,'B':B.stat().st_size}}
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('ART01_TECHNICAL_PASS',report['net_additional_meshes'],report['net_additional_triangles'],flush=True)
