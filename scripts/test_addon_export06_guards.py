"""Negative selection / input-identity guards on the saved five-house library."""
import bpy, json
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase6'
namespace={}
code=(ROOT/'scripts/test_addon_export06.py').read_text()
exec(compile(code[:code.index('# Source is never opened')],'export06_helpers','exec'),namespace)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'runtime/library.blend'))
E=namespace['E'];A=namespace['A'];state=namespace['state']
before=state();active=bpy.context.active_object;result={}
result['dirty_before_export']=bpy.data.is_dirty
E.export_house(bpy.context,active,OUT/'runtime/dirty_check.glb',overwrite=True)
result['dirty_after_export']=bpy.data.is_dirty
assert state()==before
bpy.context.view_layer.objects.active=None
assert not bpy.ops.mbg.export_house.poll()
result['no_active_poll']=True
foreign=next(o for o in bpy.context.scene.objects if not o.get(A.HOUSE_TAG))
bpy.context.view_layer.objects.active=foreign
assert not bpy.ops.mbg.export_house.poll()
result['foreign_poll']=True
bpy.context.view_layer.objects.active=active
assert bpy.ops.mbg.export_house.poll()
# Wrong self-reference is rejected instead of accidentally exporting another house.
other=next(o for o in bpy.context.scene.objects if o.get(A.HOUSE_TAG) and o!=active)
s=A.socket(A.generator_modifier(active),'Object')
s.value=other
try:
    E.export_house(bpy.context,active,OUT/'runtime/forbidden.glb')
except E.ExportError as exc:
    assert 'Object-Eingang' in str(exc)
    result['wrong_house_object_input']=str(exc)
else:raise AssertionError('Cross-house self reference accepted')
finally:s.value=active;active.update_tag()
assert not (OUT/'runtime/forbidden.glb').exists()
bpy.ops.object.mode_set(mode='EDIT')
assert not bpy.ops.mbg.export_house.poll()
bpy.ops.object.mode_set(mode='OBJECT')
result['edit_mode_poll']=True
assert state()==before
(OUT/'guards.json').write_text(json.dumps(result,indent=2))
print('PHASE6_GUARDS_PASS',result)
