"""Run from pristine 9F blend in Blender 5.2.2 -b -t 4 -P spike.py. Never save source."""
import bpy, json, hashlib, math, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SOURCE = Path(bpy.data.filepath)
assert SOURCE.name == 'three_owned_cottages.blend'
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
scene = bpy.context.scene
owner = next(c for c in scene.collection.children if any(o.type == 'EMPTY' and o.parent is None and tuple(round(v, 3) for v in o.location) == (0, 0, 0) for o in c.objects))
root = next(o for o in owner.objects if o.type == 'EMPTY' and o.parent is None)
meshes = sorted((o for o in owner.all_objects if o.type == 'MESH'), key=lambda o: o.name)
assert len(meshes) == 37
sys.path.insert(0,str(HERE.parents[1]))
sys.dont_write_bytecode=True  # collector import must not leave caches in the source tree
from building import collect_building_geometry
collected=collect_building_geometry(root,owner)
golden=json.loads((HERE.parents[1]/'experiments/cottage_geometry_collector_09g/collection_results.json').read_text())['houses']['A']
assert set(collected.mesh_objects)==set(meshes)
assert (collected.triangles,len(collected.body_objects),len(collected.roof_objects))==(golden['triangles'],golden['body_count'],golden['roof_count'])==(14054,32,5)
# Material identity is established from A's saved mesh slots, then checked against shader structure.
clay = next(m for o in meshes for m in o.data.materials if m and m.name == '08A_09F_A_clay')
oak = next(m for o in meshes for m in o.data.materials if m and m.name == '08A_09F_A_weathered_oak')
stone = next(m for o in meshes for m in o.data.materials if m and m.name == '08A_09F_A_stone')
door = next(m for o in meshes for m in o.data.materials if m and m.name == '08A_09F_A_door')
assert len({m.as_pointer() for m in (clay,oak,stone,door)})==4

def shader_info(mat):
    nodes=mat.node_tree.nodes
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    ramp=next(n for n in nodes if n.type=='VALTORGB')
    noise=next(n for n in nodes if n.type=='TEX_NOISE')
    assert any(l.from_node==ramp and l.to_node==bsdf and l.to_socket.name=='Base Color' for l in mat.node_tree.links)
    return {'name_diagnostic':mat.name,'node_types':sorted(n.type for n in nodes),
       'links':sorted([l.from_node.name+'.'+l.from_socket.name+' -> '+l.to_node.name+'.'+l.to_socket.name for l in mat.node_tree.links]),
       'ramp':[{'position':e.position,'linear_rgba':list(e.color)} for e in ramp.color_ramp.elements],
       'noise_scale':noise.inputs['Scale'].default_value,'noise_detail':noise.inputs['Detail'].default_value,
       'noise_vector_input':[l.from_node.name+'.'+l.from_socket.name for l in mat.node_tree.links if l.to_node==noise and l.to_socket.name=='Vector'],
       'roughness':bsdf.inputs['Roughness'].default_value,'metallic':bsdf.inputs['Metallic'].default_value,
       'meshes':[]}
audit={'collector_reference':{'meshes':37,'body':32,'roof':5,'triangles':14054,'matched_09g':True},'source_sha256_before':source_hash,
       'stone':shader_info(stone),'door':shader_info(door),'clay_reference':shader_info(clay),'oak_reference':shader_info(oak),
       'export': {'export_format':'GLB','use_selection':True,'export_yup':True,'export_apply':False,'export_materials':'EXPORT','export_cameras':False,'export_lights':False,'export_extras':True}}

def inventory(objects):
    result = {}
    for o in objects:
        me = o.data
        result[o.name] = {'vertices':[list(v.co) for v in me.vertices], 'polygons':[list(p.vertices) for p in me.polygons],
            'slots':[m.name if m else None for m in me.materials], 'polygon_slots':[p.material_index for p in me.polygons],
            'matrix':[list(row) for row in o.matrix_world], 'triangles':sum(len(p.vertices)-2 for p in me.polygons)}
    return result
original_inventory = inventory(meshes)
original_root_matrix=root.matrix_world.copy()
foreign_meshes=sorted((o for o in scene.objects if o.type=='MESH' and o not in set(meshes)),key=lambda o:o.name)
foreign_inventory=inventory(foreign_meshes)
original_context = (bpy.context.view_layer.objects.active, tuple((o.name,o.select_get()) for o in scene.objects))
original_collections=tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
def material_snapshot():
    def input_value(inp):
        if not hasattr(inp,'default_value'):return None
        v=inp.default_value
        return tuple(v) if hasattr(v,'__iter__') and not isinstance(v,str) else v
    result=[]
    for m in bpy.data.materials:
        if not m.use_nodes:result.append((m.name,m.as_pointer(),tuple(m.diffuse_color),None));continue
        nodes_snapshot=tuple((n.name,n.type,tuple((i.name,input_value(i)) for i in n.inputs),
            tuple((e.position,tuple(e.color)) for e in n.color_ramp.elements) if n.type=='VALTORGB' else None) for n in m.node_tree.nodes)
        links_snapshot=tuple(sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links))
        result.append((m.name,m.as_pointer(),tuple(m.diffuse_color),nodes_snapshot,links_snapshot))
    return tuple(result)
original_materials=material_snapshot()
for mat,key,expected in ((clay,'clay_reference',74),(oak,'oak_reference',264),(stone,'stone',12),(door,'door',12)):
    for o in meshes:
        ids=[i for i,m in enumerate(o.data.materials) if m is mat]
        if ids:
            polys=[p for p in o.data.polygons if p.material_index in ids]
            audit[key]['meshes'].append({'name':o.name,'slots':ids,'polygons':len(polys),'triangles':sum(len(p.vertices)-2 for p in polys)})
    assert sum(x['triangles'] for x in audit[key]['meshes'])==expected,(key,audit[key]['meshes'])
assert sum(v['triangles'] for v in original_inventory.values()) == 14054
# Real source reference renders, before creating any export-only material.
def render(name, position, target, ortho):
    camera = bpy.data.objects.new('09I_temp_camera', bpy.data.cameras.new('09I_temp_camera'))
    scene.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type = 'ORTHO'; camera.data.ortho_scale = ortho
    scene.camera = camera
    scene.render.filepath = str(HERE/'screenshots'/name)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
scene.render.engine='CYCLES'; scene.cycles.samples=16
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.5,0.5,0.5)
light_data=bpy.data.lights.new('09I_temp_sun','SUN'); light_data.energy=1.2
light=bpy.data.objects.new('09I_temp_sun',light_data);scene.collection.objects.link(light)
light.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-25))
foreign_render = {o:o.hide_render for o in scene.objects if o not in set(meshes)|{root,light}}
for o in foreign_render:o.hide_render=True
render('blender_original.png',(9,-10,7.5),(0,0,1.8),21.0)
render('blender_stone_door_detail.png',(5,-7,3.4),(0,-2,1.3),5.2)
for o,was_hidden in foreign_render.items():o.hide_render=was_hidden
bpy.data.objects.remove(light,do_unlink=True)
# Every copy receives its own mesh ID. No original geometry/material/object is edited.
copy_collection=bpy.data.collections.new('09K_disposable_A');scene.collection.children.link(copy_collection)
copies={}
for src in (root,*meshes):
    dup=src.copy()
    if src.type=='MESH':dup.data=src.data.copy()
    copy_collection.objects.link(dup);copies[src]=dup
for src,dup in copies.items():
    if src.parent:dup.parent=copies[src.parent]
    dup.matrix_world=src.matrix_world.copy()
export_clay=bpy.data.materials.new('09I_A_clay_constant');export_clay.use_nodes=True
export_bsdf=next(n for n in export_clay.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
export_bsdf.inputs['Base Color'].default_value=(.47,.38,.28,1)
export_bsdf.inputs['Roughness'].default_value=audit['clay_reference']['roughness']
export_bsdf.inputs['Metallic'].default_value=audit['clay_reference']['metallic']
export_clay.diffuse_color=(.47,.38,.28,1)
export_oak=bpy.data.materials.new('09J_A_weathered_oak_constant');export_oak.use_nodes=True
oak_bsdf=next(n for n in export_oak.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
oak_bsdf.inputs['Base Color'].default_value=(.19,.125,.077,1)
oak_bsdf.inputs['Roughness'].default_value=audit['oak_reference']['roughness']
oak_bsdf.inputs['Metallic'].default_value=audit['oak_reference']['metallic']
export_oak.diffuse_color=(.19,.125,.077,1)
export_stone=bpy.data.materials.new('09K_A_stone_constant');export_stone.use_nodes=True
stone_bsdf=next(n for n in export_stone.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
stone_bsdf.inputs['Base Color'].default_value=(.31,.29,.25,1)
stone_bsdf.inputs['Roughness'].default_value=audit['stone']['roughness']
stone_bsdf.inputs['Metallic'].default_value=audit['stone']['metallic']
export_stone.diffuse_color=(.31,.29,.25,1)
export_door=bpy.data.materials.new('09K_A_door_constant');export_door.use_nodes=True
door_bsdf=next(n for n in export_door.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
door_bsdf.inputs['Base Color'].default_value=(.25,.15,.085,1)
door_bsdf.inputs['Roughness'].default_value=audit['door']['roughness']
door_bsdf.inputs['Metallic'].default_value=audit['door']['metallic']
export_door.diffuse_color=(.25,.15,.085,1)
for src in meshes:
    dst=copies[src]
    assert dst.data is not src.data
    for i,m in enumerate(src.data.materials):
        if m is clay:dst.data.materials[i]=export_clay
        elif m is oak:dst.data.materials[i]=export_oak
        elif m is stone:dst.data.materials[i]=export_stone
        elif m is door:dst.data.materials[i]=export_door
# Compare exact positions/topology/indices/transforms; only four known body material IDs may differ.
copy_inventory=inventory([copies[o] for o in meshes]); changed=[]
for src in meshes:
    a=original_inventory[src.name];b=copy_inventory[copies[src].name]
    for key in ('vertices','polygons','polygon_slots','matrix','triangles'):
        assert a[key]==b[key],(src.name,key)
    for i,(before,after) in enumerate(zip(a['slots'],b['slots'])):
        if before!=after:
            assert any(src.data.materials[i] is original and copies[src].data.materials[i] is replacement for original,replacement in ((clay,export_clay),(oak,export_oak),(stone,export_stone),(door,export_door)))
            changed.append([src.name,i,before,after])
for mat,key in ((clay,'clay_reference'),(oak,'oak_reference'),(stone,'stone'),(door,'door')):
    assert sum(entry[2]==mat.name for entry in changed)==len(audit[key]['meshes'])
assert inventory(meshes)==original_inventory
assert (bpy.context.view_layer.objects.active, tuple((o.name,o.select_get()) for o in scene.objects if o in set(meshes)|{root})) == (original_context[0],tuple(x for x in original_context[1] if x[0] in {o.name for o in meshes}|{root.name}))
assert all(copies[o].data is not o.data for o in meshes)
assert all(all(m not in (export_clay,export_oak,export_stone,export_door) for m in o.data.materials) for o in meshes)
# Selection is changed only in this disposable Blender process.
bpy.ops.object.select_all(action='DESELECT')
for dup in copies.values():dup.select_set(True)
bpy.context.view_layer.objects.active=copies[root]
bpy.context.view_layer.update()
assert tuple(copies[root].location)==(0,0,0)
out=HERE/'godot_test/assets/stone_door_constant_A.glb'
bpy.ops.export_scene.gltf(filepath=str(out),**audit['export'])
audit['changed_slots']=changed
audit['geometry_same']=True
# Discard all export copies, restore original selection/active object, then check read-only source state.
for dup in copies.values():
    mesh_data=dup.data if dup.type=='MESH' else None
    bpy.data.objects.remove(dup,do_unlink=True)
    if mesh_data:bpy.data.meshes.remove(mesh_data)
bpy.data.collections.remove(copy_collection)
bpy.data.materials.remove(export_clay)
bpy.data.materials.remove(export_oak)
bpy.data.materials.remove(export_stone)
bpy.data.materials.remove(export_door)
bpy.ops.object.select_all(action='DESELECT')
for name,selected in original_context[1]:
    bpy.data.objects[name].select_set(selected)
bpy.context.view_layer.objects.active=original_context[0]
assert original_context==(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects))
assert original_collections==tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
assert original_materials==material_snapshot()
assert foreign_inventory==inventory(foreign_meshes)
assert root.matrix_world==original_root_matrix
audit['foreign_buildings_meshes_unchanged']=len(foreign_meshes)
audit['source_material_nodes_values_links_unchanged']=True
audit['source_in_memory_same']=inventory(meshes)==original_inventory
assert audit['source_in_memory_same']
audit['selection_and_collections_restored']=True
audit['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert audit['source_sha256_after']==source_hash
assert sum(v['triangles'] for v in copy_inventory.values())==14054
audit['mesh_count']=len(meshes);audit['triangles']=14054;audit['export_bytes']=out.stat().st_size
(HERE/'blender_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('09K_SUCCESS',out,{k:sum(x['triangles'] for x in audit[k]['meshes']) for k in ('clay_reference','oak_reference','stone','door')},flush=True)
