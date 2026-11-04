"""0.3.0 integration, with the unchanged Phase-6 independent geometry verifier."""
import bpy, importlib, hashlib, json, math, time
from collections import Counter
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7'
M='bl_ext.mbg_variety_test.medieval_building_generator'
F=importlib.import_module(M+'.footprints');A=importlib.import_module(M+'.assets');E=importlib.import_module(M+'.exporter')
# Reuse the approved independent polygon/GLB audit, not just the exporter counters.
helpers={}
code=(ROOT/'scripts/test_addon_export06.py').read_text()
exec(compile(code[:code.index('# Source is never opened')].replace('bl_ext.mbg_export_test','bl_ext.mbg_variety_test'),'phase6_verifier','exec'),helpers)
helpers['OUT']=OUT
checked_export=helpers['checked_export']
R={'version':bpy.app.version_string,'presets':{},'tests':{},'range_samples':[]}


def signature(obj):
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);mesh=ev.to_mesh()
    digest=hashlib.sha256(str([tuple(v.co) for v in mesh.vertices]).encode()).hexdigest()
    ev.to_mesh_clear()
    instances=[(list(x.persistent_id),[list(row) for row in x.matrix_world]) for x in dg.object_instances
               if x.is_instance and x.parent and x.parent.original==obj and x.show_self]
    counts,direct,number=E.owned_counts(bpy.context,obj)
    values=helpers['state']()['objects'][obj.name]['values']
    return dict(vertices=[list(v.co) for v in obj.data.vertices],matrix=[list(row) for row in obj.matrix_world],
        shape=obj.mbg_settings.shape,width=obj.mbg_settings.width,depth=obj.mbg_settings.depth,
        schema=obj.get(F.VERSION_KEY),shape_tag=obj.get(F.SHAPE_KEY),values=values,
        evaluated_vertices_sha256=digest,triangles=sum(counts.values()),instances=number,
        instance_sha256=hashlib.sha256(json.dumps(instances).encode()).hexdigest())


def assert_quad(obj):
    assert F.controlled(obj)
    width,depth=F.dimensions(obj)
    assert abs(obj.data.polygons[0].area-width*depth)<1e-4
    assert obj.data.polygons[0].normal.z>.999 and len(obj.data.vertices)==4
    assert all(abs(v.co.z)<1e-7 for v in obj.data.vertices)
    assert all(abs(c)<1e-7 for c in E.footprint_pivot(obj))
    assert tuple(obj.scale)==(1,1,1)


bpy.context.preferences.addons[M].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
houses=[]
for i,key in enumerate(F.PRESETS):
    bpy.context.scene.cursor.location=(i*12,0,0)
    assert bpy.ops.mbg.create_house()=={'FINISHED'}
    obj=bpy.context.active_object;obj.name=key.title()
    assert obj.mbg_settings.shape=='COMPACT'
    old=signature(obj)['values']
    obj.mbg_settings.shape=key
    assert signature(obj)['values']==old,'preset changed generator parameters'
    obj.mbg_settings.seed=29;obj.mbg_settings.floors=2
    obj.mbg_settings.roof_color=(.28,.09,.045,1)
    obj.mbg_settings.paint_color=(.65,.5,.3,1)
    obj.mbg_settings.beam_color=(.07,.035,.015,1)
    assert_quad(obj)
    houses.append(obj)
assert len({o.data.as_pointer() for o in houses})==3
bpy.ops.mesh.primitive_cube_add(location=(50,0,0));foreign=bpy.context.active_object
for obj in houses:obj.select_set(True)
for key,obj in zip(F.PRESETS,houses):
    bpy.context.view_layer.objects.active=obj
    result=checked_export(obj,key.lower())
    g,_=helpers['decode_glb'](result['path'])
    mins=[g['accessors'][p['attributes']['POSITION']]['min'] for p in g['meshes'][0]['primitives']]
    maxs=[g['accessors'][p['attributes']['POSITION']]['max'] for p in g['meshes'][0]['primitives']]
    bounds=[[min(p[i] for p in mins) for i in range(3)],[max(p[i] for p in maxs) for i in range(3)]]
    R['presets'][key]=dict(width=obj.mbg_settings.width,depth=obj.mbg_settings.depth,
        height_above_floor=bounds[1][1],gltf_bounds=bounds,materials=len(g['materials']),export=result,
        signature=signature(obj))
    assert result['pivot_local']==[0,0,0]
R['tests']['all_three_independent_meshes_and_full_exports']=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'runtime/presets.blend'))
# Change only house 2; state of houses 1 and 3 must remain byte-for-byte equivalent.
a,b,c=houses
before=[signature(o) for o in houses]
b.mbg_settings.width=4.4;b.mbg_settings.seed=83;b.mbg_settings.floors=3
assert b.mbg_settings.shape=='CUSTOM'
assert signature(a)==before[0] and signature(c)==before[2] and signature(b)!=before[1]
assert_quad(b)
R['tests']['change_house2_only']=True
# Native Shift-D and Alt-D both remap their RNA self input. Explicit resize uses COW.
for linked in (False,True):
    for selected in bpy.context.selected_objects:selected.select_set(False)
    b.select_set(True);bpy.context.view_layer.objects.active=b
    old=signature(b)
    bpy.ops.object.duplicate(linked=linked)
    dupe=bpy.context.active_object;dupe.name='Duplicate test'
    assert A.socket(A.generator_modifier(dupe),'Object').value==dupe
    assert dupe.mbg_settings.shape=='CUSTOM'
    shared_before=dupe.data==b.data
    assert shared_before==linked
    dupe.mbg_settings.width=5.0
    assert dupe.data!=b.data and signature(b)==old
    E.export_house(bpy.context,dupe,OUT/'runtime/duplicate.glb',overwrite=True)
    data=dupe.data;bpy.data.objects.remove(dupe,do_unlink=True)
    if data.users==0:bpy.data.meshes.remove(data)
    R['tests']['duplicate_linked' if linked else 'duplicate_normal']=dict(self_remapped=True,shared_before=shared_before,independent_after_resize=True)
# Foreign objects cannot be resized through the globally registered PropertyGroup.
bpy.context.view_layer.objects.active=foreign
verts=[list(v.co) for v in foreign.data.vertices]
foreign.mbg_settings.width=6
assert verts==[list(v.co) for v in foreign.data.vertices] and not bpy.ops.mbg.export_house.poll()
R['tests']['foreign_object_guard']=True
# Bounded range samples; the plant switches remain original, not optimized here.
bpy.context.view_layer.objects.active=c
original=signature(c)
cases=[(3.2,3,17,1,.5),(3.2,5,17,2,1.66),(7,3,17,3,2.5),(7,5,17,2,1.66),
       (3.2,3,83,3,1.66),(3.2,5,83,3,2.5),(7,3,83,1,.5),(7,5,83,3,2.5),
       (4,3.2,29,1,1.66),(7,5,29,8,1.66)]
for width,depth,seed,floors,curve in cases:
    start=time.perf_counter();c.mbg_settings.width=width;c.mbg_settings.depth=depth
    c.mbg_settings.seed=seed;c.mbg_settings.floors=floors;c.mbg_settings.curvature=curve
    assert_quad(c);bpy.context.view_layer.update()
    counts,direct,instances=E.owned_counts(bpy.context,c)
    ev=c.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    assert len(mesh.polygons)>100 and all(math.isfinite(v) for p in mesh.vertices for v in p.co)
    degenerate=sum(p.area<1e-12 for p in mesh.polygons)
    degenerate_materials=Counter(mesh.materials[p.material_index].name for p in mesh.polygons if p.area<1e-12)
    height=max(v.co.z for v in mesh.vertices)
    ev.to_mesh_clear()
    R['range_samples'].append(dict(width=width,depth=depth,seed=seed,floors=floors,curvature=curve,
        triangles=sum(counts.values()),direct_triangles=direct,instances=instances,
        direct_zero_area_polygons=degenerate,direct_zero_area_materials=dict(degenerate_materials),
        height_above_floor=height,seconds=time.perf_counter()-start))
# Restore Wide exactly; ranges do not silently clamp the approved old floor/curve controls.
c.mbg_settings.seed=29;c.mbg_settings.floors=2;c.mbg_settings.curvature=1.66;c.mbg_settings.shape='WIDE'
assert signature(c)==original
c.mbg_settings.width=-5;c.mbg_settings.depth=900
assert abs(c.mbg_settings.width-3.2)<1e-5 and abs(c.mbg_settings.depth-5)<1e-5
assert_quad(c)
F.set_dimension(c,'width',float('nan'))
assert_quad(c)
c.mbg_settings.shape='WIDE'
R['tests']['bounds_clamp_and_nan_guard']=True
assert signature(a)==before[0] and signature(c)==before[2]
# Local dimensions must not apply/reset existing object transforms.
bpy.context.view_layer.objects.active=c
original_matrix=c.matrix_world.copy()
c.rotation_euler.z=.47;c.scale=(-1.2,.8,1.1)
bpy.context.view_layer.update();transformed_matrix=c.matrix_world.copy()
c.mbg_settings.width=6.6;c.mbg_settings.depth=4.2
bpy.context.view_layer.update()
assert c.matrix_world==transformed_matrix
transformed=checked_export(c,'transformed_rectangle')
assert transformed['pivot_local']==[0,0,0]
c.matrix_world=original_matrix;c.mbg_settings.shape='WIDE'
bpy.context.view_layer.update()
assert signature(c)==before[2]
R['tests']['resize_preserves_rotation_scale_and_translation']=True
R['transformed_export']=transformed
# Rename, registration lifecycle and serialized Custom state.
b.name='Narrow custom renamed'
addon=importlib.import_module(M)
expected=[signature(o) for o in houses]
addon.unregister();addon.unregister();addon.register();addon.register()
assert [signature(o) for o in houses]==expected
R['tests']['register_cycle']=True
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in houses:obj.select_set(True)
bpy.context.view_layer.objects.active=b
R['saved']={o.name:signature(o) for o in houses}
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'runtime/custom.blend'))
R['source_sha256']=hashlib.sha256((ROOT/'GeometryNodesFrenchHous.blend').read_bytes()).hexdigest()
(OUT/'integration.json').write_text(json.dumps(R,indent=2))
print('PHASE7_INTEGRATION_PASS',json.dumps({k:(v['width'],v['depth'],v['export']['triangles'],v['export']['bytes']) for k,v in R['presets'].items()}))
