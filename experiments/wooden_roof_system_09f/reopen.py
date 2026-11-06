"""Load saved 9F scene in Blender 5.2.2 and verify real persisted ownership.
blender -b experiments/wooden_roof_system_09f/three_owned_cottages.blend \
    -P experiments/wooden_roof_system_09f/reopen.py
"""
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parent
record=json.loads((root/'ownership.json').read_text())['houses']
source=(root.parent/'wooden_roof_system_09b'/'audit.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='hash_objects')
env=dict(hashlib=hashlib)
exec(compile(ast.Module(body=[node],type_ignores=[]),str(root/'reopen.py'),'exec'),env)
hash_objects=env['hash_objects']
bpy.context.view_layer.update()
roots=[];roof_collections=[];mesh_ids=[];material_ids=[]
for label,entry in record.items():
    collection=bpy.data.collections.get(entry['collection'])
    roof=bpy.data.collections.get(entry['roof_collection'])
    owner=bpy.data.objects.get(entry['root'])
    assert collection and roof and owner and roof.name in collection.children
    assert tuple(owner.users_collection)==(collection,) and owner.type=='EMPTY'
    assert tuple(owner.location)==tuple(entry['root_location'])
    assert abs(owner.rotation_euler.z-entry['root_z_rotation'])<1e-7
    assert len(roof.objects)==entry['roofs']==5
    body=[o for o in collection.objects if o!=owner]
    assert len(body)==entry['bodies']
    assert all(o.type=='MESH' and o.parent==owner and tuple(o.users_collection)==(roof,)
               and o.get('role')=='roof' and o.data and all(m for m in o.data.materials)
               for o in roof.objects)
    assert all(o.type=='MESH' and o.parent==owner and tuple(o.users_collection)==(collection,)
               and o.data and all(m for m in o.data.materials) for o in body)
    assert hash_objects(roof.objects)==entry['roof_hash']
    assert hash_objects(body)==entry['body_hash']
    shingles=next(o for o in roof.objects if o.get('roof_part')=='shingles')
    assert [list(m.diffuse_color) for m in shingles.data.materials]==entry['roof_material_colors']
    assert hashlib.sha256(bytes(f.material_index for f in shingles.data.polygons)).hexdigest()==entry['face_material_sha256']
    for ob in [*roof.objects,*body]:
        assert all(math.isfinite(x) for v in ob.data.vertices for x in v.co)
        assert (ob.matrix_world@ob.data.vertices[0].co -
                owner.matrix_world@(ob.matrix_basis@ob.data.vertices[0].co)).length<1e-5
        mesh_ids.append(ob.data.as_pointer())
    material_ids.extend(m.as_pointer() for m in shingles.data.materials)
    roots.append(owner);roof_collections.append(roof)
assert len({o.as_pointer() for o in roots})==3
assert len({c.as_pointer() for c in roof_collections})==3
assert len(set(mesh_ids))==len(mesh_ids)
assert len(set(material_ids))==len(material_ids)
(root/'reopen_result.json').write_text(json.dumps(dict(blender=bpy.app.version_string,
    saved_scene_reloaded=True,houses=list(record),roof_meshes=15,
    unique_mesh_ids=len(set(mesh_ids)),unique_roof_material_ids=len(set(material_ids)),
    local_hashes_and_material_slots_identical=True),indent=2)+'\n')
print('09F_REOPEN PASS',len(record),'independent buildings',flush=True)
