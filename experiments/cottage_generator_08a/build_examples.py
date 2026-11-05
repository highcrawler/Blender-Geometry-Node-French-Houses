"""Run from repository root: blender -b -t 2 -P experiments/cottage_generator_08a/build_examples.py"""
import bpy, sys, json, hashlib, math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cottage import Cottage, generate, VERSION

ROOT = Path(__file__).resolve().parent
configs = json.loads((ROOT/'variants.json').read_text())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != bpy.context.scene.collection.name and c.users == 0:
        bpy.data.collections.remove(c)


def digest(coll):
    h = hashlib.sha256()
    for ob in sorted(coll.objects,key=lambda o:(o.name,tuple(o.location))):
        h.update(ob.name.encode())
        for v in ob.data.vertices:
            h.update((','.join(format(x,'.8f') for x in ob.matrix_world @ v.co)+';').encode())
    return h.hexdigest()


def stats(p,coll,mats):
    roof=[o for o in coll.objects if o.get('role')=='roof']
    triangles=lambda objs:sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in objs)
    verts=[o.matrix_world @ v.co for o in coll.objects for v in o.data.vertices]
    import bmesh
    roof_shell=[]
    for o in roof:
        if o.name.startswith('08A_ThickThatch'):
            bm=bmesh.new(); bm.from_mesh(o.data)
            roof_shell.append({'boundary_edges':sum(not e.is_manifold for e in bm.edges),
                               'faces':len(bm.faces)})
            bm.free()
    return dict(width=p.width,depth=p.depth,wall_height=p.wall_height,roof_pitch=p.roof_pitch,
                overall_height=round(max(v.z for v in verts),3),triangles_total=triangles(coll.objects),
                triangles_roof=triangles(roof),materials=len(mats),seed=p.seed,
                roof_shells=roof_shell,sha256=digest(coll))

variants=[]
for name,values in configs.items():
    p=Cottage(**values)
    coll,mats=generate(p,name)
    variants.append((name,p,coll,mats))
bpy.context.view_layer.update()
metrics={name:stats(p,coll,mats) for name,p,coll,mats in variants}
# Generate a second copy in the same scene to prove identical object meshes, not just seeded colors.
name,p,coll,mats=variants[0]
clone,_=generate(p,name+'_replay')
bpy.context.view_layer.update()
# Names/materials differ; compare the actual world-space geometry in collection order.
def geometry_signature(c):
    return hashlib.sha256(''.join(
        ';'.join(','.join(format(float(x),'.7f') for x in (o.matrix_world @ v.co)) for v in o.data.vertices)
        for o in c.objects).encode()).hexdigest()
# Blender collection iteration is name-sorted; compare after replacing replay suffix in names (identical geometry).
metrics['replay_geometry_equal']=geometry_signature(coll)==geometry_signature(clone)
assert metrics['replay_geometry_equal']
for ob in list(clone.objects): bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(clone)
assert all(all(s['boundary_edges']==0 for s in m['roof_shells']) for m in metrics.values() if isinstance(m,dict))
(ROOT/'measurements.json').write_text(json.dumps({'version':VERSION,'blender':bpy.app.version_string,'variants':metrics},indent=2)+'\n')

scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2
scene.render.resolution_x=960; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(.055,.055,.055)
cam_data=bpy.data.cameras.new('08A_Camera')
cam=bpy.data.objects.new('08A_Camera',cam_data); scene.collection.objects.link(cam); scene.camera=cam
cam_data.type='ORTHO'

def render(filename,eye,target,scale,shown):
    for _,_,c,_ in variants:
        for ob in c.objects: ob.hide_render=(c not in shown)
    cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.ortho_scale=scale
    scene.render.filepath=str(ROOT/'screenshots'/filename)
    bpy.ops.render.render(write_still=True)
    print('COTTAGE_RENDER',filename,flush=True)

for name,p,coll,_ in variants:
    render(name+'_iso.png',(9,-11,8),(0,0,1.4),10.6,[coll])
    render(name+'_front.png',(0,-12,3.7),(0,0,1.5),9.5,[coll])
# Position each example on a distinct display lane and then render all at once.
for i,(_,_,coll,_) in enumerate(variants):
    for ob in coll.objects: ob.location.x+=(i-1)*8.5
render('three_together.png',(13,-28,19),(0,0,1.3),29,[c for _,_,c,_ in variants])
# Return to origin so the saved prototypes are clean, not offset by their display positions.
for i,(_,_,coll,_) in enumerate(variants):
    for ob in coll.objects: ob.location.x-=(i-1)*8.5
render('thatch_closeup.png',(3,-5,5),(0,-1.5,3.4),5.0,[variants[2][2]])
render('timber_structure.png',(4,-7,3),(0,-2,1.35),6.5,[variants[0][2]])
for _,_,coll,_ in variants:
    for ob in coll.objects: ob.hide_render=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Cottage_Prototype_01.blend'))
print('COTTAGE_DONE',json.dumps(metrics),flush=True)
