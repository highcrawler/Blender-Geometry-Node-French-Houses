"""Load a genuine 0.2-created scene under 0.3; no inferred migration on load."""
import bpy,json,hashlib,importlib
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7'
namespace={};code=(ROOT/'scripts/test_addon_variety07.py').read_text()
exec(compile(code[:code.index('bpy.context.preferences.addons[M]')],'variety_helpers','exec'),namespace)
F=namespace['F'];E=namespace['E'];A=namespace['A']
bpy.ops.wm.open_mainfile(filepath=str(OUT/'runtime/legacy02.blend'))
obj=bpy.data.objects['Legacy 0.2 House 1'];other=bpy.data.objects['Legacy 0.2 House 2']
bpy.context.view_layer.objects.active=obj
before=namespace['signature'](obj);other_before=namespace['signature'](other)
assert F.VERSION_KEY not in obj and not F.controlled(obj) and obj.mbg_settings.shape=='CUSTOM'
assert before['vertices']==json.loads((OUT/'legacy02_reference.json').read_text())['input_vertices']
# Even direct dimension-property access cannot silently reshape an old authored footprint.
obj.mbg_settings.width=6
assert namespace['signature'](obj)==before
addon=importlib.import_module(namespace['M']);addon.unregister();addon.register()
assert namespace['signature'](obj)==before and F.VERSION_KEY not in obj
file_hash=hashlib.sha256((OUT/'runtime/legacy02.blend').read_bytes()).hexdigest()
result=namespace['checked_export'](obj,'legacy03_unmodified')
old=json.loads((OUT/'legacy02_reference.json').read_text())
assert result['glb_sha256']==old['sha256']
assert hashlib.sha256((OUT/'runtime/legacy02.blend').read_bytes()).hexdigest()==file_hash
# Explicit conversion only; original input datablock survives untouched.
old_data=obj.data;old_vertices=[list(v.co) for v in old_data.vertices];matrix=obj.matrix_world.copy()
values=before['values']
assert bpy.ops.mbg.activate_rectangle()=={'FINISHED'}
assert obj.data!=old_data and old_vertices==[list(v.co) for v in old_data.vertices]
namespace['assert_quad'](obj)
assert obj.matrix_world==matrix and namespace['signature'](obj)['values']==values
assert namespace['signature'](other)==other_before
assert obj.mbg_settings.shape=='CUSTOM'
obj.mbg_settings.shape='NARROW'
assert obj.mbg_settings.shape=='NARROW'
converted=namespace['checked_export'](obj,'legacy_explicit_rectangle')
report=dict(result='PASS',loaded_without_geometry_changes=True,no_schema_inserted_on_load=True,
    readonly_legacy_dimensions=True,old_scene_file_unchanged=True,legacy_export_sha256=result['glb_sha256'],
    old_version_export_sha256=old['sha256'],explicit_conversion_only=True,old_mesh_preserved=True,
    other_legacy_house_unchanged=True,converted_export=converted)
(OUT/'legacy.json').write_text(json.dumps(report,indent=2))
print('PHASE7_LEGACY_PASS',result['glb_sha256'])
