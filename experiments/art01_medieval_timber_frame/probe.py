"""Read-only measurement of the saved 9F A cottage; no .blend save."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;source=Path(bpy.data.filepath)
assert source.name=='three_owned_cottages.blend'
owner=next(c for c in bpy.context.scene.collection.children if any(o.type=='EMPTY' and o.parent is None and tuple(round(v,3) for v in o.location)==(0,0,0) for o in c.objects))
root=next(o for o in owner.objects if o.type=='EMPTY' and o.parent is None)
objects=sorted((o for o in owner.all_objects if o.type=='MESH'),key=lambda o:o.name)
assert len(objects)==37
sys.path.insert(0,str(P.parents[1]));sys.dont_write_bytecode=True
from building import collect_building_geometry
c=collect_building_geometry(root,owner)
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'root_position':list(root.matrix_world.translation),'collector_triangles':c.triangles,'collector_meshes':len(c.mesh_objects),'objects':{}}
for o in objects:
    verts=[o.matrix_world @ v.co for v in o.data.vertices]
    mins=[min(v[k] for v in verts) for k in range(3)];maxs=[max(v[k] for v in verts) for k in range(3)]
    report['objects'][o.name]={'world_min':mins,'world_max':maxs,'center':list(o.matrix_world.translation),'world_long_axis':list((o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':[m.name for m in o.data.materials if m],'role':o.get('role','body')}
(P/'baseline_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print('ART01_PROBE',report['source_sha256'],'objects',len(objects),'triangles',c.triangles)
