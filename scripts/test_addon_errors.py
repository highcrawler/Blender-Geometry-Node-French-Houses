"""Exercise user-facing operator failures and original-library write guard."""
import bpy, json, hashlib
from pathlib import Path
ROOT = Path.cwd()
OUT = ROOT/'tests/addon/phase5'
MODULE = 'bl_ext.mbg_test.medieval_building_generator'
prefs = bpy.context.preferences.addons[MODULE].preferences
results = {}


def cancelled(label, path, expected):
    prefs.source_file = str(path)
    before = set(bpy.data.objects)
    try:
        result = bpy.ops.mbg.create_house()
        assert result == {'CANCELLED'}
        message = 'CANCELLED'
    except RuntimeError as exc:
        # bpy.ops translates ERROR reports to RuntimeError for Python callers;
        # Blender's UI presents them as a normal user-facing error report.
        message = str(exc)
    assert set(bpy.data.objects) == before
    assert expected in message, (label, message)
    results[label] = message


cancelled('no_configuration', '', 'zuerst die IRCSS-Quelldatei')
cancelled('missing_file', OUT/'missing.blend', 'vorhandene IRCSS-Quelldatei')
cancelled('wrong_type', ROOT/'README.md', 'vorhandene IRCSS-Quelldatei')
cancelled('missing_node_group', OUT/'runtime/wrong_library.blend', 'Node-Gruppe GenerateHouse nicht')
cancelled('corrupt_file', OUT/'runtime/corrupt.blend', 'Assets konnten nicht geladen werden')
source = ROOT/'GeometryNodesFrenchHous.blend'
old_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
cancelled('source_open_as_working_scene', source, 'neue Szene öffnen')
assert hashlib.sha256(source.read_bytes()).hexdigest() == old_hash
(OUT/'errors.json').write_text(json.dumps(results,indent=2))
print('MVP_ERRORS_PASS',json.dumps(results))
