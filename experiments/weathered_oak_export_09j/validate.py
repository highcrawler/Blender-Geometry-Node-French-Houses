"""Independent Godot surface/material assertions against immutable Phase 9I GLB."""
import hashlib, json
from pathlib import Path
p=Path(__file__).resolve().parent
s=json.loads((p/'blender_audit.json').read_text())
g=json.loads((p/'godot_audit.json').read_text())
a=g['clay_reference_A.glb'];b=g['oak_constant_A.glb']
source=p.parents[0]/'wooden_roof_system_09f/three_owned_cottages.blend'
ref=p.parents[0]/'clay_material_export_09i/godot_test/assets/clay_constant_A.glb'
assert hashlib.sha256(source.read_bytes()).hexdigest()==s['source_sha256_before']==s['source_sha256_after']=='38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae'
assert hashlib.sha256(ref.read_bytes()).digest()==hashlib.sha256((p/'godot_test/assets/clay_reference_A.glb').read_bytes()).digest()
assert s['collector_reference']['matched_09g'] and s['geometry_same'] and s['source_in_memory_same'] and s['selection_and_collections_restored']
assert s['foreign_buildings_meshes_unchanged']==75 and s['source_material_nodes_values_links_unchanged']
assert sum(x['triangles'] for x in s['oak_meshes'])==264 and len(s['oak_meshes'])==22
assert a['mesh_nodes']==b['mesh_nodes']==37 and a['triangles']==b['triangles']==14054
assert a['surfaces']==b['surfaces']==39 and a['null_material_surfaces']==b['null_material_surfaces']==0
assert a['bounds_min']==b['bounds_min'] and a['bounds_max']==b['bounds_max']
assert a['root_children'][0]['position']==b['root_children'][0]['position']==[0,0,0]
assert a['root_children'][0]['rotation']==b['root_children'][0]['rotation']==[0,0,0]
assert a['root_children'][0]['scale']==b['root_children'][0]['scale']==[1,1,1]
assert sorted(x['triangles'] for x in a['mesh_details'])==sorted(x['triangles'] for x in b['mesh_details'])
old=a['materials']['08A_09F_A_weathered_oak'];oak=b['materials']['09J_A_weathered_oak_constant']
assert old['albedo']==[1,1,1,1]
assert (old['surfaces'],old['triangles'])==(oak['surfaces'],oak['triangles'])==(22,264)
assert oak['roughness']==s['roughness']==1 and oak['metallic']==s['metallic']==0

def linear_to_srgb(x):return 12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055
expected=[linear_to_srgb(x) for x in (.19,.125,.077)]
assert all(abs(x-y)<2e-5 for x,y in zip(oak['albedo'],expected))
assert a['materials'].pop('08A_09F_A_weathered_oak')['triangles']==264
assert b['materials'].pop('09J_A_weathered_oak_constant')['triangles']==264
assert a['materials']==b['materials']
assert a['materials']['09I_A_clay_constant']['albedo']==[0.715240895748138,0.649956464767456,0.565728425979614,1]
for name in ('08A_09F_A_stone','08A_09F_A_door'):
    assert a['materials'][name]['albedo']==[1,1,1,1]
assert sum(v['triangles'] for v in b['materials'].values())+264==14054
report={'result':'PASS','linear_oak':[.19,.125,.077],'expected_srgb_oak':expected,'godot_oak_albedo':oak['albedo'],
 'oak_surfaces':22,'oak_triangles':264,'clay_triangles':74,'total_triangles':14054,'roof_triangles':13692,'body_triangles':362,
 'bounds_min':b['bounds_min'],'bounds_max':b['bounds_max'],'source_sha256':s['source_sha256_after'],
 'unchanged_godot_materials':a['materials'],'reference_9i_glb_sha256':hashlib.sha256(ref.read_bytes()).hexdigest()}
(p/'material_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('09J_GODOT_PASS',expected,oak['albedo'])
