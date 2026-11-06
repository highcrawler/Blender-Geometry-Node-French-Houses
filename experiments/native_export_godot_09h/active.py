"""Change only active owner collection in a disposable loaded 3-house scene."""
import os
from pathlib import Path
import bpy
key=os.environ.get('H_TARGET','B')
pos={'B':(35.,12.,0.),'C':(-15.,8.,0.)}[key]
owner=next(c for c in bpy.context.scene.collection.children
           if any(o.type=='EMPTY' and tuple(round(v,3) for v in o.location)==pos for o in c.objects))
bpy.context.view_layer.active_layer_collection=next(c for c in bpy.context.view_layer.layer_collection.children if c.collection==owner)
out=Path(__file__).resolve().parent/'godot_test'/'assets'/f'active_{key}_three_houses.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('09H_ACTIVE',key,out.stat().st_size,flush=True)
