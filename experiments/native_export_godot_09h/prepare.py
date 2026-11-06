"""Blender 5.2: disposable native-export/import fixture preparation only.
Run with -b the immutable three-house blend -P this script, never save source.
"""
from pathlib import Path
import json
import sys
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from building import collect_building_geometry
OUT=Path(__file__).resolve().parent/'godot_test'/'assets'
OUT.mkdir(parents=True,exist_ok=True)

owners={}
for c in bpy.context.scene.collection.children:
    roots=[o for o in c.objects if o.type=='EMPTY' and o.parent is None]
    if len(roots)==1:
        key={(0.,0.,0.):'A',(35.,12.,0.):'B',(-15.,8.,0.):'C'}[tuple(round(x,3) for x in roots[0].location)]
        owners[key]=collect_building_geometry(roots[0],c)
assert set(owners)=={'A','B','C'}
assert [owners[k].triangles for k in ('A','B','C')]==[14054,6818,14066]
print('EXPORT_OPTIONS',[(p.identifier,str(p.default)) for p in bpy.ops.export_scene.gltf.get_rna_type().properties
      if p.identifier in ('export_format','use_selection','use_active_collection','use_active_collection_with_nested','export_yup','export_apply','export_materials','export_cameras','export_lights','export_extras','export_keep_originals')],flush=True)
report={}
for key in ('A','B','C'):
    record=owners[key]
    # Native Blender exporter selected-objects mode; including root preserves pivot.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in (*record.mesh_objects,record.building_root):obj.select_set(True)
    bpy.context.view_layer.objects.active=record.building_root
    old_loc=record.building_root.location.copy()
    old_yaw=record.building_root.rotation_euler.z
    # Isolated loaded process: place a standalone asset root at local ground origin.
    record.building_root.location=Vector((0,0,0));record.building_root.rotation_euler.z=0
    bpy.context.view_layer.update()
    glb=OUT/f'cottage_{key}.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,
                              export_yup=True,export_apply=False,export_materials='EXPORT',
                              export_cameras=False,export_lights=False,export_extras=True)
    report[key]={'glb_bytes':glb.stat().st_size,'source_triangles':record.triangles,
                 'source_meshes':len(record.mesh_objects),'root_original_location':list(old_loc),
                 'root_original_yaw':old_yaw,'root_export_location':list(record.building_root.location)}
    record.building_root.location=old_loc;record.building_root.rotation_euler.z=old_yaw
    bpy.context.view_layer.update()
    print('09H_GLB',key,report[key],flush=True)
# Save disposable .blend copies separately (not a custom GLB exporter).
for key in ('A','B','C'):
    record=owners[key]
    # 3-house copy with active owner collection tests Blender Active Collection Only.
    layer=bpy.context.view_layer.layer_collection
    active=next(child for child in layer.children if child.collection==record.building_collection)
    bpy.context.view_layer.active_layer_collection=active
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'active_{key}_three_houses.blend'),compress=True)
    # One-house copy: remove foreign collections and objects from this isolated process.
    # Reopen pristine reference on next iteration via separate blender invocation if needed.
    if key=='A':
        for other, other_result in owners.items():
            if other==key:continue
            c=other_result.building_collection
            for ob in list(c.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
            bpy.data.collections.remove(c,do_unlink=True)
        # Exclude cameras/lights/helpers from one-owner import without altering the source file.
        for ob in list(bpy.context.scene.objects):
            if ob not in set(record.mesh_objects)|{record.building_root}:
                bpy.data.objects.remove(ob,do_unlink=True)
        bpy.context.view_layer.active_layer_collection=next(child for child in bpy.context.view_layer.layer_collection.children if child.collection==record.building_collection)
        # Preserve original A root (at 0); B/C are isolated by rerunning this script with -- tag.
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'single_A.blend'),compress=True)
        break
(OUT.parent.parent/'blender_export_report.json').write_text(json.dumps(report,indent=2)+'\n')
