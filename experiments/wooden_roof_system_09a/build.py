"""Phase 9A: blender -b -t 4 -P experiments/wooden_roof_system_09a/build.py"""
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'cottage_generator_08a'))
from cottage import Cottage, generate, mesh

assert bpy.app.version[:2] == (5, 2), bpy.app.version_string
p = Cottage(**json.loads((ROOT / 'config.json').read_text()))
assert (p.width,p.depth,p.wall_height,p.roof_pitch,p.seed)==(5.1,7.3,2.3,40,23)
OUT = ROOT / 'screenshots'
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def roof_material(name, rgb):
    mat = bpy.data.materials.new('09A_' + name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = .92
    bs.inputs['Metallic'].default_value = 0
    return mat


def tri(objs):
    return sum(len(poly.vertices) - 2 for ob in objs for poly in ob.data.polygons)


def signature(objs):
    h = hashlib.sha256()
    for ob in sorted(objs, key=lambda o: o.name.split('.')[0]):
        for v in ob.data.vertices:
            h.update(repr(tuple(round(float(x), 6) for x in v.co)).encode())
        for poly in ob.data.polygons:
            h.update(repr(tuple(poly.vertices)).encode())
    return h.hexdigest()


def roof_geometry(coll, aged):
    rng = random.Random(p.seed ^ 0x9A08)
    colors = ([(.29,.185,.105), (.35,.235,.141), (.245,.165,.105), (.32,.205,.12)] if not aged else
              [(.17,.155,.133), (.235,.21,.172), (.28,.245,.193), (.22,.265,.139)])
    mats = [roof_material(('AGED' if aged else 'CLEAN') + '_' + str(i), c) for i,c in enumerate(colors)]
    eave_x = p.width / 2 + .34
    y_end = p.depth / 2 + .25
    ridge = p.wall_height + p.width / 2 * math.tan(math.radians(p.roof_pitch))
    # Substrate: thin closed plank under the shingle field, not the old straw shell.
    for side in (-1, 1):
        vertices=[]
        for x,z in ((eave_x, p.wall_height-.10), (0, ridge)):
            for y in (-y_end, y_end):
                for bottom in (True, False):
                    vertices.append((side*x,y,z+(-.13 if bottom else .012)))
        faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
        ob=mesh(coll,'09A_Deck',vertices,faces,mats[0]); ob['role']='roof'
    # Each closed shingle has eight vertices and six quads. Courses overlap by ~42%.
    vertices=[]; faces=[]; indices=[]; moss=0; shingles=0
    slope_length=math.hypot(eave_x, ridge-(p.wall_height-.10))
    course_step=.185
    shingle_length=.315
    n_courses=math.ceil(slope_length/course_step)
    for side in (-1,1):
        for row in range(n_courses):
            start=row*course_step
            if start > slope_length-.06: continue
            offset= (-.135 if row%2 else 0) + rng.uniform(-.018,.018)
            cursor=-y_end+offset
            while cursor < y_end:
                width=max(.205,min(.335,rng.gauss(.272,.029)))
                left=max(-y_end,cursor)
                right=min(y_end,cursor+width)
                cursor+=width+.006
                if right-left < .07: continue
                length=min(shingle_length+rng.uniform(-.016,.016),slope_length-start+.025)
                # End cuts vary a few millimeters; upper ends remain straight beneath next course.
                cut_l=rng.uniform(-.009,.009)
                cut_r=rng.uniform(-.009,.009)
                def point(distance,y,height):
                    t=distance/slope_length
                    return (side*(eave_x*(1-t)), y, p.wall_height-.10+(ridge-(p.wall_height-.10))*t+height)
                # Top face is slightly tapered in thickness; outward tip rides over the previous course.
                base=len(vertices)
                vertices.extend((point(start,left+cut_l,.115),point(start,right+cut_r,.115),
                                 point(start+length,right-.004,.073),point(start+length,left+.004,.073),
                                 point(start,left+cut_l,.085),point(start,right+cut_r,.085),
                                 point(start+length,right-.004,.049),point(start+length,left+.004,.049)))
                quads=((0,1,2,3),(7,6,5,4),(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3))
                faces.extend(tuple(base+i for i in q) for q in quads)
                # Aged moss is only a sparse material tint on existing shingles, biased to eave
                # and one damp slope. It introduces NO extra polygons or new roof geometry.
                damp=(row<4 and side<0) or (row>n_courses-4 and side<0)
                moss_roll=rng.random()  # same RNG consumption in both states
                use_moss=aged and damp and moss_roll<.19
                wood_tone=rng.randrange(3)
                tone=3 if use_moss else wood_tone
                indices.extend([tone]*6)
                moss+=int(use_moss)
                shingles+=1
    cover=mesh(coll,'09A_ShingleField',vertices,faces,mats[0]);cover['role']='roof'
    for mat in mats[1:]:cover.data.materials.append(mat)
    for face,idx in zip(cover.data.polygons,indices):face.material_index=idx
    # Two simple staggered ridge planks cover the seam and meet the slope naturally.
    for side in (-1,1):
        verts=[]
        for x,z in ((.0,ridge+.07),(.235,ridge-.105)):
            for y in (-y_end-.035,y_end+.035):
                for under in (0,.035):verts.append((side*x,y,z-under))
        ob=mesh(coll,'09A_RidgeCap',verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mats[1]);ob['role']='roof'
    return dict(shingles=shingles, courses=n_courses, moss_tinted_shingles=moss,
                exposure_m=course_step, length_m=shingle_length,
                roof_materials=len(mats))


collections={}; data={}
for state in ('CLEAN','AGED'):
    t=time.perf_counter()
    coll,_=generate(p,'09A_'+state,refine_eave=False)
    for ob in list(coll.objects):
        if ob.get('role')=='roof':bpy.data.objects.remove(ob,do_unlink=True)
    extra=roof_geometry(coll,state=='AGED')
    bpy.context.view_layer.update()
    roof=[o for o in coll.objects if o.get('role')=='roof']
    other=[o for o in coll.objects if not o.get('role')=='roof']
    collections[state]=coll
    data[state]=dict(roof_triangles=tri(roof),total_triangles=tri(coll.objects),
        materials=len({m.as_pointer() for o in coll.objects for m in o.data.materials}),
        generation_ms_single_run=round((time.perf_counter()-t)*1000,2),
        roof_objects=len(roof),**extra)
assert signature([o for o in collections['CLEAN'].objects if o.get('role')=='roof']) == signature([o for o in collections['AGED'].objects if o.get('role')=='roof'])
assert signature([o for o in collections['CLEAN'].objects if not o.get('role')=='roof']) == signature([o for o in collections['AGED'].objects if not o.get('role')=='roof'])
assert data['CLEAN']['shingles']==data['AGED']['shingles']
assert data['CLEAN']['roof_triangles']==data['AGED']['roof_triangles']

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=600
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.19,.195,.21,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.75
for name,xyz,power,size in [('Key',(0,-5,9),1000,7),('Fill',(-6,1,6),430,6)]:
    light=bpy.data.lights.new('09A_'+name,'AREA');light.energy=power;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new('09A_'+name,light);scene.collection.objects.link(ob);ob.location=xyz
    ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('09A_Camera');camdata.type='ORTHO'
cam=bpy.data.objects.new('09A_Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
views={'iso':((9,-11,8),(0,0,1.7),11.5),
       'front':((0,-13,4),(0,0,2),10.4),
       'side':((13,0,4),(0,0,2),11.5),
       'detail':((5,-3.5,5.8),(1.9,-1.5,3.0),4.8),
       'ridge_eave':((5,-3.5,4.5),(2.15,-1.2,2.9),4.0),
       'iso_300':((9,-11,8),(0,0,1.7),11.5)}
for kind,(eye,target,scale) in views.items():
    scene.render.resolution_x,scene.render.resolution_y=(480,360) if kind=='iso_300' else (800,600)
    cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.ortho_scale=scale
    for state,coll in collections.items():
        for key,c in collections.items():
            for ob in c.objects:ob.hide_render=key!=state
        scene.render.filepath=str(OUT/(state.lower()+'_'+kind+'.png'))
        bpy.ops.render.render(write_still=True)
        print('09A_RENDER',state,kind,flush=True)
for ob in collections['AGED'].objects:ob.location.y+=11
for ob in collections['CLEAN'].objects:ob.hide_render=False
for ob in collections['AGED'].objects:ob.hide_render=False
scene.render.resolution_x=800;scene.render.resolution_y=600
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'wooden_roof_09a.blend'))
(ROOT/'measurements.json').write_text(json.dumps(dict(blender=bpy.app.version_string,
    source_commit='f4f3651',configuration=vars(p),same_roof_geometry=True,
    same_nonroof_geometry=True,render_samples=12,states=data),indent=2)+'\n')
print('09A_METRICS',json.dumps(data),flush=True)
