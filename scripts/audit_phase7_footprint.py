"""Read-only source / temporary controlled quad experiments, before 0.3 implementation."""
import bpy, importlib, json, math, hashlib, time, os, tomllib
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7'
M=os.environ.get('MBG_AUDIT_MODULE','bl_ext.mbg_variety_test.medieval_building_generator')
A=importlib.import_module(M+'.assets');E=importlib.import_module(M+'.exporter')
bpy.context.preferences.addons[M].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
assert bpy.ops.mbg.create_house()=={'FINISHED'}
o=bpy.context.active_object
report={'version':bpy.app.version_string,'source_sha256':hashlib.sha256((ROOT/'GeometryNodesFrenchHous.blend').read_bytes()).hexdigest(),
    'input_vertices':[list(v.co) for v in o.data.vertices],'input_attributes':[(a.name,a.data_type,a.domain) for a in o.data.attributes],
    'matrix':[list(row) for row in o.matrix_world],'graph':[],'samples':[]}
def value(v):
    return v.name if isinstance(v,bpy.types.ID) else list(v) if hasattr(v,'__len__') and not isinstance(v,str) else v

report['addon_version']=tomllib.loads((Path(importlib.import_module(M).__file__).parent/'blender_manifest.toml').read_text())['version']
baseline=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
report['original_direct_zero_area_polygons']=sum(p.area<1e-12 for p in baseline.polygons)
report['original_direct_polygons']=len(baseline.polygons)
o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
g=A.generator_modifier(o).node_group
report['space_and_spacing_nodes']=[dict(name=n.name,type=n.bl_idname,parent=n.parent.label if n.parent else '',
    inputs=[(s.name,str(s.default_value)) for s in n.inputs if hasattr(s,'default_value')],
    incoming=[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in g.links if l.to_node==n])
    for n in g.nodes if n.bl_idname in ('GeometryNodeTransform','GeometryNodeObjectInfo','GeometryNodeCurveToPoints','GeometryNodeResampleCurve')]
for n in g.nodes:
    if n.type=='FRAME' or n.bl_idname in ('GeometryNodeInputPosition','ShaderNodeSeparateXYZ','ShaderNodeMath','GeometryNodeBoundBox','GeometryNodeMeshLine','GeometryNodeResampleCurve','GeometryNodeDistributePointsOnFaces','GeometryNodeMeshToCurve','GeometryNodeExtrudeMesh'):
        report['graph'].append(dict(name=n.name,label=n.label,type=n.bl_idname,parent=n.parent.label if n.parent else '',
            operation=getattr(n,'operation',None),inputs=[(s.name,str(s.default_value)) for s in n.inputs if hasattr(s,'default_value')],
            incoming=[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in g.links if l.to_node==n]))
# Original Group Input connections: interface is not guessed from modifier keys.
report['axis_nodes']=[dict(name=n.name,type=n.bl_idname,parent=n.parent.label,
    operation=getattr(n,'operation',None),inputs=[(i,s.name,value(s.default_value)) for i,s in enumerate(n.inputs) if hasattr(s,'default_value')],
    incoming=[(l.from_node.name,l.from_socket.name,list(n.inputs).index(l.to_socket)) for l in g.links if l.to_node==n])
    for n in g.nodes if n.parent and n.parent.name in ('Frame.082','Frame.008','Frame.009','Frame.019','Frame.044')]
report['input_links']=[(l.from_socket.name,l.to_node.name,l.to_socket.name) for l in g.links if l.from_node.type=='GROUP_INPUT']
original=o.data
for label,width,depth in [('COMPACT',4,3.2),('NARROW',3.2,5),('WIDE',7,4),('MIN',3.2,3),('MAX',7,5),('THIN',2,3),('SHALLOW',4,2),('HUGE',9,6)]:
    mesh=bpy.data.meshes.new('Audit_'+label)
    mesh.from_pydata([(-depth/2,-width/2,0),(depth/2,-width/2,0),(-depth/2,width/2,0),(depth/2,width/2,0)],[],[(0,1,3,2)])
    o.data=mesh;o.update_tag();start=time.perf_counter();bpy.context.view_layer.update()
    expected,direct,instances=E.owned_counts(bpy.context,o)
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
    lo=[min(v.co[i] for v in data.vertices) for i in range(3)];hi=[max(v.co[i] for v in data.vertices) for i in range(3)]
    report['samples'].append(dict(name=label,width=width,depth=depth,triangles=sum(expected.values()),direct=direct,instances=instances,
        direct_bounds=[lo,hi],height=hi[2]-lo[2],seconds=time.perf_counter()-start,
        finite=all(math.isfinite(c) for v in data.vertices for c in v.co),
        direct_polygons=len(data.polygons),direct_zero_area_polygons=sum(p.area<1e-12 for p in data.polygons)))
    ev.to_mesh_clear()
    o.data=original;bpy.data.meshes.remove(mesh)
# Native duplication behavior, important before adding any automatic repair handlers.
for linked in (False,True):
    bpy.context.view_layer.objects.active=o
    for other in bpy.context.selected_objects:other.select_set(False)
    o.select_set(True)
    bpy.ops.object.duplicate(linked=linked)
    dupe=bpy.context.active_object
    report['duplicate_linked' if linked else 'duplicate_normal']=dict(self_reference=A.socket(A.generator_modifier(dupe),'Object').value==dupe,shared_mesh=dupe.data==o.data)
    bpy.data.objects.remove(dupe,do_unlink=True)
(OUT/'footprint_audit.json').write_text(json.dumps(report,indent=2))
print('PHASE7_AUDIT',json.dumps(report['samples']),report['duplicate_normal'],report['duplicate_linked'])
