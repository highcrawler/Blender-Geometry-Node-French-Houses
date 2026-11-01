"""Read-only shader dependency and original UV audit for HouseOne."""
import bpy, json
from pathlib import Path
obj=bpy.data.objects['HouseOne']
deps=bpy.context.evaluated_depsgraph_get()
mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
trees={}
def value(s):
    v=getattr(s,'default_value',None)
    return list(v) if hasattr(v,'__len__') else v if isinstance(v,(str,float,int,bool)) else str(v)
def scan(tree):
    if tree.name in trees: return
    trees[tree.name]={'nodes':[{'name':n.name,'type':n.bl_idname,'attribute':getattr(n,'attribute_name',None),'operation':getattr(n,'operation',None),'blend_type':getattr(n,'blend_type',None),'outputs':[{ 'name':s.name,'value':value(s)} for s in n.outputs],'inputs':[{ 'name':s.name,'value':value(s)} for s in n.inputs],'group':n.node_tree.name if n.type=='GROUP' else None} for n in tree.nodes], 'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in tree.links]}
    for n in tree.nodes:
        if n.type=='GROUP': scan(n.node_tree)
scan(bpy.data.materials['UpperFloorsPaint'].node_tree)
slot=next(i for i,m in enumerate(mesh.materials) if m and m.name=='UpperFloorsPaint')
polys=[p for p in mesh.polygons if p.material_index==slot]
uv={}
for layer in mesh.uv_layers:
    coords=[tuple(layer.data[i].uv) for p in polys for i in p.loop_indices]
    uv[layer.name]={'loops':len(coords),'unique_coordinates':len(set(coords)),'min':list(map(min,zip(*coords))),'max':list(map(max,zip(*coords))),'polygons':[[list(layer.data[i].uv) for i in p.loop_indices] for p in polys]}
report={'object_matrix':[list(r) for r in obj.matrix_world], 'shader_trees':trees,'uv':uv,'plaster_faces':len(polys),'plaster_vertices':[[list(mesh.vertices[i].co) for i in p.vertices] for p in polys],'seams':sum(e.use_seam for e in mesh.edges),'attributes':[(a.name,a.data_type,a.domain) for a in mesh.attributes]}
Path('tests/baking/phase4/source_audit.json').write_text(json.dumps(report,indent=2))
print('PHASE4_AUDIT',len(polys),[(k,{x:y for x,y in v.items() if x!='polygons'}) for k,v in uv.items()])

print('TEXSPACE_SOURCE',list(obj.data.texspace_location),list(obj.data.texspace_size),'EVAL',list(mesh.texspace_location),list(mesh.texspace_size))
