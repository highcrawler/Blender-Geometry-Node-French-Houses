"""From repository root: blender -b -t 2 -P experiments/cottage_generator_08b/build_compare.py"""
import bpy, sys, json, hashlib, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'cottage_generator_08a'
sys.path.insert(0,str(OLD))
from cottage import Cottage, generate, VERSION
configs=json.loads((OLD/'variants.json').read_text())
reference=json.loads((OLD/'measurements.json').read_text())['variants']
assert VERSION=='08b.1' and bpy.app.version[:2]==(5,2)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)  # Remove Blender startup Cube, camera and light.

def tris(objects):
    return sum(len(face.vertices)-2 for obj in objects for face in obj.data.polygons)

def digest(coll):
    h=hashlib.sha256()
    for ob in sorted(coll.objects,key=lambda o:(o.name,tuple(o.location))):
        h.update(ob.name.encode())
        for v in ob.data.vertices:
            h.update((','.join(format(x,'.8f') for x in ob.matrix_world @ v.co)+';').encode())
    return h.hexdigest()

def geometry_hash(coll, roof_only=False):
    h=hashlib.sha256()
    for ob in coll.objects:
        if roof_only and not ob.get('role')=='roof': continue
        if not roof_only and ob.get('role')=='roof': continue
        h.update(ob.name.split('.')[0].encode())
        for v in ob.data.vertices:
            h.update(repr(tuple(round(x,6) for x in ob.matrix_world @ v.co)).encode())
    return h.hexdigest()

def inspect_roof(coll):
    import bmesh
    issues=[]; shells=[]
    for ob in coll.objects:
        if not ob.name.startswith('08A_ThickThatch'): continue
        bm=bmesh.new(); bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        boundary=sum(not e.is_manifold for e in bm.edges)
        duplicate=len(bm.faces)-len({tuple(sorted(v.index for v in f.verts)) for f in bm.faces})
        volume=bm.calc_volume(signed=True)
        # Signed face orientation and nonzero volume independently check winding.
        if boundary or duplicate or volume<=0: issues.append((ob.name,boundary,duplicate,volume))
        shells.append(dict(boundary_edges=boundary,duplicate_faces=duplicate,signed_volume=round(volume,4),
                           inverted_faces=sum(f.normal.length<.99 for f in bm.faces)))
        bm.free()
    assert len(shells)==2 and not issues,issues
    return shells

base={}; refined={}; measurements={}
# Build all baselines FIRST so the Blender object names match 8A exactly.
for name,values in configs.items():
    p=Cottage(**values)
    coll,_=generate(p,name,refine_eave=False)
    base[name]=coll
bpy.context.view_layer.update()
for name,coll in base.items():
    assert digest(coll)==reference[name]['sha256'], ('8A baseline changed',name,digest(coll))
    assert tris(coll.objects)==reference[name]['triangles_total']
for name,values in configs.items():
    p=Cottage(**values)
    coll,_=generate(p,name+'_08b')
    refined[name]=coll
bpy.context.view_layer.update()
for name,coll in refined.items():
    before=base[name]
    assert geometry_hash(before)==geometry_hash(coll),('non-roof geometry changed',name)
    def immutable_roof_parts(c):
        return [o for o in c.objects if o.get('role')=='roof' and not o.name.startswith('08A_ThickThatch')]
    def part_coordinates(parts):
        return [tuple(tuple(round(x,6) for x in o.matrix_world @ v.co)
                      for v in o.data.vertices) for o in parts]
    assert part_coordinates(immutable_roof_parts(before))==part_coordinates(immutable_roof_parts(coll)),name
    assert sorted(tuple(round(x,6) for x in m.diffuse_color) for m in {mat for o in before.objects for mat in o.data.materials})==sorted(tuple(round(x,6) for x in m.diffuse_color) for m in {mat for o in coll.objects for mat in o.data.materials}),name
    shells=inspect_roof(coll)
    roof=[o for o in coll.objects if o.get('role')=='roof']
    before_roof=[o for o in before.objects if o.get('role')=='roof']
    total=tris(coll.objects); roof_tri=tris(roof)
    delta=total-reference[name]['triangles_total']
    assert delta==roof_tri-reference[name]['triangles_roof']
    assert delta <= int(reference[name]['triangles_total']*.16),(name,delta)
    measurements[name]=dict(parameters=configs[name],before_total=reference[name]['triangles_total'],
        after_total=total,added_triangles=delta,before_roof=reference[name]['triangles_roof'],
        after_roof=roof_tri,shells=shells,unchanged_non_roof=True,
        unchanged_existing_roof_parts=True,unchanged_material_colors=True)
# Run repeat generation AFTER the measured examples: one clone per seed.
for name,values in configs.items():
    replay,_=generate(Cottage(**values),name+'_replay')
    bpy.context.view_layer.update()
    assert geometry_hash(refined[name],roof_only=True)==geometry_hash(replay,roof_only=True),name
    for o in list(replay.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(replay)
    measurements[name]['seed_replay']=True
(ROOT/'measurements.json').write_text(json.dumps({'blender':bpy.app.version_string,
    'version':VERSION,'baseline':'666a567','variants':measurements},indent=2)+'\n')
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2
scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(.055,.055,.055)
cam_data=bpy.data.cameras.new('08B_ComparisonCamera')
cam=bpy.data.objects.new('08B_ComparisonCamera',cam_data);scene.collection.objects.link(cam);scene.camera=cam
cam_data.type='ORTHO'
collections=list(base.values())+list(refined.values())

def render(filename,eye,target,scale,shown,roof_only=False):
    for c in collections:
        for o in c.objects:
            hidden=(c not in shown or (roof_only and not o.get('role')=='roof'))
            o.hide_render=hidden
            o.hide_set(hidden)
    bpy.context.view_layer.update()
    cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.ortho_scale=scale
    scene.render.filepath=str(ROOT/'screenshots'/filename)
    bpy.ops.render.render(write_still=True)
    print('08B_RENDER',filename,flush=True)

# Exact Phase 8A single-view cameras, studio setup, orthographic scales and resolution.
for name in configs:
    for label,collection in [('before',base[name]),('after',refined[name])]:
        render(f'{name}_{label}.png',(9,-11,8),(0,0,1.4),10.6,[collection])
# A matching material-free roof-silhouette series, with fixed projection and lighting.
scene.display.shading.color_type='SINGLE'
scene.display.shading.single_color=(.9,.9,.9)
scene.display.shading.show_shadows=False
scene.display.shading.show_cavity=False
for name in configs:
    for label,collection in [('before',base[name]),('after',refined[name])]:
        render(f'{name}_silhouette_{label}.png',(9,-11,8),(0,0,1.4),10.6,[collection],roof_only=True)
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
for label,collection in [('before',base['steep_roof']),('after',refined['steep_roof'])]:
    render(f'eave_close_{label}.png',(5,-3.5,4.5),(2.15,-1.2,2.9),4.0,[collection])
# One common display camera; collection offsets are restored before saving.
for i,name in enumerate(configs):
    for o in refined[name].objects: o.location.x+=(i-1)*8.5
render('three_after.png',(13,-28,19),(0,0,1.3),29,list(refined.values()))
for i,name in enumerate(configs):
    for o in refined[name].objects: o.location.x-=(i-1)*8.5
for c in collections:
    for o in c.objects:
        o.hide_render=False
        o.hide_set(False)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Cottage_Thatch_08B.blend'))
print('08B_PASS',json.dumps(measurements),flush=True)
