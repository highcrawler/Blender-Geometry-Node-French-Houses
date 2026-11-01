"""Read-only HouseOne dependency-graph and coordinate probe."""
import bpy,json,hashlib
from pathlib import Path
from collections import Counter
r=Path.cwd(); out=r/'tests/baking/phase4b';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'GeometryNodesFrenchHous.blend'))
o=bpy.data.objects['HouseOne']; d=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(d)
def mesh(m):
 m.calc_loop_triangles()
 return dict(vertices=len(m.vertices),faces=len(m.polygons),triangles=len(m.loop_triangles),materials=[x.name if x else None for x in m.materials],texspace_location=list(m.texspace_location),texspace_size=list(m.texspace_size),auto_texspace=m.use_auto_texspace,bounds=[[min(v.co[i] for v in m.vertices),max(v.co[i] for v in m.vertices)] for i in range(3)] if m.vertices else [],attributes=[(a.name,a.domain,a.data_type) for a in m.attributes])
instances=[]
for x in d.object_instances:
 if x.is_instance and x.parent and x.parent.original==o:
  instances.append(dict(object=x.object.original.name,parent=x.parent.original.name,instance_object=x.instance_object.original.name if x.instance_object else None,persistent_id=list(x.persistent_id),matrix=[list(row) for row in x.matrix_world],show_self=x.show_self,mesh=mesh(x.object.data) if x.object.type=='MESH' else None))
refs=[]
seen=set()
def nodes(g):
 if g.name in seen:return
 seen.add(g.name)
 for n in g.nodes:
  if n.type in ('OBJECT_INFO','COLLECTION_INFO','GROUP') or 'Attribute' in n.bl_idname or hasattr(n,'collection') or hasattr(n,'object'):
   refs.append(dict(group=g.name,node=n.name,type=n.bl_idname,subgroup=n.node_tree.name if n.type=='GROUP' else None,collection=n.collection.name if getattr(n,'collection',None) else None,object=n.object.name if getattr(n,'object',None) else None,inputs={s.name:str(s.default_value) for s in n.inputs if hasattr(s,'default_value')},links=[(s.name,l.from_node.name,l.from_socket.name) for s in n.inputs for l in s.links]))
  if n.type=='GROUP':nodes(n.node_tree)
for mod in o.modifiers:
 if mod.type=='NODES':nodes(mod.node_group)
bindings={}
for mod in o.modifiers:
 if mod.type=='NODES':
  for item in mod.node_group.interface.items_tree:
   if item.item_type=='SOCKET' and item.in_out=='INPUT':
    try:value=mod[item.identifier]
    except (KeyError,TypeError):value=getattr(item,'default_value',None)
    bindings[item.name]=str(value)
collections={name:[dict(object=x.name,type=x.type,matrix=[list(row) for row in x.matrix_world]) for x in bpy.data.collections[name].all_objects] for name in {v['collection'] for v in refs if v.get('collection')}}
seed=bpy.data.node_groups.get('GetPositionBasedSeed')
seed_graph=dict(nodes=[dict(name=n.name,type=n.bl_idname,operation=getattr(n,'operation',None)) for n in seed.nodes],links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in seed.links]) if seed else None
report=dict(referenced_collections=collections,position_seed_graph=seed_graph,modifier_interface_defaults_or_legacy_values=bindings,modifiers=[(m.name,m.type,m.node_group.name if m.type=='NODES' else None) for m in o.modifiers],blender=bpy.app.version_string,source_sha256=hashlib.sha256((r/'GeometryNodesFrenchHous.blend').read_bytes()).hexdigest(),object_matrix=[list(row) for row in o.matrix_world],original_mesh=mesh(o.data),evaluated_mesh=mesh(e.data),instances=instances,instance_counts=dict(Counter(x['object'] for x in instances)),references=refs)
(out/'probe.json').write_text(json.dumps(report,indent=2))
print('PROBE',json.dumps({k:v for k,v in report.items() if k not in ('instances','references')}),flush=True)
