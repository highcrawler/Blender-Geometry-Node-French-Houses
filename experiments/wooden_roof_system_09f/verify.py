"""Phase 9F: Blender 5.2.2 full 9E/9D regression and owner/transform tests.
blender -b -t 4 -P experiments/wooden_roof_system_09f/verify.py
"""
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sys.path[:0]=[str(PROJECT),str(PROJECT/'experiments'/'cottage_generator_08a'),str(HERE)]
from cottage import Cottage
from cottage_adapter import build_cottage
from roof.wooden_rect import RoofSpec,build_rectangular_roof
import roof.wooden_rect as module
assert bpy.app.version[:2]==(5,2)
B=PROJECT/'experiments'/'wooden_roof_system_09b'
C=PROJECT/'experiments'/'wooden_roof_system_09c'
D=PROJECT/'experiments'/'wooden_roof_system_09d'
config={**json.loads((B/'config.json').read_text()),**json.loads((C/'config.json').read_text())}
expected=json.loads((D/'measurements.json').read_text())['matrix']
# Reuse the unchanged 9B physical audit with the 9D test-only correction to
# identify actual rows. No threshold/mesh test is copied or loosened.
src=(B/'audit.py').read_text()
names={'roof_objects','hash_objects','volume','geometry_audit'}
nodes=[n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in names]
class ActualRows(ast.NodeTransformer):
    def visit_Assign(self,node):
        if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='n_courses':
            return ast.copy_location(ast.Assign(targets=node.targets,value=ast.parse(
                'max(row for side,row in row_intervals)+1',mode='eval').body),node)
        return node
nodes=[ActualRows().visit(n) if n.name=='geometry_audit' else n for n in nodes]
for n in nodes:ast.fix_missing_locations(n)
checks=dict(Counter=Counter,hashlib=hashlib,math=math)
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(B/'audit.py'),'exec'),checks)
# Material-slot and shader fingerprints are the *exact* 9D inventory method;
# normalize only the intentional parent organizational difference.
src=(D/'regress.py').read_text()
nodes=[n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in ('shader','object_inventory')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(D/'regress.py'),'exec'),checks)

def meshes(house):return [*house.body_objects,*house.roof.roof_collection.objects]
def local_inventory(obs):
    rows=checks['object_inventory'](SimpleNamespace(objects=obs))
    return sorted([(r[0],r[1],True,*r[3:]) for r in rows],key=repr)
def hashes(house):
    return checks['hash_objects'](house.roof.roof_collection.objects),checks['hash_objects'](house.body_objects)
def tris(obs):return sum(len(f.vertices)-2 for o in obs for f in o.data.polygons)
def material_count(obs):return len({m.as_pointer() for o in obs for m in o.data.materials})
def snapshot():
    return {key:tuple(sorted(o.name for o in values)) for key,values in
            [('objects',bpy.data.objects),('meshes',bpy.data.meshes),
             ('materials',bpy.data.materials),('collections',bpy.data.collections)]}
def expect_error(fn,exceptions=(ValueError,TypeError)):
    before=snapshot()
    try:fn()
    except exceptions:pass
    else:raise AssertionError('invalid call succeeded')
    assert snapshot()==before,'failed call changed scene datablocks'

def drop(house):
    r=house.roof
    mats={m for o in house.body_objects for m in o.data.materials}
    roofmats={m for o in r.roof_collection.objects for m in o.data.materials}
    for o in list(r.roof_collection.objects):
        data=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if data.users==0:bpy.data.meshes.remove(data)
    house.building_collection.children.unlink(r.roof_collection)
    bpy.data.collections.remove(r.roof_collection)
    for o in house.body_objects:
        data=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if data.users==0:bpy.data.meshes.remove(data)
    bpy.data.objects.remove(house.building_root,do_unlink=True)
    bpy.data.collections.remove(house.building_collection)
    for m in mats|roofmats:
        if m.users==0:bpy.data.materials.remove(m)

# Independent repeated build in the same scene, no names or order in the hashes.
rows={};controls={}
for key,raw in config.items():
    p=Cottage(**raw)
    for state in ('CLEAN','AGED'):
        house=build_cottage(p,'09F_'+key+'_'+state,state)
        roof=house.roof
        obs=meshes(house)
        target=expected[key+'_'+state]
        geo=checks['geometry_audit'](SimpleNamespace(objects=obs),p)
        roof_sha,body_sha=hashes(house)
        assert (roof_sha,body_sha)==(target['new_roof_hash'],target['new_nonroof_hash']),(key,state,'mesh sha')
        assert (roof.courses_per_side,roof.shingle_count)==(target['after_courses'],target['shingles'])
        assert roof.courses_per_side==geo['courses_per_slope']
        assert (tris(roof.roof_collection.objects),tris(obs))==(target['roof_triangles'],target['total_triangles'])
        assert len(roof.roof_collection.objects)==5 and len(roof.deck_objects)==2 and len(roof.ridge_objects)==2
        assert len(roof.shingle_object.data.materials)==4 and material_count(obs)==8
        faces=roof.shingle_object.data.polygons
        assert len(faces)==roof.shingle_count*6
        assert all(len({f.material_index for f in faces[i:i+6]})==1 for i in range(0,len(faces),6))
        actual_moss=sum(faces[i].material_index==3 for i in range(0,len(faces),6))
        assert actual_moss==target['moss_tinted_shingles']
        assert all(o.parent==house.building_root and tuple(o.users_collection)==(roof.roof_collection,)
                   and o.get('role')=='roof' for o in roof.roof_collection.objects)
        assert all(o.parent==house.building_root and tuple(o.users_collection)==(house.building_collection,)
                   for o in house.body_objects)
        assert tuple(house.building_root.users_collection)==(house.building_collection,)
        assert all(geo[k]==target['roof_dimensions_and_integrity'][k] for k in
             ('shortest_shingle_slope_m','max_gable_edge_gap_m','max_between_shingles_gap_m',
              'ridge_height_m','roof_x_extent_m','deck_y_extent_m'))
        with bpy.data.libraries.load(str(C/'wooden_roof_validation_09c.blend'),link=False) as (source,loaded):
            archive_name='08A_09C_'+key+'_'+state
            assert archive_name in source.collections
            loaded.collections=[archive_name]
        archive=loaded.collections[0]
        assert local_inventory(archive.objects)==local_inventory(obs),(key,state,'material/vertex inventory')
        for o in list(archive.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(archive)
        rows[key+'_'+state]=dict(roof_sha256=roof_sha,body_sha256=body_sha,courses=roof.courses_per_side,
            shingles=roof.shingle_count,roof_triangles=tris(roof.roof_collection.objects),
            total_triangles=tris(obs),materials=material_count(obs),
            moss_tinted_shingles=actual_moss,integrity=geo,status='PASS')
        if key in ('long','compact','T03_short','T05_shallow'):controls[(key,state)]=house
        else:drop(house)
        print('09F_CASE',key,state,'PASS',flush=True)
    assert rows[key+'_CLEAN']['roof_sha256']==rows[key+'_AGED']['roof_sha256']
    assert rows[key+'_CLEAN']['body_sha256']==rows[key+'_AGED']['body_sha256']

# Same input after intervening different seeds and creation order.
for key in ('T02_wide','long','T05_shallow'):
    p=Cottage(**config[key]);house=build_cottage(p,'repeat_'+key,'AGED')
    assert hashes(house)==(expected[key+'_AGED']['new_roof_hash'],expected[key+'_AGED']['new_nonroof_hash'])
    drop(house)
reverse_b=build_cottage(Cottage(**config['compact']),'09F_reverse_B','AGED')
reverse_a=build_cottage(Cottage(**config['long']),'09F_reverse_A','CLEAN')
assert hashes(reverse_b)==(expected['compact_AGED']['new_roof_hash'],expected['compact_AGED']['new_nonroof_hash'])
assert hashes(reverse_a)==(expected['long_CLEAN']['new_roof_hash'],expected['long_CLEAN']['new_nonroof_hash'])
drop(reverse_b);drop(reverse_a)

# Direct module use without a Cottage object or any body mesh.
solo_collection=bpy.data.collections.new('09F_StandaloneOwner')
bpy.context.scene.collection.children.link(solo_collection)
solo_root=bpy.data.objects.new('09F_StandaloneRoot',None);solo_collection.objects.link(solo_root)
p=Cottage(**config['long']);base=RoofSpec(p.width,p.depth,p.wall_height,p.roof_pitch,p.seed,'CLEAN')
solo_roof=build_rectangular_roof(base,solo_root,solo_collection)
assert checks['hash_objects'](solo_roof.roof_collection.objects)==expected['long_CLEAN']['new_roof_hash']
assert solo_roof.courses_per_side==20 and solo_roof.shingle_count==1137
drop(SimpleNamespace(roof=solo_roof,body_objects=(),building_root=solo_root,building_collection=solo_collection))
# Input/owner validation: no resource or collection leak, including an injected
# failure after one deck has actually been created.
owner=controls['long','CLEAN']
for invalid in (RoofSpec(float('nan'),p.depth,p.wall_height,p.roof_pitch,p.seed,'CLEAN'),
                RoofSpec(2.9,p.depth,p.wall_height,p.roof_pitch,p.seed,'CLEAN'),
                RoofSpec(p.width,9.1,p.wall_height,p.roof_pitch,p.seed,'CLEAN'),
                RoofSpec(p.width,p.depth,1.9,p.roof_pitch,p.seed,'CLEAN'),
                RoofSpec(p.width,p.depth,p.wall_height,61,p.seed,'CLEAN'),
                RoofSpec(p.width,p.depth,p.wall_height,p.roof_pitch,-1,'CLEAN'),
                RoofSpec(p.width,p.depth,p.wall_height,p.roof_pitch,2**31,'CLEAN'),
                RoofSpec(p.width,p.depth,p.wall_height,p.roof_pitch,p.seed,'OTHER'),
                RoofSpec(float('inf'),p.depth,p.wall_height,p.roof_pitch,p.seed,'CLEAN')):
    expect_error(lambda invalid=invalid:build_rectangular_roof(invalid,owner.building_root,owner.building_collection))
protected={key:(hashes(h),tuple(checks['shader'](m) for m in h.roof.shingle_object.data.materials),
                tuple(h.building_root.location)) for key,h in controls.items()}
expect_error(lambda:build_rectangular_roof(base,None,owner.building_collection))
expect_error(lambda:build_rectangular_roof(base,owner.building_root,controls['compact','CLEAN'].building_collection))
expect_error(lambda:build_rectangular_roof(base,owner.building_root,owner.building_collection))
# A new owner exposes the actual creation-failure cleanup path without touching existing houses.
coll=bpy.data.collections.new('09F_FailureOwner');bpy.context.scene.collection.children.link(coll)
root=bpy.data.objects.new('09F_FailureRoot',None);coll.objects.link(root)
root.scale.x=2
expect_error(lambda:build_rectangular_roof(base,root,coll));root.scale.x=1
root.rotation_euler.x=.1
expect_error(lambda:build_rectangular_roof(base,root,coll));root.rotation_euler.x=0
root.location.x=float('nan')
expect_error(lambda:build_rectangular_roof(base,root,coll));root.location.x=0
original=module._mesh
calls=[0]
def fail_after_first(*args,**kwargs):
    result=original(*args,**kwargs);calls[0]+=1
    if calls[0]==1:raise RuntimeError('injected deck construction failure')
    return result
module._mesh=fail_after_first
try:
    expect_error(lambda:build_rectangular_roof(base,root,coll),(RuntimeError,))
finally:module._mesh=original
assert calls==[1] and not coll.children and tuple(coll.objects)==(root,)
bpy.data.objects.remove(root,do_unlink=True);bpy.data.collections.remove(coll)
calls[0]=0;module._mesh=fail_after_first
try:
    expect_error(lambda:build_cottage(p,'09F_failed_adapter','CLEAN'),(RuntimeError,))
finally:module._mesh=original
assert calls==[1]
assert all((hashes(h),tuple(checks['shader'](m) for m in h.roof.shingle_object.data.materials),
            tuple(h.building_root.location))==protected[key] for key,h in controls.items())

report=dict(blender=bpy.app.version_string,base_commit='fc6a355',cases=rows,
            archives_exact=True,invalid_input_and_partial_failure_isolated=True,
            seed_replay_and_order_independent=True)
(HERE/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print('09F_AUDIT',len(rows),'cases, all hashes/materials/geometry PASS',flush=True)

# Cycles controls use the exact final 9C/9D camera/light rig for per-pixel regression.
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.19,.195,.21,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.75
for label,pos,power,size in [('Key',(0,-5,9),1000,7),('Fill',(-6,1,6),430,6)]:
    ld=bpy.data.lights.new('09C_'+label,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    light=bpy.data.objects.new('09C_'+label,ld);scene.collection.objects.link(light);light.location=pos
    light.rotation_euler=(Vector((0,0,2))-light.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('09C_Camera');camd.type='ORTHO'
cam=bpy.data.objects.new('09C_Camera',camd);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(10,-12,9);cam.rotation_euler=(Vector((0,0,2.8))-cam.location).to_track_quat('-Z','Y').to_euler()
camd.ortho_scale=14.5
out=HERE/'screenshots';out.mkdir(exist_ok=True)
for key in ('long','compact','T03_short','T05_shallow'):
    for state in ('CLEAN','AGED'):
        for identity,h in controls.items():
            for ob in meshes(h):ob.hide_render=identity!=(key,state)
        scene.render.filepath=str(out/f'{key}_{state.lower()}_iso.png')
        bpy.ops.render.render(write_still=True)
        print('09F_RENDER',key,state,flush=True)
for house in controls.values():drop(house)
# Three roofs, three owners and private material/mesh IDs in one saved scene.
a=build_cottage(Cottage(**config['long']),'09F_A','CLEAN')
b=build_cottage(Cottage(**config['compact']),'09F_B','AGED',location=(35,12,0))
c=build_cottage(Cottage(**{**config['long'],'seed':29}),'09F_C','AGED',location=(-15,8,0),yaw=.45)
houses=(a,b,c)
bpy.context.view_layer.update()
for h in houses:
    assert len(h.roof.roof_collection.objects)==5
    assert all(ob.parent==h.building_root for ob in meshes(h))
assert len({h.building_root.as_pointer() for h in houses})==3
assert len({h.roof.shingle_object.data.as_pointer() for h in houses})==3
assert len({h.roof.shingle_object.data.materials[0].as_pointer() for h in houses})==3
transform_errors=[(h.building_root.name,o.name,(o.matrix_world@o.data.vertices[0].co -
                  h.building_root.matrix_world@(o.matrix_basis@o.data.vertices[0].co)).length)
                  for h in houses for o in meshes(h)]
assert max(x[2] for x in transform_errors)<1e-5, sorted(transform_errors,key=lambda x:-x[2])[:5]
# Root-local coordinates do not depend on placement. A translated/rotated C
# must match an identically seeded identity-root probe.
probe=build_cottage(Cottage(**{**config['long'],'seed':29}),'09F_C_probe','AGED')
assert hashes(probe)==hashes(c)
drop(probe)
# Mutate B alone; prove A/C roof meshes/shaders/root transform do not change.
def state(h):return (hashes(h),tuple(checks['shader'](m) for m in h.roof.shingle_object.data.materials),
                      tuple(h.building_root.location),tuple(h.building_root.rotation_euler))
sa,sc=state(a),state(c)
material=b.roof.shingle_object.data.materials[0]
old_color=material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:]
old_location=b.building_root.location.copy()
material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.75,.3,.1,1)
b.building_root.location.x+=2
bpy.context.view_layer.update()
assert state(a)==sa and state(c)==sc
material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=old_color
b.building_root.location=old_location
bpy.context.view_layer.update()
assert tuple(b.building_root.location)==(35,12,0)
# Whole scene preview with the same lighting and orthographic camera type.
cam.location=(35,-55,50);cam.rotation_euler=(Vector((10,7,2))-cam.location).to_track_quat('-Z','Y').to_euler()
camd.ortho_scale=58
scene.render.resolution_x=1400;scene.render.resolution_y=800
scene.render.filepath=str(out/'three_owned_cottages.png')
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=800;scene.render.resolution_y=600
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'three_owned_cottages.blend'))
(HERE/'ownership.json').write_text(json.dumps(dict(blender=bpy.app.version_string,
    houses={name:dict(root=h.building_root.name,collection=h.building_collection.name,
        roof_collection=h.roof.roof_collection.name,root_location=list(h.building_root.location),
        root_z_rotation=h.building_root.rotation_euler.z,roof_hash=hashes(h)[0],
        body_hash=hashes(h)[1],
        roof_material_colors=[list(m.diffuse_color) for m in h.roof.shingle_object.data.materials],
        face_material_sha256=hashlib.sha256(bytes(f.material_index for f in h.roof.shingle_object.data.polygons)).hexdigest(),
        bodies=len(h.body_objects),roofs=len(h.roof.roof_collection.objects))
        for name,h in zip(('A','B','C'),houses)},mutation_isolated=True),indent=2)+'\n')
