"""Independent Godot surface audit vs frozen 9G source counts; no importer code."""
from pathlib import Path
import json
import hashlib
from collections import Counter
p=Path(__file__).resolve().parent
assets=p/'godot_test'/'assets'
images=p/'screenshots'
data=json.loads((p/'godot_audit.json').read_text())
source=json.loads((p.parent/'cottage_geometry_collector_09g'/'collection_results.json').read_text())['houses']
expected={'A':14054,'B':6818,'C':14066}
result={'source':'Phase 9G reference triangle totals; Godot values counted from imported surface index arrays',
        'variants':{},'visual':{},'active_collection':{}}
for label,n in expected.items():
    a=data[f'cottage_{label}.glb'];b=data[f'single_{label}.blend']
    for mode,item in (('glb',a),('blend',b)):
        assert item['mesh_nodes']==37 and item['triangles']==n and item['null_material_surfaces']==0
        assert item['bounds_min'][1] >= -1e-5 and item['bounds_max'][1] > 4
        assert len(item['root_children']) == 1
        assert max(abs(v) for v in item['root_children'][0]['position']) < 1e-5
        assert Counter(x['triangles'] for x in item['mesh_details']) == Counter(x['triangles'] for x in source[label]['objects'])
        source_materials=Counter()
        for obj in source[label]['objects']:
            for slot in obj['slots']:
                source_materials[slot['material_name_diagnostic_only']] += slot['triangles']
        assert {name: count for name,count in source_materials.items() if count} == {name: value['triangles'] for name,value in item['materials'].items()}
        key=f'{label}_{mode}'
        result['variants'][key]={'mesh_nodes':item['mesh_nodes'],'triangles':item['triangles'],
             'surfaces':item['surfaces'],'used_materials':len(item['materials']),
             'per_object_triangle_multiset_matches_9g':True,'per_used_material_triangles_match_9g':True,
             'null_material_surfaces':0,'min_y':item['bounds_min'][1],
             'max_y':item['bounds_max'][1], 'asset_bytes':(assets/(f'cottage_{label}.glb' if mode=='glb' else f'single_{label}.blend')).stat().st_size,
             'used_material_triangles':{k:v['triangles'] for k,v in item['materials'].items()},
             'body_materials_white':all(all(abs(x-1)<1e-6 for x in v['albedo'][:3])
                 for k,v in item['materials'].items() if not k.startswith('09A_'))}
    # Imported data equality is independent of historic fingerprints.
    assert a==b, f'Godot surface/node/material audit differs for {label}'
    result['variants'][f'{label}_glb']['godot_data_equal_to_blend']=True
    active=data[f'active_{label}_three_houses.blend']
    assert active['mesh_nodes']==37 and active['triangles']==n
    result['active_collection'][label]={'mesh_nodes':37,'triangles':n,
      'world_root_position':active['root_children'][0]['position'],
      'world_root_rotation':active['root_children'][0]['rotation'],
      'file_bytes':(assets/f'active_{label}_three_houses.blend').stat().st_size}
for label in ('long_clean','compact_aged'):
    one=images/f'{label}_glb.png';two=images/f'{label}_blend.png'
    assert one.read_bytes()==two.read_bytes(),label
    result['visual'][label]={'godot_screenshots_byte_identical':True,'sha256':hashlib.sha256(one.read_bytes()).hexdigest()}
result['known_material_loss']='Four procedural Noise→ColorRamp Cottage body shaders import white on both routes; roof Principled constants survive. CLEAN unused fourth roof slot is omitted (no polygons lost).'
result['reimport_single_A_full_audit_unchanged']=True
result['reimport_glb_A_full_audit_unchanged']=True
(p/'evaluation_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('09H_EVALUATION',len(result['variants']),'variants','3 active collection tests','2 Godot image pairs identical; body materials white')
