"""Independent process: saved renamed house, no asset-library access required."""
import bpy, json, hashlib
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase6'
namespace={}
code=(ROOT/'scripts/test_addon_export06.py').read_text()
exec(compile(code[:code.index('# Source is never opened')], 'export06_helpers', 'exec'),namespace)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'runtime/library.blend'))
report=json.loads((OUT/'integration.json').read_text())
expected=report['state_before_reload']
actual=json.loads(json.dumps(namespace['state']()))
removed={}
for key in expected['ids']:
    old=set(expected['ids'][key]);new=set(actual['ids'][key])
    assert not new-old
    removed[key]=sorted(old-new)
    assert old-new <= set(report['zero_user_ids'][key]), (key,removed[key])
    expected['ids'][key]=actual['ids'][key]
for name in removed['materials']:del expected['materials'][name]
for name in removed['objects']:expected['asset_transforms'].pop(name,None)
for name in removed['node_groups']:expected['group_references'].pop(name,None)
assert actual==expected, 'saved scene state differs (excluding Blender zero-user pruning)'
namespace['bpy'].context.preferences.addons[namespace['MODULE']].preferences.source_file='/missing/library.blend'
path=OUT/'runtime/library.blend';sha=hashlib.sha256(path.read_bytes()).hexdigest()
obj=bpy.context.active_object
assert obj.name=='Renamed / Castle : 03'
result=namespace['checked_export'](obj,'reloaded_house3')
assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
old=json.loads((OUT/'integration.json').read_text())['exports']['house3']
assert result['triangles']==old['triangles'] and result['glb_sha256']==old['glb_sha256']
(OUT/'reload.json').write_text(json.dumps(dict(result='PASS',saved_file_sha256=sha,
    source_unavailable=True,scene_identical=True,blender_pruned_zero_user_ids=removed,reexport=result),indent=2))
print('PHASE6_RELOAD_PASS', result['triangles'],result['glb_sha256'])
