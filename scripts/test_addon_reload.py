"""Independent Blender-process save/reload verification; does not read the library."""
import bpy, importlib, json, hashlib
from pathlib import Path
ROOT = Path.cwd()
OUT = ROOT/'tests/addon/phase5'
# Reuse the fingerprint functions without executing integration setup.
source = (ROOT/'scripts/test_addon_mvp.py').read_text()
namespace = {}
exec(source[:source.index("bpy.ops.object.select_all(action='SELECT')")], namespace)
assets = namespace['assets']
bpy.ops.wm.open_mainfile(filepath=str(OUT/'runtime/three_houses.blend'))
namespace['prefs'].source_file = str(OUT/'missing-source.blend')
expected = json.loads((OUT/'integration.json').read_text())['saved']
actual = {o.name: dict(signature=namespace['signature'](o), values=namespace['values'](o))
          for o in bpy.context.scene.objects if o.get(assets.HOUSE_TAG)}
# JSON-normalize tuples for comparison.
actual = json.loads(json.dumps(actual))
assert actual == expected
module = importlib.import_module(namespace['MODULE'])
module.unregister()
module.register()
assert namespace['values'](bpy.data.objects['Medieval House.001']) == expected['Medieval House.001']['values']
bpy.data.objects['Medieval House.001'].mbg_settings.floors = 4
assert namespace['signature'](bpy.data.objects['Medieval House.001']) != expected['Medieval House.001']['signature']
report = {'result':'PASS', 'independent_process':True, 'source_config_missing':True,
          'saved_values_and_evaluation_identical': True, 'reregister_and_live_edit': True,
          'source_sha256':hashlib.sha256((ROOT/'GeometryNodesFrenchHous.blend').read_bytes()).hexdigest()}
(OUT/'reload.json').write_text(json.dumps(report,indent=2))
print('MVP_RELOAD_PASS',report)
