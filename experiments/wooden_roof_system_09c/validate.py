"""Phase 9C: six bounded Cottage inputs, unchanged 9A roof and 9B checks.
blender -b -t 4 -P experiments/wooden_roof_system_09c/validate.py
Use ROOF09C_AUDIT_ONLY=1 to skip the renders. Failures are recorded, never fixed.
"""
import ast
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
import time
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
A=ROOT.parent/'wooden_roof_system_09a'
B=ROOT.parent/'wooden_roof_system_09b'
sys.path.insert(0,str(ROOT.parent/'cottage_generator_08a'))
from cottage import Cottage,generate,mesh
assert bpy.app.version[:2]==(5,2),bpy.app.version_string
raw=json.loads((ROOT/'config.json').read_text())
assert list(raw)==[f'T{i:02d}_{name}' for i,name in enumerate(
    ('narrow','wide','short','long','shallow','steep'),1)]
params={key:Cottage(**v) for key,v in raw.items()}
for p in params.values():p.validate()
reference=json.loads((B/'config.json').read_text())
assert set(reference)=={'long','compact'}
all_params={**{key:Cottage(**value) for key,value in reference.items()},**params}
for p in all_params.values():p.validate()
assert len({p.seed for p in all_params.values()})==8

# Extract unchanged roof definitions: importing 9A build.py would overwrite 9A output.
roof_source=(A/'build.py').read_text()
roof_names={'roof_material','roof_geometry','tri','signature'}
roof_funcs=[n for n in ast.parse(roof_source).body if isinstance(n,ast.FunctionDef) and n.name in roof_names]
assert {n.name for n in roof_funcs}==roof_names
api=dict(bpy=bpy,math=math,random=random,hashlib=hashlib,mesh=mesh)
exec(compile(ast.Module(body=roof_funcs,type_ignores=[]),str(A/'build.py'),'exec'),api)
# Use the existing 9B geometry audit; turn its assertions into logged violations
# ONLY for the six exploratory inputs. References run the exact strict 9B audit.
b_source=(B/'audit.py').read_text()
b_names={'roof_objects','hash_objects','volume','geometry_audit'}
b_funcs=[n for n in ast.parse(b_source).body if isinstance(n,ast.FunctionDef) and n.name in b_names]
assert {n.name for n in b_funcs}==b_names
checks=dict(Counter=Counter,hashlib=hashlib,math=math)
exec(compile(ast.Module(body=b_funcs,type_ignores=[]),str(B/'audit.py'),'exec'),checks)
class CaptureThresholds(ast.NodeTransformer):
    def visit_Assign(self,node):
        if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='n_courses':
            # 9B expects ceil(slope/step), but 9A sometimes intentionally skips
            # a last row when <0.06 m remains. Log the discrepancy, then use
            # actual rows to finish measuring coverage instead of crashing.
            supplement=ast.parse('''
observed_courses=max(row for side,row in row_intervals)+1
if observed_courses != n_courses:
    audit_issues.append(f'generated course count {observed_courses} differs from reported {n_courses}')
n_courses=observed_courses
''').body
            return [node,*supplement]
        return node
    def visit_Assert(self,node):
        expr=ast.get_source_segment(b_source,node.test) or f'line {node.lineno}'
        append=ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='audit_issues',ctx=ast.Load()),
            attr='append',ctx=ast.Load()),args=[ast.Constant(value=expr)],keywords=[]))
        return ast.copy_location(ast.If(test=ast.UnaryOp(op=ast.Not(),operand=node.test),
                                         body=[append],orelse=[]),node)
# Parse again so the strict original isn't mutated.
explore=[n for n in ast.parse(b_source).body if isinstance(n,ast.FunctionDef) and n.name=='geometry_audit']
explore[0].name='geometry_audit_recording'
explore=CaptureThresholds().visit(explore[0])
ast.fix_missing_locations(explore)
checks['audit_issues']=[]
exec(compile(ast.Module(body=[explore],type_ignores=[]),str(B/'audit.py'),'exec'),checks)


def make(key,p,state):
    api['p']=p
    t=time.perf_counter()
    c,_=generate(p,'09C_'+key+'_'+state,refine_eave=False)
    for ob in list(c.objects):
        if ob.get('role')=='roof':bpy.data.objects.remove(ob,do_unlink=True)
    info=api['roof_geometry'](c,state=='AGED')
    bpy.context.view_layer.update()
    return c,info,round((time.perf_counter()-t)*1000,2)


def mesh_hash(c,roof):
    return checks['hash_objects']([o for o in c.objects if bool(o.get('role')=='roof')==roof])

objects={};results={};failures={};hashes={}
for key,p in all_params.items():
    for state in ('CLEAN','AGED'):
        c,info,ms=make(key,p,state)
        objects[(key,state)]=c
        roof=checks['roof_objects'](c)
        entry=dict(config=vars(p),roof_triangles=api['tri'](roof),total_triangles=api['tri'](c.objects),
            materials=len({m.as_pointer() for o in c.objects for m in o.data.materials}),
            generation_ms_single_run=ms,**info)
        results[key+'_'+state]=entry
        checks['audit_issues']=[]
        try:
            if key in reference:entry['geometry']=checks['geometry_audit'](c,p)
            else:entry['geometry']=checks['geometry_audit_recording'](c,p)
        except (AssertionError,ValueError,IndexError,ZeroDivisionError) as exc:
            checks['audit_issues'].append('audit did not complete: '+repr(exc))
        failures[key+'_'+state]=list(checks['audit_issues'])
        hashes[(key,state)]=(mesh_hash(c,True),mesh_hash(c,False))
    if hashes[(key,'CLEAN')]!=hashes[(key,'AGED')]:
        for state in ('CLEAN','AGED'):failures[key+'_'+state].append('CLEAN/AGED geometry differs')
    for state in ('CLEAN','AGED'):
        replay,_,_=make(key+'_replay',p,state)
        if hashes[(key,state)]!=(mesh_hash(replay,True),mesh_hash(replay,False)):
            failures[key+'_'+state].append('seed replay geometry differs')
        for ob in list(replay.objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(replay)
    print('09C_TEST',key,[(s,results[key+'_'+s]['shingles'],failures[key+'_'+s]) for s in ('CLEAN','AGED')],flush=True)

# Check saved 9A and 9B reference meshes (the 9B Compact was placed x+11 in its saved scene).
for path,coll_name,key,shift in ((A/'wooden_roof_09a.blend','08A_09A_CLEAN','long',0),
                                  (B/'wooden_roof_portability_09b.blend','08A_09B_compact_CLEAN','compact',11)):
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):
        assert coll_name in src.collections,src.collections
        dst.collections=[coll_name]
    archived=dst.collections[0]
    for ob in archived.objects:ob.location.x-=shift
    if hashes[(key,'CLEAN')]!=(mesh_hash(archived,True),mesh_hash(archived,False)):
        failures[key+'_CLEAN'].append('saved reference mesh fingerprint differs')
    for ob in list(archived.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(archived)
b_metrics=json.loads((B/'measurements.json').read_text())['states']
for key in reference:
    for state in ('CLEAN','AGED'):
        now=results[key+'_'+state];old=b_metrics[key+'_'+state]
        if any(now[k]!=old[k] for k in ('roof_triangles','total_triangles','materials','shingles','courses','moss_tinted_shingles')):
            failures[key+'_'+state].append('9B reference metrics differ')
# Reconstruct references AFTER the six cases: detect cross-case global RNG or other state leakage.
for key in reference:
    p=all_params[key]
    for state in ('CLEAN','AGED'):
        probe,_,_=make(key+'_after_all',p,state)
        if hashes[(key,state)]!=(mesh_hash(probe,True),mesh_hash(probe,False)):
            failures[key+'_'+state].append('later cases changed reference geometry')
        for ob in list(probe.objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(probe)
for key in all_params:
    for state in ('CLEAN','AGED'):
        entry=results[key+'_'+state]
        entry['issues']=failures[key+'_'+state]
        entry['status']='FAIL' if entry['issues'] else 'PASS'
        entry['roof_mesh_sha256'],entry['nonroof_mesh_sha256']=hashes[(key,state)]
report=dict(blender=bpy.app.version_string,base_commit='94ac0a3',config=raw,
            thresholds_m=dict(max_gable_edge_gap=.09,max_between_shingles_gap=.04),
            phase9a_source_sha256=hashlib.sha256(roof_source.encode()).hexdigest(),
            phase9b_audit_source_sha256=hashlib.sha256(b_source.encode()).hexdigest(),
            cases=results)
(ROOT/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print('09C_SUMMARY',json.dumps({k:(v['status'],v.get('geometry',{}).get('max_gable_edge_gap_m'),
    v.get('geometry',{}).get('max_between_shingles_gap_m'),v['issues']) for k,v in results.items()}),flush=True)
if os.environ.get('ROOF09C_AUDIT_ONLY')=='1':sys.exit(0)

scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.19,.195,.21,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.75
for label,pos,power,size in [('Key',(0,-5,9),1000,7),('Fill',(-6,1,6),430,6)]:
    light=bpy.data.lights.new('09C_'+label,'AREA');light.energy=power;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new('09C_'+label,light);scene.collection.objects.link(ob);ob.location=pos
    ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('09C_Camera');cam_data.type='ORTHO'
cam=bpy.data.objects.new('09C_Camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam
OUT=ROOT/'screenshots';OUT.mkdir(exist_ok=True)
for key,p in all_params.items():
    # Identical iso camera/ortho across all eight cases: no flattering reframing.
    views={'iso':((10,-12,9),(0,0,2.8),14.5)}
    # One shared, generous frame also contains the valid 60-degree ridge.
    if key not in reference:views['front']=((0,-13,4),(0,0,2.5),12.5)
    if any(failures[key+'_'+s] for s in ('CLEAN','AGED')):
        end=p.depth/2+.25;eave=p.width/2+.34
        ridge=p.wall_height+p.width/2*math.tan(math.radians(p.roof_pitch))
        views.update(gable_ridge=((3,-end-4.2,5.6),(0,-end,ridge-.18),3.7),
                     eave_end=((eave+3,-end-2.6,4.8),(eave,-end+.10,p.wall_height),3.4))
    for view,(eye,target,scale) in views.items():
        cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cam_data.ortho_scale=scale
        states=('CLEAN','AGED') if view=='iso' else ('CLEAN',)
        for state in states:
            for identity,c in objects.items():
                for ob in c.objects:ob.hide_render=identity!=(key,state)
            scene.render.filepath=str(OUT/f'{key}_{state.lower()}_{view}.png')
            bpy.ops.render.render(write_still=True)
            print('09C_RENDER',key,state,view,flush=True)
# Preserve the 16 generated models, separated for inspection without changing render results.
for number,((key,state),c) in enumerate(objects.items()):
    offset=Vector(((number//2)%4*14,(number//8)*14+(number%2)*7,0))
    for ob in c.objects:ob.location+=offset;ob.hide_render=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'wooden_roof_validation_09c.blend'))
