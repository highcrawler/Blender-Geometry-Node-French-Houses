"""Phase 9D: compare corrected canonical 9A roof to de11f7e, all 8 x 2 states.
blender -b -t 4 -P experiments/wooden_roof_system_09d/regress.py
ROOF09D_AUDIT_ONLY=1 skips only the four-case CLEAN/AGED control renders.
"""
import ast
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
A=ROOT.parent/'wooden_roof_system_09a'
B=ROOT.parent/'wooden_roof_system_09b'
C=ROOT.parent/'wooden_roof_system_09c'
sys.path.insert(0,str(ROOT.parent/'cottage_generator_08a'))
from cottage import Cottage,generate,mesh
assert bpy.app.version[:2]==(5,2),bpy.app.version_string
config={**json.loads((B/'config.json').read_text()),**json.loads((C/'config.json').read_text())}
assert list(config)==['long','compact','T01_narrow','T02_wide','T03_short',
                      'T04_long','T05_shallow','T06_steep']
params={k:Cottage(**p) for k,p in config.items()}
for p in params.values():p.validate()
expected_courses=dict(zip(config,(20,18,13,31,21,21,18,29)))
expected_triangles=dict(zip(config,((13692,14054),(6456,6818),(5616,5978),(15672,16034),
                                    (6336,6698),(17400,17762),(8892,9254),(14196,14558))))
old_source=subprocess.check_output(['git','show','de11f7e:experiments/wooden_roof_system_09a/build.py'],
                                   cwd=PROJECT,text=True)
new_source=(A/'build.py').read_text()
archived=json.loads((C/'measurements.json').read_text())['cases']
assert hashlib.sha256(old_source.encode()).hexdigest()==json.loads(
    (C/'measurements.json').read_text())['phase9a_source_sha256']


def roof_namespace(source):
    names={'roof_material','roof_geometry','tri','signature'}
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes}==names
    env=dict(bpy=bpy,math=math,random=random,hashlib=hashlib,mesh=mesh)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(A/'build.py'),'exec'),env)
    return env
old_api=roof_namespace(old_source)
new_api=roof_namespace(new_source)

# Retain the 9B audit geometry/threshold checks unchanged, adapting ONLY its
# assumption that 'ceil' is necessarily an existing last course: use observed
# row IDs for the 9D audit. All 9B <.09/<.04/>.10 thresholds remain identical.
audit_src=(B/'audit.py').read_text()
names={'roof_objects','hash_objects','volume','geometry_audit'}
nodes=[n for n in ast.parse(audit_src).body if isinstance(n,ast.FunctionDef) and n.name in names]
assert {n.name for n in nodes}==names
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


def build(api,key,p,state,label):
    api['p']=p
    start=time.perf_counter()
    c,_=generate(p,'09D_'+key+'_'+state+'_'+label,refine_eave=False)
    for ob in list(c.objects):
        if ob.get('role')=='roof':bpy.data.objects.remove(ob,do_unlink=True)
    extra=api['roof_geometry'](c,state=='AGED')
    bpy.context.view_layer.update()
    return c,extra,round((time.perf_counter()-start)*1000,2)


def remove(c):
    for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(c)


def fingerprint(objects):return checks['hash_objects'](objects)
def roof(c):return checks['roof_objects'](c)
def body(c):return [ob for ob in c.objects if not ob.get('role')=='roof']

def shader(mat):
    def val(x):
        if hasattr(x,'to_tuple'):return tuple(round(float(v),7) for v in x)
        if isinstance(x,(float,int,bool)):return round(float(x),7)
        return str(x)
    result=[tuple(round(float(x),7) for x in mat.diffuse_color),mat.use_nodes]
    if mat.use_nodes:
        for node in sorted(mat.node_tree.nodes,key=lambda n:(n.bl_idname,n.name)):
            inputs=tuple((s.name,val(s.default_value)) for s in node.inputs if hasattr(s,'default_value'))
            ramp=tuple((round(e.position,7),tuple(round(float(v),7) for v in e.color))
                       for e in node.color_ramp.elements) if node.type=='VALTORGB' else ()
            result.append((node.bl_idname,inputs,ramp))
        result.append(tuple(sorted((link.from_node.bl_idname,link.from_socket.name,
                                    link.to_node.bl_idname,link.to_socket.name)
                                   for link in mat.node_tree.links)))
    return tuple(result)


def object_inventory(c):
    """Mesh topology/vertex coordinates, flat hierarchy, per-face slot assignments and shaders."""
    output=[]
    for ob in c.objects:
        h=hashlib.sha256()
        for v in ob.data.vertices:
            h.update(repr(tuple(float(x) for x in v.co)).encode())
        for face in ob.data.polygons:
            h.update(repr(tuple(face.vertices)).encode())
        output.append((ob.get('role')=='roof',ob.type,ob.parent is None,
                       h.hexdigest(),tuple(f.material_index for f in ob.data.polygons),
                       tuple(shader(m) for m in ob.data.materials)))
    return sorted(output,key=repr)


controls={};matrix={};errors=[]
for key,p in params.items():
    for state in ('CLEAN','AGED'):
        label=key+'_'+state
        prior,old,old_ms=build(old_api,key,p,state,'before')
        current,now,new_ms=build(new_api,key,p,state,'after')
        old_roof_hash=fingerprint(roof(prior));new_roof_hash=fingerprint(roof(current))
        old_body_hash=fingerprint(body(prior));new_body_hash=fingerprint(body(current))
        baseline=archived[label]
        audited=checks['geometry_audit'](current,p)
        triangles=(new_api['tri'](roof(current)),new_api['tri'](current.objects))
        issues=[]
        if old['courses']!=baseline['courses']:issues.append('old reported count differs from 9C archive')
        if now['courses']!=expected_courses[key] or now['courses']!=audited['courses_per_slope']:
            issues.append('new count differs from independently observed rows')
        if old_roof_hash!=new_roof_hash or old_body_hash!=new_body_hash:
            issues.append('old/new transformed mesh geometry differs')
        if new_roof_hash!=baseline['roof_mesh_sha256'] or new_body_hash!=baseline['nonroof_mesh_sha256']:
            issues.append('new mesh differs from archived 9C fingerprint')
        inventory_equal=object_inventory(prior)==object_inventory(current)
        if not inventory_equal:
            issues.append('vertex/face or object/material inventory differs')
        # Compare actual 9C Blender archive, including local float32 vertex coordinates,
        # polygon winding, per-face slot indices, shader values and flat hierarchy.
        coll_name='08A_09C_'+key+'_'+state
        with bpy.data.libraries.load(str(C/'wooden_roof_validation_09c.blend'),link=False) as (src,dst):
            assert coll_name in src.collections,coll_name
            dst.collections=[coll_name]
        saved=dst.collections[0]
        archive_inventory_equal=object_inventory(saved)==object_inventory(current)
        if not archive_inventory_equal:issues.append('saved 9C Blender object/material inventory differs')
        remove(saved)
        if triangles!=expected_triangles[key] or triangles!=(baseline['roof_triangles'],baseline['total_triangles']):
            issues.append('triangle regression')
        if now['shingles']!=old['shingles'] or now['moss_tinted_shingles']!=old['moss_tinted_shingles']:
            issues.append('shingle or moss/material state regression')
        if any(audited[k]!=baseline['geometry'][k] for k in ('deck_eave_halfwidth_m','deck_halfdepth_m',
                'ridge_height_m','slope_length_m','max_gable_edge_gap_m','max_between_shingles_gap_m',
                'shortest_shingle_slope_m','last_course_ends_past_ridge_m')):
            issues.append('measured roof dimensions or gaps differ')
        # Run a second independent generation; compare both mesh hashes and actual metadata.
        again,repeat,_=build(new_api,key,p,state,'replay')
        if repeat!=now or fingerprint(roof(again))!=new_roof_hash or fingerprint(body(again))!=new_body_hash:
            issues.append('seed replay differs')
        remove(again)
        matrix[label]=dict(config=vars(p),before_courses=old['courses'],after_courses=now['courses'],
            observed_courses=audited['courses_per_slope'],shingles=now['shingles'],
            moss_tinted_shingles=now['moss_tinted_shingles'],roof_triangles=triangles[0],
            total_triangles=triangles[1],materials=len({m.as_pointer() for o in current.objects for m in o.data.materials}),
            generation_ms_single_run=new_ms,previous_ms_single_run=old_ms,
            old_roof_hash=old_roof_hash,new_roof_hash=new_roof_hash,
            old_nonroof_hash=old_body_hash,new_nonroof_hash=new_body_hash,
            roof_dimensions_and_integrity=audited,object_and_material_inventory_equal=inventory_equal,
            archived_9c_object_and_material_inventory_equal=archive_inventory_equal,
            status='FAIL' if issues else 'PASS',issues=issues)
        errors.extend(label+': '+issue for issue in issues)
        print('09D_CASE',label,old['courses'],'->',now['courses'],matrix[label]['status'],flush=True)
        remove(prior)
        if key in ('long','compact','T03_short','T05_shallow'):controls[(key,state)]=current
        else:remove(current)
    a,b=(matrix[key+'_'+state] for state in ('CLEAN','AGED'))
    if a['new_roof_hash']!=b['new_roof_hash'] or a['new_nonroof_hash']!=b['new_nonroof_hash']:
        errors.append(key+': CLEAN/AGED geometry differs')
    if (a['after_courses'],a['shingles'],a['roof_triangles'])!=(b['after_courses'],b['shingles'],b['roof_triangles']):
        errors.append(key+': CLEAN/AGED counts differ')

# Check saved collection meshes for BOTH reference buildings (not just 9C hashes).
for path,name,key,offset in ((A/'wooden_roof_09a.blend','08A_09A_CLEAN','long',Vector((0,0,0))),
                             (B/'wooden_roof_portability_09b.blend','08A_09B_compact_CLEAN','compact',Vector((11,0,0)))):
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):
        assert name in src.collections
        dst.collections=[name]
    archive=dst.collections[0]
    for ob in archive.objects:ob.location-=offset
    c=controls[(key,'CLEAN')]
    if fingerprint(roof(archive))!=fingerprint(roof(c)) or fingerprint(body(archive))!=fingerprint(body(c)):
        errors.append(key+': saved 9A/9B reference mesh differs')
    remove(archive)

report=dict(blender=bpy.app.version_string,base_commit='de11f7e',
    old_source_sha256=hashlib.sha256(old_source.encode()).hexdigest(),
    corrected_source_sha256=hashlib.sha256(new_source.encode()).hexdigest(),
    thresholds_m=dict(gable=.09,internal=.04,min_shingle=.10),
    matrix=matrix,errors=errors)
(ROOT/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print('09D_AUDIT',json.dumps({k:(v['before_courses'],v['after_courses'],v['status'])
                            for k,v in matrix.items()}),flush=True)
if errors:
    print('09D_ERRORS',errors,flush=True)
    raise SystemExit(1)
if os.environ.get('ROOF09D_AUDIT_ONLY')=='1':raise SystemExit(0)

# Exact Phase-9C final Cycles iso scene/camera/light parameters; image differences
# are recorded separately (Cycles/denoising may be nondeterministic).
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.19,.195,.21,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.75
for label,pos,power,size in [('Key',(0,-5,9),1000,7),('Fill',(-6,1,6),430,6)]:
    data=bpy.data.lights.new('09C_'+label,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new('09C_'+label,data);scene.collection.objects.link(ob);ob.location=pos
    ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('09C_Camera');camdata.type='ORTHO'
cam=bpy.data.objects.new('09C_Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(10,-12,9);cam.rotation_euler=(Vector((0,0,2.8))-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.ortho_scale=14.5
OUT=ROOT/'screenshots';OUT.mkdir(exist_ok=True)
for key in ('long','compact','T03_short','T05_shallow'):
    for state in ('CLEAN','AGED'):
        for identity,c in controls.items():
            for ob in c.objects:ob.hide_render=identity!=(key,state)
        scene.render.filepath=str(OUT/f'{key}_{state.lower()}_iso.png')
        bpy.ops.render.render(write_still=True)
        print('09D_RENDER',key,state,flush=True)
# Save unmodified four-case models separated for inspection only AFTER all proofs/renders.
for i,((key,state),c) in enumerate(controls.items()):
    offset=Vector(((i//2)*14,(i%2)*7,0))
    for ob in c.objects:ob.location+=offset;ob.hide_render=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'wooden_roof_rowcount_09d.blend'))
