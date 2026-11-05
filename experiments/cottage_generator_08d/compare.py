"""Blender 5.2.2: blender -b -t 4 -P experiments/cottage_generator_08d/compare.py"""
import sys, json, time, hashlib, math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT.parent/'cottage_generator_08a'))
sys.path.insert(0,str(ROOT.parent/'cottage_generator_08c'))
from cottage import Cottage,generate
from roofs import replace
from hybrid import replace_with_hybrid
assert bpy.app.version[:2]==(5,2)
p=Cottage(**json.loads((ROOT/'long.json').read_text()))
assert (p.width,p.depth,p.wall_height,p.roof_pitch,p.seed)==(5.1,7.3,2.3,40,23)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def triangles(obs): return sum(len(f.vertices)-2 for o in obs for f in o.data.polygons)
def signature(obs):
    h=hashlib.sha256()
    for obj in obs:
        for v in obj.data.vertices:
            h.update(repr(tuple(round(float(x),6) for x in obj.matrix_basis @ v.co)).encode())
    return h.hexdigest()
def roof_objects(c):return [o for o in c.objects if o.get('role')=='roof']
def nonroof(c):return [o for o in c.objects if not o.get('role')=='roof']
def inspect_details(c,label):
    import bmesh
    closed=0; intentional_open=0
    for obj in roof_objects(c):
        if label=='BASELINE' or obj.name.startswith('08C_SupportThatch'):
            continue
        bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
        duplicates=len(bm.faces)-len({tuple(sorted(v.index for v in face.verts)) for face in bm.faces})
        assert duplicates==0 and all(f.normal.length>.99 for f in bm.faces),obj.name
        if all(e.is_manifold for e in bm.edges):
            assert bm.calc_volume(signed=True)>0,obj.name
            closed+=1
        else:
            assert label=='VARIANT_B' and obj.name.startswith('08C_TaperedRoll')
            intentional_open+=1
        bm.free()
    return dict(closed_detail_meshes=closed,intentionally_open_detail_meshes=intentional_open)
def mesh_bytes(obs):
    # Measured raw triangle GPU-payload lower bound (XYZ float32 + triangle uint32 indices),
    # NOT Blender heap memory, textures or evaluated mesh storage.
    return sum(12*len(o.data.vertices)+12*triangles([o]) for o in obs)
def validate_support(c,label):
    import bmesh
    support=[o for o in roof_objects(c) if o.name.startswith('08A_ThickThatch' if label=='BASELINE' else '08C_SupportThatch')]
    assert len(support)==2,(label,len(support))
    result=[]
    for o in support:
        bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
        duplicate=len(bm.faces)-len({tuple(sorted(v.index for v in f.verts)) for f in bm.faces})
        nonmanifold=sum(not edge.is_manifold for edge in bm.edges)
        volume=bm.calc_volume(signed=True)
        zero_normals=sum(f.normal.length<.99 for f in bm.faces)
        result.append(dict(nonmanifold_edges=nonmanifold,duplicate_faces=duplicate,
                           signed_volume_m3=round(volume,5),invalid_normals=zero_normals))
        assert nonmanifold==duplicate==zero_normals==0 and volume>0,(label,result)
        bm.free()
    return result

all_variants={}; metrics={}
for label in ('BASELINE','VARIANT_A','VARIANT_B','VARIANT_H'):
    start=time.perf_counter()
    coll,_=generate(p,'08D_'+label)
    extra={}
    if label in ('VARIANT_A','VARIANT_B'):
        replace(coll,p,label[-1])
    elif label=='VARIANT_H':
        extra=replace_with_hybrid(coll,p)
    bpy.context.view_layer.update()
    elapsed=(time.perf_counter()-start)*1000
    all_variants[label]=coll
    roof=roof_objects(coll)
    metrics[label]=dict(total_triangles=triangles(coll.objects),roof_triangles=triangles(roof),
        materials=len({m.as_pointer() for o in coll.objects for m in o.data.materials}),
        creation_ms=round(elapsed,2),mesh_raw_payload_bytes=mesh_bytes(coll.objects),
        roof_raw_payload_bytes=mesh_bytes(roof),support_shells=validate_support(coll,label),
        all_mesh_materials_assigned=all(len(o.data.materials)>0 for o in coll.objects),
        roof_meshes=len(roof),**inspect_details(coll,label))
    if extra:
        metrics[label].update(bundle_modules=extra['bundle_modules'],component_strips=extra['component_strips'],
          support_triangles=triangles(extra['support_objects']),
          bundle_triangles=triangles(extra['bundle_objects']),
          ridge_triangles=triangles([extra['ridge_object']]))
        assert metrics[label]['roof_triangles']==sum(metrics[label][key] for key in
            ('support_triangles','bundle_triangles','ridge_triangles'))
assert metrics['BASELINE']['total_triangles']==3966 and metrics['BASELINE']['roof_triangles']==3604
assert len({signature(nonroof(c)) for c in all_variants.values()})==1
assert metrics['VARIANT_A']['intentionally_open_detail_meshes']==0
assert metrics['VARIANT_B']['intentionally_open_detail_meshes']==24
assert metrics['VARIANT_H']['intentionally_open_detail_meshes']==0
source_08c=json.loads((ROOT.parent/'cottage_generator_08c'/'measurements.json').read_text())['variants']
for label in ('VARIANT_A','VARIANT_B'):
    assert metrics[label]['roof_triangles']==source_08c[label]['roof_triangles']
    assert metrics[label]['total_triangles']==source_08c[label]['total_triangles']
assert any(m.name.startswith('08C_Fibrous') and m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].is_linked
           for o in roof_objects(all_variants['VARIANT_B']) for m in o.data.materials)
# Read-only independent comparison against the saved Phase-8B .blend asset.
source_blend=ROOT.parent/'cottage_generator_08b'/'Cottage_Thatch_08B.blend'
with bpy.data.libraries.load(str(source_blend),link=False) as (source,loaded):
    assert '08A_long_08b' in source.collections
    loaded.collections=['08A_long_08b']
archive=loaded.collections[0]
bpy.context.view_layer.update()
from collections import Counter
def object_meshes(coll):
    return Counter(signature([o]) for o in coll.objects)
assert object_meshes(archive)==object_meshes(all_variants['BASELINE']),'archived 8B geometry differs'
for obj in list(archive.objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(archive)
# A and B are also byte-quantized geometry matches of their 8C archived assets.
for label in ('VARIANT_A','VARIANT_B'):
    path=ROOT.parent/'cottage_generator_08c'/(label.lower()+'_meshes.blend')
    with bpy.data.libraries.load(str(path),link=False) as (source,loaded):
        expected='08A_08C_'+label
        assert expected in source.collections
        loaded.collections=[expected]
    previous=loaded.collections[0]
    assert object_meshes(previous)==object_meshes(all_variants[label]),label
    for obj in list(previous.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(previous)
    metrics[label]['matches_archived_08c_blend']=True
# The required dimension sensitivity probe is transient, not a fourth house
# variant or a saved render.
probe_p=Cottage(width=5.6,depth=8.3,wall_height=p.wall_height,roof_pitch=p.roof_pitch,seed=p.seed)
probe,_=generate(probe_p,'08D_dimension_test')
probe_info=replace_with_hybrid(probe,probe_p)
assert probe_info['bundle_modules']>metrics['VARIANT_H']['bundle_modules']
assert triangles(probe_info['bundle_objects'])>metrics['VARIANT_H']['bundle_triangles']
assert max(abs(v.co.x) for o in probe_info['support_objects'] for v in o.data.vertices)>p.width/2+.34
metrics['VARIANT_H']['dimension_probe_passed']=True
metrics['VARIANT_H']['dimension_probe']={'width':probe_p.width,'depth':probe_p.depth,
    'bundle_modules':probe_info['bundle_modules'],
    'support_max_abs_x':round(max(abs(v.co.x) for o in probe_info['support_objects']
                                   for v in o.data.vertices),5)}
for obj in list(probe.objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(probe)
assert any(m.name.startswith('08D_Hybrid') and
           all(m.node_tree.nodes.get('Principled BSDF').inputs[x].is_linked for x in ('Base Color','Roughness','Normal'))
           for o in roof_objects(all_variants['VARIANT_H']) for m in o.data.materials)
assert all(abs(max((o.matrix_world@v.co).z for o in c.objects for v in o.data.vertices)-
                   max((o.matrix_world@v.co).z for o in all_variants['BASELINE'].objects for v in o.data.vertices))<.002
           for c in all_variants.values()),'building height changed'
# Canonical baseline hash follows mesh coordinates; generate a
# second copy to guard an accidental change to the original generator or seed.
for label,c in all_variants.items():
    replay,_=generate(p,'08D_replay_'+label)
    if label in ('VARIANT_A','VARIANT_B'):replace(replay,p,label[-1])
    elif label=='VARIANT_H':replace_with_hybrid(replay,p)
    bpy.context.view_layer.update()
    metrics[label]['deterministic_mesh']=signature(c.objects)==signature(replay.objects)
    assert metrics[label]['deterministic_mesh'],label
    for o in list(replay.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(replay)
# This frozen baseline geometry fingerprint is independent of collection names.
metrics['BASELINE']['reference_geometry_sha256']=signature(all_variants['BASELINE'].objects)
metrics['BASELINE']['matches_archived_08b_blend']=True
for label,collection in all_variants.items():
    archive_path=ROOT/(label.lower()+'_meshes.blend')
    bpy.data.libraries.write(str(archive_path),{collection})
    metrics[label]['saved_collection_bytes']=archive_path.stat().st_size
(ROOT/'measurements.json').write_text(json.dumps({'blender':bpy.app.version_string,'source_commit':'3749fa4',
    'configuration':vars(p),'variants':metrics},indent=2)+'\n')

scene=bpy.context.scene
scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.engine='CYCLES';scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.world.use_nodes=True
world_bg=scene.world.node_tree.nodes.get('Background')
world_bg.inputs['Color'].default_value=(.19,.195,.21,1);world_bg.inputs['Strength'].default_value=.75
scene.render.image_settings.color_mode='RGBA'
# Fixed light rig, same material lighting for every candidate.
def area(name,xyz,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=xyz
    o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
area('08D_Key',(0,-5,9),1000,7)
area('08D_Fill',(-6,1,6),430,6)
cam_data=bpy.data.cameras.new('08D_Camera')
cam=bpy.data.objects.new('08D_Camera',cam_data);scene.collection.objects.link(cam)
cam_data.type='ORTHO';scene.camera=cam
# Lights/camera never included in coll; roofs hide only via hide_render AND hide_set.
def render(label,kind,eye,target,scale,roof_only=False):
    for key,c in all_variants.items():
        for o in c.objects:
            hidden=(key!=label or (roof_only and not o.get('role')=='roof'))
            o.hide_render=hidden;o.hide_set(hidden)
    bpy.context.view_layer.update()
    cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.ortho_scale=scale
    scene.render.filepath=str(ROOT/'screenshots'/(label.lower()+'_'+kind+'.png'))
    bpy.ops.render.render(write_still=True)
    print('08D_RENDER',label,kind,flush=True)

# Material-based views: all Cycles at same 800x600, 16 samples, two area lights.
views={'iso':((9,-11,8),(0,0,1.7),11.5),
       'front':((0,-13,4),(0,0,2),10.4),
       'side':((13,0,4),(0,0,2),11.5),
       'detail':((5,-3.5,5.8),(1.9,-1.5,3.0),4.8),
       'eave':((5,-3.5,4.5),(2.15,-1.2,2.9),4.0)}
for kind,(eye,target,scale) in views.items():
    for label in all_variants: render(label,kind,eye,target,scale)
# Actual Blender renders at 480x360: the ISO building is ~300 pixels tall.
scene.render.resolution_x=480;scene.render.resolution_y=360
for label in all_variants:
    render(label,'iso_300',(9,-11,8),(0,0,1.7),11.5)
scene.render.resolution_x=800;scene.render.resolution_y=600
# Roof-only monochrome silhouette; same studio shader/view for all four.
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='SINGLE'
scene.display.shading.single_color=(.85,.85,.85)
scene.display.shading.show_shadows=False
scene.display.shading.show_cavity=False
scene.world.color=(.055,.055,.055)
for label in all_variants:
    render(label,'silhouette',(9,-11,8),(0,0,1.7),11.5,roof_only=True)
scene.render.engine='CYCLES'
# Space collections apart for inspecting the saved .blend. An actual unbiased
# comparison board is assembled from the four original identical-view renders
# by make_board.py, rather than re-lighting a long three-house scene.
for i,(label,c) in enumerate(all_variants.items()):
    for o in c.objects: o.location.x+=(i-1)*9.3
for c in all_variants.values():
    for o in c.objects: o.hide_render=False;o.hide_set(False)
bpy.context.view_layer.update()
cam.location=(14,-27,16)
cam.rotation_euler=(Vector((0,0,1.9))-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.ortho_scale=31
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Roof_Hybrid_08D.blend'))
print('08D_PASS',json.dumps(metrics),flush=True)
