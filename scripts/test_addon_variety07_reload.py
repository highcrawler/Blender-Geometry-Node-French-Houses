"""Separate process: serialized preset/custom dimensions + GN + repeat export."""
import bpy, json, importlib
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7'
namespace={};code=(ROOT/'scripts/test_addon_variety07.py').read_text()
exec(compile(code[:code.index('bpy.context.preferences.addons[M]')],'variety_helpers','exec'),namespace)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'runtime/custom.blend'))
expected=json.loads((OUT/'integration.json').read_text())['saved']
actual={name:namespace['signature'](bpy.data.objects[name]) for name in expected}
assert actual==expected
b=bpy.data.objects['Narrow custom renamed']
assert b.mbg_settings.shape=='CUSTOM' and abs(b.mbg_settings.width-4.4)<1e-5 and b.mbg_settings.depth==5
assert bpy.data.objects['Compact'].mbg_settings.shape=='COMPACT' and bpy.data.objects['Wide'].mbg_settings.shape=='WIDE'
bpy.context.view_layer.objects.active=b
result=namespace['checked_export'](b,'custom_reload')
addon=importlib.import_module(namespace['M']);addon.unregister();addon.register()
assert {name:namespace['signature'](bpy.data.objects[name]) for name in expected}==expected
(OUT/'reload.json').write_text(json.dumps(dict(result='PASS',all_input_and_evaluated_signatures_identical=True,
    custom_width=b.mbg_settings.width,custom_depth=b.mbg_settings.depth,preset=b.mbg_settings.shape,
    export=result,registration_cycle=True),indent=2))
print('PHASE7_RELOAD_PASS',result['triangles'])
