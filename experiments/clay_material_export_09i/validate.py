import json, math
from pathlib import Path
p=Path(__file__).resolve().parent
s=json.loads((p/'blender_audit.json').read_text())
g=json.loads((p/'godot_audit.json').read_text())
a=g['baseline_A.glb'];b=g['clay_constant_A.glb']
assert s['source_sha256_before']==s['source_sha256_after']=='38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae'
assert s['geometry_same'] and s['source_in_memory_same'] and s['selection_and_collections_restored']
assert a['mesh_nodes']==b['mesh_nodes']==37 and a['triangles']==b['triangles']==14054
assert a['surfaces']==b['surfaces']==39 and a['null_material_surfaces']==b['null_material_surfaces']==0
assert a['bounds_min']==b['bounds_min'] and a['bounds_max']==b['bounds_max']
assert a['root_children'][0]['position']==b['root_children'][0]['position']==[0,0,0]
assert a['root_children'][0]['rotation']==b['root_children'][0]['rotation']==[0,0,0]
assert a['root_children'][0]['scale']==b['root_children'][0]['scale']==[1,1,1]
assert all(abs(x-y)<1e-6 for x,y in zip(a['materials']['08A_09F_A_clay']['albedo'],[1]*4))
clay=b['materials']['09I_A_clay_constant']
def linear_to_srgb(x):return 12.92*x if x <= .0031308 else 1.055*x**(1/2.4)-.055
expected=[linear_to_srgb(x) for x in (.47,.38,.28)]
assert all(abs(x-y)<2e-5 for x,y in zip(clay['albedo'],expected))
assert clay['surfaces']==8 and clay['triangles']==74 and clay['roughness']==1 and clay['metallic']==0
assert a['materials'].pop('08A_09F_A_clay')['triangles']==74
assert b['materials'].pop('09I_A_clay_constant')['triangles']==74
assert a['materials']==b['materials']
assert sorted(x['triangles'] for x in a['mesh_details'])==sorted(x['triangles'] for x in b['mesh_details'])
assert sum(m['triangles'] for m in b['materials'].values())+74==14054
report={'technical_assertions':'PASS','linear_input':[.47,.38,.28], 'expected_srgb':expected,'godot_albedo':clay['albedo'], 'clay_surfaces':8,'clay_triangles':74,'total_triangles':14054,'roof_triangles':13692,'body_triangles':362,'bounds_y':[b['bounds_min'][1],b['bounds_max'][1]],'roof_and_other_materials_unchanged':True,'source_sha256':s['source_sha256_after']}
(p/'material_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('09I_GODOT_PASS',report)
