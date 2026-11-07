"""MOD-01: rebuild the ART-01 B wall with three actual local-pivot infill modules."""
import bpy,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[1];SOURCE=Path(bpy.data.filepath)
assert SOURCE.name=='three_owned_cottages.blend'
sys.path.insert(0,str(P));sys.path.insert(0,str(R));sys.dont_write_bytecode=True
from wall_plain import WallPlain
from assemble import create_member,create_module,dispose_module
from building import collect_building_geometry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(SOURCE);scene=bpy.context.scene
source_owner=next(c for c in scene.collection.children if any(o.type=='EMPTY' and o.parent is None and tuple(round(v,3) for v in o.location)==(0,0,0) for o in c.objects))
source_root=next(o for o in source_owner.objects if o.type=='EMPTY' and o.parent is None)
source_meshes=sorted((o for o in source_owner.all_objects if o.type=='MESH'),key=lambda o:o.name)
assert (len(source_meshes),collect_building_geometry(source_root,source_owner).triangles)==(37,14054)
art=json.loads((R/'experiments/art01_medieval_timber_frame/geometry_audit.json').read_text())
probe=json.loads((R/'experiments/art01_medieval_timber_frame/baseline_geometry.json').read_text())
assert art['source_sha256_before']==source_sha==probe['source_sha256']
wall=next(o for o in source_meshes if o.name==art['measured_wall']['wall_name'])
plate=next(o for o in source_meshes if o.name==art['moved_existing_plate'])
corners=sorted((o for o in source_meshes if o.name.startswith('08A_CornerPost') and o.matrix_world.translation.x>0),key=lambda o:o.matrix_world.translation.y)
assert len(corners)==2 and [round(o.matrix_world.translation.y,3) for o in corners]==[-3.65,3.65]
source_clay=next(m for m in wall.data.materials if m)
source_oak=next(m for m in plate.data.materials if m)
assert source_clay.name=='08A_09F_A_clay' and source_oak.name=='08A_09F_A_weathered_oak'

def source_inventory():
 return {o.name:(tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world),tuple(m.name for m in o.data.materials)) for o in source_meshes}
original=source_inventory();original_sel=(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects));original_camera=scene.camera
original_collections=tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
foreign=tuple((o.name,len(o.data.vertices),len(o.data.polygons)) for o in scene.objects if o.type=='MESH' and o not in source_meshes)
wall_data=probe['objects'][wall.name]
xcenter=(wall_data['world_min'][0]+wall_data['world_max'][0])/2
y_edges=[wall_data['world_min'][1]]+[item['endpoints_world'][0][1] for item in art['new_members'] if item['name'].startswith('ART01_IntermediatePost')]+[wall_data['world_max'][1]]
assert len(y_edges)==4 and all(y_edges[i]<y_edges[i+1] for i in range(3))
wall_bottom=wall_data['world_min'][2];height=wall_data['world_max'][2]-wall_bottom
thick=wall_data['world_max'][0]-wall_data['world_min'][0]
definition=WallPlain(height=height,thickness=thick)
assert abs(xcenter-2.55)<1e-5 and abs(height-2.05)<1e-5 and abs(thick-.16)<1e-5
assert all(abs(y_edges[i+1]-y_edges[i]-art['measured_wall']['bay_width'])<2e-6 for i in range(3))

# Two phase-9I/9J constant material IDs, zero new material types or texture slots.
def material(name,rgb,source):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
 bs=m.node_tree.nodes.get('Principled BSDF');old=next(n for n in source.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(*rgb,1)
 for prop in ('Roughness','Metallic'):bs.inputs[prop].default_value=old.inputs[prop].default_value
 return m
clay=material('09I_A_clay_constant',(.47,.38,.28),source_clay)
oak=material('09J_A_weathered_oak_constant',(.19,.125,.077),source_oak)
main=bpy.data.collections.new('MOD01_DisposableWall');scene.collection.children.link(main)
frame_coll=bpy.data.collections.new('MOD01_SharedFrame');main.children.link(frame_coll)
modules_coll=bpy.data.collections.new('MOD01_Modules');main.children.link(modules_coll)
root=bpy.data.objects.new('MOD01_WallRoot',None);main.objects.link(root);root.location=(0,0,0)

def copy_source(src,coll,mat):
 dup=src.copy();dup.data=src.data.copy();coll.objects.link(dup)
 dup.parent=root;dup.matrix_world=src.matrix_world.copy()
 for i in range(len(dup.data.materials)):dup.data.materials[i]=mat
 bpy.context.view_layer.update()
 return dup

frame=[copy_source(o,frame_coll,oak) for o in corners]
upper=copy_source(plate,frame_coll,oak)
mat=upper.matrix_world.copy();mat.translation.x=art['measured_wall']['new_frame_x'];upper.matrix_world=mat
bpy.context.view_layer.update();assert abs(upper.matrix_world.translation.x-art['measured_wall']['new_frame_x'])<1e-5
frame.append(upper)
for item in art['new_members']:
 ob=create_member(frame_coll,root,item['name'],item['endpoints_world'],item['thickness'],oak)
 frame.append(ob)
assert len(frame)==9 and len({o.as_pointer() for o in frame})==9
baseline_wall=copy_source(wall,main,clay)
assert tuple(root.matrix_world.translation)==(0,0,0)

# Inventory records shared ownership, assembled module local geometry and AABB contacts.
def digest(objects):
 return hashlib.sha256(repr([(o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(round(float(n),6) for n in row) for row in o.matrix_world)) for o in objects]).encode()).hexdigest()
frame_sha=digest(frame);frame_ids=[o.as_pointer() for o in frame]
report={'source_sha256_before':source_sha,'art01_geometry_sha256':sha(R/'experiments/art01_medieval_timber_frame/geometry_audit.json'),
        'reference_glb_sha256':sha(R/'experiments/art01_medieval_timber_frame/godot_test/assets/art01_B_timber_frame.glb'),
        'wall_measurement':{'x_center':xcenter,'x_min':wall_data['world_min'][0],'x_max':wall_data['world_max'][0],
                            'y_edges':y_edges,'bottom':wall_bottom,'top':wall_bottom+height,'height':height,'thickness':thick},
        'shared_frame':{'owner':'MOD01_SharedFrame','members':[{'name':o.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'material':o.data.materials[0].name} for o in frame],
                        'mesh_count':len(frame),'triangles':108,'fingerprint_before':frame_sha},
        'reused_module_definition':{'type':'WALL_PLAIN','height':height,'thickness':thick,'python_class':'WallPlain','material':clay.name},'instances':[],
        'module_pivot_convention':'local u=world +Y, v=world +Z, n=world +X; pivot=(x_center,left_y,wall_bottom)',
        'export':{'format':'GLB','native_blender':True,'use_selection':True,'export_yup':True,'export_apply':False}}

# Source and foreign buildings remain hidden for renders; never alter source geometry.
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
light_data=bpy.data.lights.new('MOD01_sun','SUN');light_data.energy=1.2
light=bpy.data.objects.new('MOD01_sun',light_data);scene.collection.objects.link(light);light.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-25))
disposable={root,baseline_wall,*frame}
original_hidden={o:o.hide_render for o in scene.objects if o not in disposable}
for o in original_hidden:o.hide_render=True
for o in disposable:o.hide_render=True
root.hide_render=False
light.hide_render=False

def render(name,visible,pos,target,ortho):
 for ob in (baseline_wall,*frame):ob.hide_render=ob not in visible
 for coll in modules_coll.children:
  for ob in coll.objects:ob.hide_render=ob not in visible
 camera=bpy.data.objects.new('MOD01_camera',bpy.data.cameras.new('MOD01_camera'));scene.collection.objects.link(camera)
 camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=ortho;scene.camera=camera
 scene.render.filepath=str(P/'screenshots'/(name+'.png'));bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(camera,do_unlink=True)

views={'side':((12,0,3.2),(xcenter,0,1.3),9.0),
       'iso':((8,-8,4.5),(xcenter,0,1.3),9.0),
       'detail':((7,-2.4,2.4),(xcenter,-1.2167,1.17),3.4),
       'distance300':((12,0,3.2),(xcenter,0,1.3),18.0)}
# Standalone closed module: reusable without needing a frame or its neighbor.
preview=create_module(modules_coll,root,definition,'MOD01_PreviewSingle',y_edges[0],y_edges[1]-y_edges[0],xcenter,wall_bottom,clay,True,True)
render('single_plain',[preview['mesh']],(12,y_edges[0]+(y_edges[1]-y_edges[0])/2,2.5),(xcenter,y_edges[0]+(y_edges[1]-y_edges[0])/2,1.3),4.0)
report['standalone_module']={'contract':preview['contract'],'triangles':preview['contract']['triangles'],'closed_caps':2}
dispose_module(preview)
# Three separate, closed, repeated instances at known offsets – not one prejoined wall mesh.
preview_instances=[]
for i in range(3):
 offset=.25*i
 preview_instances.append(create_module(modules_coll,root,definition,'MOD01_Preview_'+str(i+1),y_edges[i]+offset,y_edges[i+1]-y_edges[i],xcenter,wall_bottom,clay,True,True))
render('three_separate',[item['mesh'] for item in preview_instances],*views['side'])
report['exploded_preview_offsets_m']=[.25*i for i in range(3)]
for item in preview_instances:dispose_module(item)
render('shared_frame',[o for o in frame],*views['side'])
for view,args in views.items():render('A_'+view,[baseline_wall,*frame],*args)

# Assembly owns the ONLY shared frame; only the infill mesh is module-owned.
instances=[]
for i in range(3):
 instances.append(create_module(modules_coll,root,definition,'MOD01_Bay_'+str(i+1),y_edges[i],y_edges[i+1]-y_edges[i],xcenter,wall_bottom,clay,i==0,i==2))
assert len({x['pivot'].as_pointer() for x in instances})==3
report['instances']=[x['contract'] for x in instances]
assert [x['contract']['triangles'] for x in instances]==[10,8,10]
for view,args in views.items():render('B_'+view,[*frame,*[x['mesh'] for x in instances]],*args)
assert digest(frame)==frame_sha
# Opening test: remove middle module ID+mesh, inspect opening, reinstall same definition.
removed=instances.pop(1)
removed_contract=removed['contract'].copy()
dispose_module(removed)
assert digest(frame)==frame_sha and [o.as_pointer() for o in frame]==frame_ids
render('middle_removed',[*frame,*[x['mesh'] for x in instances]],*views['side'])
restored=create_module(modules_coll,root,definition,'MOD01_Bay_2',y_edges[1],y_edges[2]-y_edges[1],xcenter,wall_bottom,clay,False,False)
instances.insert(1,restored)
assert digest(frame)==frame_sha and [o.as_pointer() for o in frame]==frame_ids
assert restored['contract']['connectors_local']==removed_contract['connectors_local']
assert restored['contract']['world_mount']==removed_contract['world_mount']
render('middle_restored',[*frame,*[x['mesh'] for x in instances]],*views['side'])
report['opening_test']={'removed_id':removed_contract['id'],'reinstalled_id':restored['contract']['id'],
                        'same_definition':True,'frame_same_object_ids':True,'frame_sha_before_after':frame_sha,
                        'connector_and_pivot_roundtrip':True}
report['shared_frame']['fingerprint_after']=digest(frame)

args={'export_format':'GLB','use_selection':True,'export_yup':True,'export_apply':False,'export_materials':'EXPORT','export_cameras':False,'export_lights':False,'export_extras':True}
for variant,objects in [('A',[root,baseline_wall,*frame]),('B',[root,*frame,*[o for inst in instances for o in (inst['pivot'],inst['mesh'])]])]:
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=root;bpy.context.view_layer.update()
 out=P/'godot_test/assets'/('mod01_A_art01_wall.glb' if variant=='A' else 'mod01_B_three_modules.glb')
 bpy.ops.export_scene.gltf(filepath=str(out),**args)
 meshes=[o for o in objects if o.type=='MESH']
 report[variant]={'mesh_count':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
                  'materials':sorted({m.name for o in meshes for m in o.data.materials}), 'glb_sha256':sha(out),'glb_bytes':out.stat().st_size}
 print('MOD01_EXPORT',variant,report[variant],flush=True)
assert (report['A']['mesh_count'],report['A']['triangles'])==(10,120)
assert (report['B']['mesh_count'],report['B']['triangles'])==(12,136)
assert report['A']['materials']==report['B']['materials']==['09I_A_clay_constant','09J_A_weathered_oak_constant']
# Clean disposable Blender IDs to verify the source collection, meshes, materials, and other houses.
for item in instances:dispose_module(item)
data=baseline_wall.data;bpy.data.objects.remove(baseline_wall,do_unlink=True);bpy.data.meshes.remove(data)
for ob in frame:
 data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
bpy.data.objects.remove(root,do_unlink=True)
for coll in (modules_coll,frame_coll,main):bpy.data.collections.remove(coll)
for mat in (clay,oak):bpy.data.materials.remove(mat)
for ob,hidden in original_hidden.items():ob.hide_render=hidden
bpy.data.objects.remove(light,do_unlink=True)
scene.camera=original_camera
bpy.ops.object.select_all(action='DESELECT')
for name,selected in original_sel[1]:bpy.data.objects[name].select_set(selected)
bpy.context.view_layer.objects.active=original_sel[0]
assert original_sel==(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects))
assert original_collections==tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
assert original==source_inventory()
assert foreign==tuple((o.name,len(o.data.vertices),len(o.data.polygons)) for o in scene.objects if o.type=='MESH' and o not in source_meshes)
assert source_sha==sha(SOURCE)
report['source_sha256_after']=sha(SOURCE)
(P/'assembly_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOD01_BLENDER_PASS',report['A']['mesh_count'],report['B']['mesh_count'],report['opening_test'],flush=True)
