"""Phase 9B: reuse 9A roof functions without modifying or copying the generator.
Run: blender -b -t 4 -P experiments/wooden_roof_system_09b/audit.py
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
BASE=ROOT.parent/'wooden_roof_system_09a'
sys.path.insert(0,str(ROOT.parent/'cottage_generator_08a'))
from cottage import Cottage,generate,mesh
assert bpy.app.version[:2]==(5,2),bpy.app.version_string
config=json.loads((ROOT/'config.json').read_text())
params={key:Cottage(**value) for key,value in config.items()}
assert set(params)=={'long','compact'}
for p in params.values():p.validate()
assert vars(params['long'])==json.loads((BASE/'config.json').read_text())
assert vars(params['compact'])==dict(width=4.0,depth=3.5,wall_height=2.3,roof_pitch=48,seed=11)

# Import ONLY the unchanged roof functions from 9A. Executing build.py as a module
# would trigger its top-level rendering and overwrite the archived screenshots.
source=(BASE/'build.py').read_text()
tree=ast.parse(source,filename=str(BASE/'build.py'))
names={'roof_material','roof_geometry','tri','signature'}
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
assert {n.name for n in selected}==names
roof_api=dict(bpy=bpy,math=math,random=random,hashlib=hashlib,mesh=mesh)
exec(compile(ast.Module(body=selected,type_ignores=[]),str(BASE/'build.py'),'exec'),roof_api)
assert hashlib.sha256(source.encode()).hexdigest()==hashlib.sha256((BASE/'build.py').read_bytes()).hexdigest()


def triangles(objects):return roof_api['tri'](objects)
def roof_objects(coll):return [o for o in coll.objects if o.get('role')=='roof']
def make(name,p,aged):
    roof_api['p']=p
    start=time.perf_counter()
    coll,_=generate(p,'09B_'+name,refine_eave=False)
    for ob in list(coll.objects):
        if ob.get('role')=='roof':bpy.data.objects.remove(ob,do_unlink=True)
    info=roof_api['roof_geometry'](coll,aged)
    bpy.context.view_layer.update()
    elapsed=round((time.perf_counter()-start)*1000,2)
    return coll,info,elapsed


def hash_objects(objects):
    """Order/name independent; includes basis-transformed geometry, not materials."""
    individual=[]
    for o in objects:
        h=hashlib.sha256()
        for v in o.data.vertices:
            h.update(repr(tuple(round(float(x),6) for x in o.matrix_basis@v.co)).encode())
        for face in o.data.polygons:h.update(repr(tuple(face.vertices)).encode())
        individual.append(h.hexdigest())
    return hashlib.sha256(''.join(sorted(individual)).encode()).hexdigest()


def volume(vertices,faces):
    # Signed enclosed volume: sum of oriented triangle tetrahedra.
    vol=0.0
    for face in faces:
        a=vertices[face[0]]
        for i in range(1,len(face)-1):
            vol+=a.dot(vertices[face[i]].cross(vertices[face[i+1]]))/6.0
    return vol


def geometry_audit(c,p):
    roof=roof_objects(c)
    shingles=next(o for o in roof if o.name.startswith('09A_ShingleField'))
    eave_x=p.width/2+.34
    y_end=p.depth/2+.25
    ridge=p.wall_height+p.width/2*math.tan(math.radians(p.roof_pitch))
    slope=math.hypot(eave_x,ridge-p.wall_height+.10)
    verts=[v.co.copy() for v in shingles.data.vertices]
    polys=[tuple(f.vertices) for f in shingles.data.polygons]
    assert len(verts)%8==0 and len(polys)==len(verts)//8*6
    n=len(verts)//8
    lengths=[]; row_lengths={}; row_intervals={}; box_duplicates=set(); smallest_area=1e9
    nonpositive_volumes=0; bad_edges=0; zero_faces=0; bad_normals=0; duplicate_count=0
    for j in range(n):
        v=verts[j*8:j*8+8]
        f=[tuple(i-8*j for i in face) for face in polys[6*j:6*j+6]]
        assert all(0<=idx<8 for face in f for idx in face)
        assert len({tuple(sorted(face)) for face in f})==6
        edges=Counter(tuple(sorted((face[k],face[(k+1)%len(face)])))
                      for face in f for k in range(len(face)))
        bad_edges+=sum(count!=2 for count in edges.values())
        value=volume(v,f)
        nonpositive_volumes+=value<=1e-9
        for face in f:
            a=v[face[0]]
            for k in range(1,len(face)-1):
                b,c=v[face[k]],v[face[k+1]]
                area=(b-a).cross(c-a).length/2
                smallest_area=min(smallest_area,area)
                zero_faces+=area<=1e-9
                bad_normals+=area<=1e-9
        digest=tuple(tuple(round(float(x),5) for x in vv) for vv in v)
        duplicate_count+=digest in box_duplicates
        box_duplicates.add(digest)
        side=1 if v[0].x>0 else -1
        course=round((eave_x-abs(v[0].x))/eave_x*slope/.185)
        start=course*.185
        if abs(start-(eave_x-abs(v[0].x))/eave_x*slope)>.0001:raise AssertionError('irregular start')
        shingle_length=(side*(v[0].x-v[3].x)/eave_x)*slope
        lengths.append(shingle_length)
        row_lengths.setdefault((side,course),[]).append(shingle_length)
        row_intervals.setdefault((side,course),[]).append((v[0].y,v[1].y))
        assert all(abs(x.x)<=eave_x+.01 and abs(x.y)<=y_end+.02 for x in v)
    boundary=[]; max_internal_gap=0
    for key,intervals in sorted(row_intervals.items()):
        intervals.sort()
        left=max(0,intervals[0][0]+y_end)
        right=max(0,y_end-intervals[-1][1])
        boundary.append((key,round(left,5),round(right,5),len(intervals)))
        max_internal_gap=max(max_internal_gap,max((a[0]-b[1] for b,a in zip(intervals,intervals[1:])),default=0))
    n_courses=math.ceil(slope/.185)
    assert set(row_intervals)=={(side,row) for side in (-1,1) for row in range(n_courses)}
    assert all(min(v)>.185 for (_,row),v in row_lengths.items() if row<n_courses-1), 'open course transition'
    assert bad_edges==nonpositive_volumes==zero_faces==bad_normals==duplicate_count==0
    assert max_internal_gap<.04
    assert max(max(left,right) for _,left,right,_ in boundary)<.09,sorted(boundary,key=lambda x:max(x[1],x[2]),reverse=True)[:4]
    # Every closed solid (both deck slabs and both ridge planks) is also tested.
    solid_audits=[]
    for ob in roof:
        if ob==shingles:continue
        vv=[v.co for v in ob.data.vertices]
        ff=[tuple(f.vertices) for f in ob.data.polygons]
        edges=Counter(tuple(sorted((f[k],f[(k+1)%len(f)]))) for f in ff for k in range(len(f)))
        vol=volume(vv,ff)
        solid_audits.append(dict(name=ob.name.split('.')[0],manifold=all(x==2 for x in edges.values()),
                                  signed_volume_m3=round(vol,7)))
        assert all(x==2 for x in edges.values()) and vol>1e-9
    min_length=min(lengths);max_length=max(lengths)
    # Short ridge courses are covered by the ~0.235 m horizontal ridge plank;
    # reject only genuinely tiny/degenerate slivers, not concealed cap underlay.
    assert min_length>.10,('short ridge remainder',min_length)
    assert max_length<.34
    # The upper course reaches the ridge, with no free end left outside the cap.
    last_start=(n_courses-1)*.185
    last_end=last_start+min_length if n_courses==1 else max(
        ((1 if verts[j*8].x>0 else -1)*(verts[j*8].x-verts[j*8+3].x)/eave_x)*slope+last_start
        for j in range(n) if round((eave_x-abs(verts[j*8].x))/eave_x*slope/.185)==n_courses-1)
    assert last_end>=slope-1e-6 and last_start<slope,(last_end,slope,last_start)
    assert all(o.data.polygons for o in roof)
    return dict(deck_eave_halfwidth_m=round(eave_x,5),deck_halfdepth_m=round(y_end,5),
        ridge_height_m=round(ridge,5),slope_length_m=round(slope,5),
        roof_x_extent_m=round(2*eave_x,5),deck_y_extent_m=round(2*y_end,5),
        courses_per_slope=n_courses,shingles_per_course_min=min(x[3] for x in boundary),
        shingles_per_course_max=max(x[3] for x in boundary),
        max_gable_edge_gap_m=round(max(max(left,right) for _,left,right,_ in boundary),5),
        max_between_shingles_gap_m=round(max_internal_gap,5),
        shortest_shingle_slope_m=round(min_length,5),longest_shingle_slope_m=round(max_length,5),
        last_course_ends_past_ridge_m=round(last_end-slope,5),
        min_face_triangle_area_m2=round(smallest_area,9),
        nonmanifold_shingle_edges=bad_edges,nonpositive_shingle_volumes=nonpositive_volumes,
        zero_shingle_faces=zero_faces,duplicate_shingles=duplicate_count,
        deck_and_ridge=solid_audits)


objects={};metrics={};audit={}
for name,p in params.items():
    for state in ('CLEAN','AGED'):
        c,info,ms=make(name+'_'+state,p,state=='AGED')
        objects[(name,state)]=c
        roof=roof_objects(c)
        metrics[name+'_'+state]=dict(width_m=p.width,depth_m=p.depth,pitch_degrees=p.roof_pitch,
            seed=p.seed,roof_triangles=triangles(roof),total_triangles=triangles(c.objects),
            materials=len({m.as_pointer() for o in c.objects for m in o.data.materials}),
            generation_ms_single_run=ms,roof_meshes=len(roof),**info)
        audit[name+'_'+state]=geometry_audit(c,p)
    a,b=(objects[name,x] for x in ('CLEAN','AGED'))
    assert hash_objects(roof_objects(a))==hash_objects(roof_objects(b))
    assert hash_objects([o for o in a.objects if not o.get('role')=='roof'])==hash_objects([o for o in b.objects if not o.get('role')=='roof'])
    for state in ('CLEAN','AGED'):
        original=objects[name,state]
        replay,_,_=make(name+'_replay_'+state,p,state=='AGED')
        assert hash_objects(roof_objects(original))==hash_objects(roof_objects(replay))
        assert hash_objects([o for o in original.objects if not o.get('role')=='roof'])==hash_objects([o for o in replay.objects if not o.get('role')=='roof'])
        for obj in list(replay.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.collections.remove(replay)
# Actual archived 9A .blend, not just stated triangle totals or a reconstructed hash.
with bpy.data.libraries.load(str(BASE/'wooden_roof_09a.blend'),link=False) as (src,dst):
    assert '08A_09A_CLEAN' in src.collections,src.collections
    dst.collections=['08A_09A_CLEAN']
archived=dst.collections[0]
assert hash_objects(roof_objects(archived))==hash_objects(roof_objects(objects['long','CLEAN']))
assert hash_objects([o for o in archived.objects if not o.get('role')=='roof'])==hash_objects(
    [o for o in objects['long','CLEAN'].objects if not o.get('role')=='roof'])
for obj in list(archived.objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(archived)
old=json.loads((BASE/'measurements.json').read_text())['states']
for state in ('CLEAN','AGED'):
    assert all(metrics['long_'+state][key]==old[state][key] for key in
        ('roof_triangles','total_triangles','materials','shingles','courses','moss_tinted_shingles'))
assert hash_objects(roof_objects(objects['long','CLEAN']))==hash_objects(roof_objects(objects['long','AGED']))
results=dict(blender=bpy.app.version_string,source_commit='ca28be3',
    source_roof_build_sha256=hashlib.sha256(source.encode()).hexdigest(),
    config=config,baseline_9a_saved_blend_geometry_identical=True,
    clean_aged_geometry_identical_each_building=True,replay_deterministic=True,
    states=metrics,geometry_audit=audit)
(ROOT/'measurements.json').write_text(json.dumps(results,indent=2)+'\n')
print('09B_AUDIT',json.dumps({k:(v['roof_triangles'],v['shingles'],audit[k]['max_gable_edge_gap_m'],audit[k]['shortest_shingle_slope_m']) for k,v in metrics.items()}),flush=True)

if os.environ.get('ROOF09B_AUDIT_ONLY')=='1':sys.exit(0)
# Exactly the 9A lighting, Cycles settings and orthographic camera projection.
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.19,.195,.21,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.75
for label,pos,power,size in [('Key',(0,-5,9),1000,7),('Fill',(-6,1,6),430,6)]:
    light=bpy.data.lights.new('09B_'+label,'AREA');light.energy=power;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new('09B_'+label,light);scene.collection.objects.link(ob);ob.location=pos
    ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('09B_Camera');camdata.type='ORTHO'
cam=bpy.data.objects.new('09B_Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
# Same coordinates and ortho scale for both sizes in standard views.
fixed={'iso':((9,-11,8),(0,0,1.7),11.5),
       'front':((0,-13,4),(0,0,2),10.4),
       'side':((13,0,4),(0,0,2),11.5),
       'roof_detail':((5,-3.5,5.8),(1.9,-1.5,3.0),4.8)}
for name,p in params.items():
    e=p.width/2+.34; end=p.depth/2+.25
    ridge=p.wall_height+p.width/2*math.tan(math.radians(p.roof_pitch))
    specific={'gable_ridge':((3,-end-4.2,5.6),(0,-end,ridge-.18),3.7),
              'eave_end':((e+3,-end-2.6,4.8),(e,-end+.10,p.wall_height),3.4)}
    views=dict(fixed,**specific)
    views['iso_300']=((9,-11,8),(0,0,1.7),11.5 if name=='long' else 8.25)
    for view,(eye,target,scale) in views.items():
        cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        camdata.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=(480,360) if view=='iso_300' else (800,600)
        for state in ('CLEAN','AGED'):
            for key,c in objects.items():
                for ob in c.objects:ob.hide_render=key!=(name,state)
            scene.render.filepath=str(ROOT/'screenshots'/f'{name}_{state.lower()}_{view}.png')
            bpy.ops.render.render(write_still=True)
            print('09B_RENDER',name,state,view,flush=True)
# Save a non-overlapping inspection scene; after validation/renders only.
for (name,state),c in objects.items():
    offset=(0 if name=='long' else 11,0 if state=='CLEAN' else 11,0)
    for ob in c.objects:
        ob.location+=Vector(offset)
        ob.hide_render=False
scene.render.resolution_x=800;scene.render.resolution_y=600
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'wooden_roof_portability_09b.blend'))
