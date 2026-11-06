"""Save a disposable one-owner .blend from the immutable 9F scene; H_TARGET=B or C."""
import os
from pathlib import Path
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from building import collect_building_geometry
label=os.environ.get('H_TARGET','B')
assert label in ('B','C')
position={'B':(35,12,0),'C':(-15,8,0)}[label]
owner=next(c for c in bpy.context.scene.collection.children
           if any(o.type=='EMPTY' and tuple(round(v,3) for v in o.location)==position for o in c.objects))
root=next(o for o in owner.objects if o.type=='EMPTY')
record=collect_building_geometry(root,owner)
for ob in list(bpy.data.objects):
    if ob not in set(record.mesh_objects)|{root}:bpy.data.objects.remove(ob,do_unlink=True)
for coll in list(bpy.context.scene.collection.children):
    if coll!=owner:bpy.data.collections.remove(coll,do_unlink=True)
root.location=Vector((0,0,0));root.rotation_euler.z=0
bpy.context.view_layer.update()
bpy.context.view_layer.active_layer_collection=next(c for c in bpy.context.view_layer.layer_collection.children if c.collection==owner)
out=Path(__file__).resolve().parent/'godot_test'/'assets'/f'single_{label}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('09H_SINGLE',label,record.triangles,out.stat().st_size,flush=True)
