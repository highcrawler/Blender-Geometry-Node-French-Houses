"""Blender: blender -b three_owned_cottages.blend -P this_file.py"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
from building import CollectorError, collect_building_geometry

OUT = Path(__file__).resolve().parent


def snapshot():
    """Saved scene plus all datablocks, selection and mesh/shader contents."""
    payload = (
        sorted((s.as_pointer(), s.name, tuple(c.as_pointer() for c in s.collection.children)) for s in bpy.data.scenes),
        sorted((c.as_pointer(), c.name, tuple(o.as_pointer() for o in c.objects),
                tuple(x.as_pointer() for x in c.children), c.users) for c in bpy.data.collections),
        sorted((o.as_pointer(), o.name, o.type, o.parent.as_pointer() if o.parent else None,
                tuple(c.as_pointer() for c in o.users_collection), tuple(tuple(r) for r in o.matrix_world),
                tuple(tuple(r) for r in o.matrix_basis), o.data.as_pointer() if o.data else None,
                tuple((s.link, s.material.as_pointer() if s.material else None) for s in o.material_slots),
                o.select_get()) for o in bpy.data.objects),
        sorted((m.as_pointer(), m.name, m.users,
                tuple(tuple(v.co) for v in m.vertices),
                tuple((tuple(p.vertices), p.material_index) for p in m.polygons),
                tuple(mat.as_pointer() if mat else None for mat in m.materials)) for m in bpy.data.meshes),
        sorted((m.as_pointer(), m.name, m.users, tuple(m.diffuse_color), m.use_nodes,
                tuple((n.type, tuple((inp.name, str(inp.default_value)) for inp in n.inputs if hasattr(inp,'default_value')))
                      for n in m.node_tree.nodes) if m.use_nodes else ()) for m in bpy.data.materials),
        bpy.context.view_layer.objects.active.as_pointer() if bpy.context.view_layer.objects.active else None,
        tuple(sorted(o.as_pointer() for o in bpy.context.selected_objects)),
        bpy.context.scene.as_pointer(),
    )
    return hashlib.sha256(repr(payload).encode()).hexdigest(), tuple(len(x) for x in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.collections))


def summary(label, r):
    return {
        'owner': label, 'root_name_diagnostic_only': r.building_root.name,
        'root_id': r.building_root.as_pointer(), 'collection_id': r.building_collection.as_pointer(),
        'body_count': len(r.body_objects), 'roof_count': len(r.roof_objects),
        'mesh_count': len(r.mesh_objects), 'triangles': r.triangles,
        'body_triangles': sum(x.triangles for x in r.records if x.role == 'body'),
        'roof_triangles': sum(x.triangles for x in r.records if x.role == 'roof'),
        'pivot_local': list(r.pivot_local), 'pivot_world': list(r.pivot_world),
        'root_world_matrix': [list(row) for row in r.building_root.matrix_world],
        'world_to_export_local': [list(row) for row in r.world_to_export_local],
        'materials_distinct': len(r.materials), 'diagnostics': list(r.diagnostics),
        'roof_parts': {part: sum(x.roof_part == part for x in r.records) for part in ('deck','shingles','ridge')},
        'objects': [
            {'name_diagnostic_only': x.obj.name, 'role': x.role, 'roof_part': x.roof_part,
             'mesh_id': x.mesh.as_pointer(), 'triangles': x.triangles,
             'matrix_local': [list(row) for row in x.matrix_local],
             'matrix_world': [list(row) for row in x.matrix_world],
             'export_local_matrix': [list(row) for row in x.export_local_matrix],
             'slots': [{'index': s.slot_index, 'material_name_diagnostic_only': s.material.name,
                        'material_id': s.material.as_pointer(), 'polygons': s.polygons,
                        'triangles': s.triangles} for s in x.materials]} for x in sorted(r.records, key=lambda rec: rec.obj.name)]
    }


def make_fixture():
    scene = bpy.data.scenes.new('09G_temp_isolated')
    owner = bpy.data.collections.new('09G_fixture_owner'); scene.collection.children.link(owner)
    roofcoll = bpy.data.collections.new('09G_fixture_roof'); owner.children.link(roofcoll)
    root = bpy.data.objects.new('09G_fixture_root', None); owner.objects.link(root)
    mat = bpy.data.materials.new('09G_fixture_material')
    objects = []
    for i in range(6):
        data = bpy.data.meshes.new('09G_fixture_data'); data.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)]); data.update()
        data.materials.append(mat)
        obj = bpy.data.objects.new('09G_fixture_part',data)
        (owner if i == 0 else roofcoll).objects.link(obj); obj.parent = root
        if i:
            obj['role'] = 'roof'; obj['roof_part'] = ('deck','deck','shingles','ridge','ridge')[i-1]
        objects.append(obj)
    return scene, owner, roofcoll, root, objects, mat


def discard_fixture(scene):
    # Only IDs created in the temporary isolated scene. No source-scene edits.
    collections = list(scene.collection.children)
    for coll in collections:
        for c in list(coll.children):
            for ob in list(c.objects):
                data = ob.data if ob.type == 'MESH' else None
                bpy.data.objects.remove(ob, do_unlink=True)
                if data and data.users == 0: bpy.data.meshes.remove(data)
            coll.children.unlink(c); bpy.data.collections.remove(c)
        for ob in list(coll.objects):
            data = ob.data if ob.type == 'MESH' else None
            bpy.data.objects.remove(ob, do_unlink=True)
            if data and data.users == 0: bpy.data.meshes.remove(data)
        scene.collection.children.unlink(coll); bpy.data.collections.remove(coll)
    bpy.data.scenes.remove(scene)
    for mat in list(bpy.data.materials):
        if mat.name.startswith('09G_fixture_') and mat.users == 0: bpy.data.materials.remove(mat)


def expect(code, fn):
    try: fn()
    except CollectorError as exc:
        assert exc.code == code, (code, exc.code, str(exc))
        return code
    raise AssertionError('expected ' + code)


before, counts = snapshot()
scene = bpy.context.scene
# Test fixtures are selected by documented root positions, not by collector logic.
houses = {}
for coll in scene.collection.children:
    roots = [o for o in coll.objects if o.type == 'EMPTY' and o.parent is None]
    if len(roots) == 1:
        pos = tuple(round(float(x), 5) for x in roots[0].location)
        key = {(0.0,0.0,0.0): 'A', (35.0,12.0,0.0): 'B', (-15.0,8.0,0.0): 'C'}[pos]
        houses[key] = (roots[0],coll)
assert set(houses) == {'A','B','C'}
results = {}
for label in ('A','B','C'):
    root, coll = houses[label]
    results[label] = collect_building_geometry(root, coll)
    r=results[label]
    assert (len(r.body_objects),len(r.roof_objects),len(r.mesh_objects)) == (32,5,37)
    assert r.pivot_local == Vector((0,0,0)) and (r.pivot_world-root.location).length < 1e-7
    for rec in r.records:
        for vert in (rec.mesh.vertices[0].co, rec.mesh.vertices[-1].co):
            assert ((r.building_root.matrix_world @ (rec.export_local_matrix @ vert)) -
                    (rec.matrix_world @ vert)).length < 1e-5
        assert (rec.export_local_matrix @ Vector((0,0,0,1))).w == 1
    assert sum(sum(s.triangles for s in rec.materials) for rec in r.records) == r.triangles
    assert sum(sum(len(p.vertices)-2 for p in rec.mesh.polygons) for rec in r.records) == r.triangles
    assert all(sum(s.polygons for s in rec.materials) == len(rec.mesh.polygons) for rec in r.records)
    assert all(not rec.obj.modifiers and rec.obj.instance_type == 'NONE' for rec in r.records)
assert [results[x].triangles for x in ('A','B','C')] == [14054,6818,14066]
assert abs(results['C'].building_root.rotation_euler.z - .45) < 1e-6
for a in results:
    for b in results:
        if a != b:
            assert set(results[a].mesh_objects).isdisjoint(results[b].mesh_objects)
            assert set(rec.mesh for rec in results[a].records).isdisjoint(rec.mesh for rec in results[b].records)
            assert set(results[a].materials).isdisjoint(results[b].materials)
assert all(len(results[x].materials) == 8 for x in results)
assert sum(1 for s in next(rec for rec in results['A'].records if rec.roof_part == 'shingles').materials
           if s.slot_index == 3 and s.triangles == 0) == 1
assert tuple(collect_building_geometry(*houses[x]).triangles for x in ('C','A','B')) == (14066,14054,6818)
assert snapshot() == (before,counts), 'collector modified saved reference scene'
negative = {}
negative['missing_root'] = expect('ROOT_INVALID', lambda: collect_building_geometry(None,houses['A'][1]))
negative['wrong_root_type'] = expect('ROOT_INVALID', lambda: collect_building_geometry(results['A'].mesh_objects[0],houses['A'][1]))
negative['wrong_collection'] = expect('ROOT_COLLECTION',lambda: collect_building_geometry(houses['A'][0],houses['B'][1]))
for key in ('foreign_mesh','external_child','wrong_roof_parent','missing_roof','multiple_collections',
            'shared_collection','invalid_transform','shared_mesh','shared_material','missing_material',
            'modifier','constraint','instance'):
    temp, owner, roofcoll, root, objects, mat = make_fixture()
    try:
        assert collect_building_geometry(root,owner).triangles == 6
        if key == 'foreign_mesh':
            foreign = bpy.data.objects.new('09G_foreign',bpy.data.meshes.new('09G_foreign_data'))
            owner.objects.link(foreign)  # not parented: ownership conflict
            code = 'OBJECT_PARENT'
        elif key == 'external_child':
            extra=bpy.data.collections.new('09G_extra');temp.collection.children.link(extra)
            foreign=bpy.data.objects.new('09G_foreign',bpy.data.meshes.new('09G_foreign_data'))
            extra.objects.link(foreign);foreign.parent=root;code='EXTERNAL_CHILD'
        elif key == 'wrong_roof_parent': objects[1].parent=None; code='OBJECT_PARENT'
        elif key == 'missing_roof':
            doomed=objects.pop(); data=doomed.data; bpy.data.objects.remove(doomed,do_unlink=True)
            bpy.data.meshes.remove(data); code='ROOF_INCOMPLETE'
        elif key == 'multiple_collections':
            extra=bpy.data.collections.new('09G_extra'); temp.collection.children.link(extra)
            extra.objects.link(objects[1]); code='OBJECT_COLLECTION'
        elif key == 'shared_collection':
            extra=bpy.data.collections.new('09G_extra');temp.collection.children.link(extra)
            extra.children.link(roofcoll);code='COLLECTION_SHARED'
        elif key == 'invalid_transform':root.location.x=float('nan');code='ROOT_TRANSFORM'
        elif key in ('shared_mesh','shared_material'):
            extra=bpy.data.collections.new('09G_extra'); temp.collection.children.link(extra)
            if key == 'shared_mesh': data=objects[1].data;code='MESH_SHARED'
            else:
                data=bpy.data.meshes.new('09G_foreign_data');data.from_pydata([(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)])
                data.materials.append(mat);code='MATERIAL_SHARED'
            foreign=bpy.data.objects.new('09G_foreign',data);extra.objects.link(foreign)
        elif key == 'missing_material':objects[1].data.materials.clear();code='MATERIAL_INDEX'
        elif key == 'modifier':objects[1].modifiers.new('09G_unsupported','SUBSURF');code='MODIFIER_UNSUPPORTED'
        elif key == 'constraint':objects[1].constraints.new('COPY_LOCATION');code='EVALUATION_UNSUPPORTED'
        else:objects[1].instance_type='VERTS';code='INSTANCE_UNSUPPORTED'
        negative[key] = expect(code,lambda:collect_building_geometry(root,owner))
    finally:
        # Drop extra temporary objects and collections before the fixture teardown.
        for coll in list(temp.collection.children):
            if coll != owner:
                for ob in list(coll.objects):
                    data=ob.data if ob.type == 'MESH' else None
                    bpy.data.objects.remove(ob,do_unlink=True)
                    if data and data.users == 0: bpy.data.meshes.remove(data)
                for child in list(coll.children): coll.children.unlink(child)
                temp.collection.children.unlink(coll);bpy.data.collections.remove(coll)
        for ob in list(owner.objects):
            if ob.name.startswith('09G_foreign'):
                data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
                if data and data.users==0:bpy.data.meshes.remove(data)
        discard_fixture(temp)
    assert snapshot() == (before,counts), 'negative case left a scene/datablock change: ' + key
# Renaming cannot affect ownership. Do this in another isolated fixture.
temp, owner, roofcoll, root, objects, mat = make_fixture()
try:
    root.name='completely_arbitrary';roofcoll.name='not_roof';objects[1].name='wall_looking_name'
    assert collect_building_geometry(root,owner).triangles == 6
    negative['rename_is_inert']='PASS'
finally:discard_fixture(temp)
assert snapshot() == (before,counts)
report = {'blender': bpy.app.version_string, 'status': 'PASS', 'reference_scene': 'three_owned_cottages.blend',
          'houses': {k:summary(k,results[k]) for k in ('A','B','C')}, 'negative_tests':negative,
          'read_only': {'before_sha256':before,'after_sha256':snapshot()[0],'counts':counts,
                        'unchanged':snapshot() == (before,counts)},
          'collection_order_independent':True,'no_export_performed':True}
OUT.joinpath('collection_results.json').write_text(json.dumps(report,indent=2)+'\n')
print('09G_PASS', [(k,report['houses'][k]['triangles']) for k in ('A','B','C')],negative,'read_only',report['read_only']['unchanged'])
