"""Validate Godot 4.7 Stone/Door imports against byte-identical Phase-9J A GLB."""
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
repo=p.parents[1]
s=json.loads((p/'blender_audit.json').read_text())
g=json.loads((p/'godot_audit.json').read_text())
a=g['oak_reference_A.glb'];b=g['stone_door_constant_A.glb']
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=repo/'experiments/wooden_roof_system_09f/three_owned_cottages.blend'
ref=repo/'experiments/weathered_oak_export_09j/godot_test/assets/oak_constant_A.glb'
assert h(source)==s['source_sha256_before']==s['source_sha256_after']=='38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae'
assert h(ref)==h(p/'godot_test/assets/oak_reference_A.glb')
assert s['collector_reference']['matched_09g'] and s['geometry_same'] and s['source_in_memory_same'] and s['selection_and_collections_restored']
assert s['source_material_nodes_values_links_unchanged'] and s['foreign_buildings_meshes_unchanged']==75
for key in ('stone','door'):
    shader=s[key]
    assert shader['node_types']==['BSDF_PRINCIPLED','OUTPUT_MATERIAL','TEX_COORD','TEX_NOISE','VALTORGB']
    assert shader['roughness']==1 and shader['metallic']==0 and shader['noise_scale']==5 and shader['noise_detail']==2
    assert shader['noise_vector_input']==['Texture Coordinate.Generated']
    assert sum(x['triangles'] for x in shader['meshes'])==12
assert a['mesh_nodes']==b['mesh_nodes']==37 and a['triangles']==b['triangles']==14054
assert a['surfaces']==b['surfaces']==39 and a['null_material_surfaces']==b['null_material_surfaces']==0
assert a['bounds_min']==b['bounds_min'] and a['bounds_max']==b['bounds_max']
assert a['root_children'][0]['position']==b['root_children'][0]['position']==[0,0,0]
assert a['root_children'][0]['rotation']==b['root_children'][0]['rotation']==[0,0,0]
assert a['root_children'][0]['scale']==b['root_children'][0]['scale']==[1,1,1]
assert sorted(x['triangles'] for x in a['mesh_details'])==sorted(x['triangles'] for x in b['mesh_details'])
old=a['materials'];new=b['materials']
expected_ref=json.loads((repo/'experiments/weathered_oak_export_09j/godot_audit.json').read_text())['oak_constant_A.glb']['materials']
assert old==expected_ref
for name in old.keys()-{'08A_09F_A_stone','08A_09F_A_door'}:assert old[name]==new[name],name
assert old['08A_09F_A_stone']['albedo']==old['08A_09F_A_door']['albedo']==[1,1,1,1]

def linear_to_srgb(x):return 12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055
colors={'stone':(.31,.29,.25),'door':(.25,.15,.085)}
checks={}
for key,linear in colors.items():
    material=new[f'09K_A_{key}_constant'];expected=[linear_to_srgb(x) for x in linear]
    assert all(abs(x-y)<2e-5 for x,y in zip(material['albedo'],expected))
    assert (material['surfaces'],material['triangles'],material['roughness'],material['metallic'])==(1,12,1,0)
    assert old[f'08A_09F_A_{key}']['triangles']==material['triangles']
    checks[key]={'linear_rgb':linear,'expected_srgb':expected,'godot_albedo':material['albedo'],'roughness':1,'metallic':0,'surfaces':1,'triangles':12}
assert len(new)==7 and sum(x['triangles'] for x in new.values())==14054
result={'result':'PASS','stone_and_door':checks,'reference_glb_sha256':h(ref),'source_sha256':h(source),
 'meshes':37,'surfaces':39,'triangles':14054,'roof_triangles':13692,'body_triangles':362,
 'clay_reference_identical':new['09I_A_clay_constant'],'oak_reference_identical':new['09J_A_weathered_oak_constant'],
 'unchanged_roof_materials':{k:v for k,v in new.items() if k.startswith('09A_')},
 'bounds_min':b['bounds_min'],'bounds_max':b['bounds_max'],'root':b['root_children'][0]}
(p/'material_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('09K_GODOT_PASS',checks,flush=True)
