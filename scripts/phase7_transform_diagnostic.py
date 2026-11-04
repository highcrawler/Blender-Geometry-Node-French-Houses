"""Measure the transform round-trip that affected the mirrored rectangle fixture."""
import bpy,importlib,json
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7';M='bl_ext.mbg_variety_test.medieval_building_generator'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'runtime/presets.blend'))
o=bpy.data.objects['Wide'];o.rotation_euler.z=.47;o.scale=(-1.2,.8,1.1)
o.mbg_settings.width=6.6;o.mbg_settings.depth=4.2
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();matrix=o.evaluated_get(dg).matrix_world.copy()
report={'source_scale':list(o.scale),'source_rotation':list(o.rotation_euler),'cases':{}}
for label,assign in [('exact_channels',False),('matrix_roundtrip',True)]:
    clone=o.copy();clone.data=o.data.copy();clone.animation_data_clear();clone.parent=None;clone.constraints.clear()
    if assign:clone.matrix_world=matrix
    bpy.context.scene.collection.objects.link(clone);bpy.context.view_layer.update()
    m=clone.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
    report['cases'][label]={'scale':list(clone.scale),'rotation':list(clone.rotation_euler),
        'max_matrix_error':max(abs(m[i][j]-matrix[i][j]) for i in range(4) for j in range(4))}
    data=clone.data;bpy.data.objects.remove(clone,do_unlink=True);bpy.data.meshes.remove(data)
(OUT/'transform_diagnostic.json').write_text(json.dumps(report,indent=2))
assert report['cases']['exact_channels']['max_matrix_error']==0
print('TRANSFORM_DIAGNOSTIC',report)
