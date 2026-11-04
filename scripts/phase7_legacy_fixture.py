"""Run with the ZIP-installed 0.2.0 in the isolated legacy profile, never 0.3.0."""
import bpy, importlib, json, hashlib
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7/runtime'
MODULE='bl_ext.mbg_legacy_test.medieval_building_generator'
E=importlib.import_module(MODULE+'.exporter');A=importlib.import_module(MODULE+'.assets')
bpy.context.preferences.addons[MODULE].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
houses=[]
for i in range(2):
    bpy.context.scene.cursor.location=(i*15,-i*10,0)
    bpy.ops.mbg.create_house();obj=bpy.context.active_object;obj.name=f'Legacy 0.2 House {i+1}'
    obj.mbg_settings.seed=17+i;obj.mbg_settings.floors=2+i
    obj.mbg_settings.roof_color=(.12,.25,.4,1);obj.mbg_settings.paint_color=(.6,.4,.2,1)
    houses.append(obj)
bpy.context.view_layer.objects.active=houses[0]
assert 'mbg_footprint_version' not in houses[0]
result=E.export_house(bpy.context,houses[0],OUT/'legacy_reference.glb',overwrite=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'legacy02.blend'))
result['sha256']=hashlib.sha256((OUT/'legacy_reference.glb').read_bytes()).hexdigest()
result['input_vertices']=[list(v.co) for v in houses[0].data.vertices]
(OUT.parent/'legacy02_reference.json').write_text(json.dumps(result,indent=2))
print('LEGACY_02_FIXTURE_PASS',result['triangles'],result['sha256'])
