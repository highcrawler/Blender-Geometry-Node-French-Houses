"""Re-export genuine Phase-6 library under 0.3, including its mirrored variant."""
import bpy,json
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7'
helpers={};code=(ROOT/'scripts/test_addon_export06.py').read_text()
exec(compile(code[:code.index('# Source is never opened')].replace('bl_ext.mbg_export_test','bl_ext.mbg_variety_test'),'phase6_verifier','exec'),helpers)
helpers['OUT']=OUT
baseline=ROOT/'tests/consolidation/runtime/sandbox/tests/addon/phase6'
reference=json.loads((baseline/'integration.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(baseline/'runtime/library.blend'))
reports={}
for name,key in [('Renamed / Castle : 03','house3'),('Library House 1','house1'),('Library House 5','house5'),('Library House 2','transformed_house2')]:
    obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
    result=helpers['checked_export'](obj,'phase6_regression_'+key)
    old=reference['exports'][key]
    assert result['triangles']==old['triangles'] and result['material_triangles']==old['material_triangles']
    if key!='transformed_house2':assert result['glb_sha256']==old['glb_sha256']
    reports[key]=dict(triangles=result['triangles'],polygon_bijection=result['polygon_bijection'],
        sha256=result['glb_sha256'],reference_sha256=old['glb_sha256'],source_scene_unchanged=True)
(OUT/'export_regression.json').write_text(json.dumps(dict(result='PASS',cases=reports),indent=2))
print('PHASE7_PHASE6_EXPORT_REGRESSION_PASS',json.dumps({k:v['triangles'] for k,v in reports.items()}))
