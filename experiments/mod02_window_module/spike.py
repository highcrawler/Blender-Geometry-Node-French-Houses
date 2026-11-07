"""MOD-02: replace only middle plain infill with an actual open window module."""
import bpy,hashlib,json,math,shutil,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[1];SOURCE=Path(bpy.data.filepath)
assert SOURCE.name=='three_owned_cottages.blend'
sys.path.insert(0,str(P));sys.path.insert(0,str(R));sys.dont_write_bytecode=True
from wall_plain import WallPlain
from wall_window import WallWindow
from assemble import create_member,create_module,dispose_module
from building import collect_building_geometry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(SOURCE);scene=bpy.context.scene
source_owner=next(c for c in scene.collection.children if any(o.type=='EMPTY' and o.parent is None and tuple(round(v,3) for v in o.location)==(0,0,0) for o in c.objects))
source_root=next(o for o in source_owner.objects if o.type=='EMPTY' and o.parent is None)
source_meshes=sorted((o for o in source_owner.all_objects if o.type=='MESH'),key=lambda o:o.name)
assert (len(source_meshes),collect_building_geometry(source_root,source_owner).triangles)==(37,14054)
art=json.loads((R/'experiments/art01_medieval_timber_frame/geometry_audit.json').read_text())
mod01=json.loads((R/'experiments/mod01_modular_wall_poc/assembly_audit.json').read_text())
assert source_sha==art['source_sha256_before']==mod01['source_sha256_before']
w=mod01['wall_measurement'];edges=w['y_edges'];xcenter=w['x_center'];bottom=w['bottom']
assert len(edges)==4 and abs(w['height']-2.05)<1e-5 and abs(w['thickness']-.16)<1e-5
source_clay=next(m for o in source_meshes for m in o.data.materials if m and m.name=='08A_09F_A_clay')
source_oak=next(m for o in source_meshes for m in o.data.materials if m and m.name=='08A_09F_A_weathered_oak')
plate=next(o for o in source_meshes if o.name==art['moved_existing_plate'])
corners=sorted((o for o in source_meshes if o.name.startswith('08A_CornerPost') and o.matrix_world.translation.x>0),key=lambda o:o.matrix_world.translation.y)
assert len(corners)==2
old_sel=(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects));old_camera=scene.camera
old_collections=tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
def inventory():
 return {o.name:(tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world),tuple(m.name for m in o.data.materials)) for o in source_meshes}
old_inventory=inventory();foreign=tuple((o.name,len(o.data.vertices),len(o.data.polygons)) for o in scene.objects if o.type=='MESH' and o not in source_meshes)

def solid(name,rgb,src):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
 bs=m.node_tree.nodes.get('Principled BSDF');old=next(n for n in src.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(*rgb,1)
 for key in ('Roughness','Metallic'):bs.inputs[key].default_value=old.inputs[key].default_value
 return m
clay=solid('09I_A_clay_constant',(.47,.38,.28),source_clay)
oak=solid('09J_A_weathered_oak_constant',(.19,.125,.077),source_oak)
main=bpy.data.collections.new('MOD02_DisposableWall');scene.collection.children.link(main)
frame_coll=bpy.data.collections.new('MOD02_SharedFrame');main.children.link(frame_coll)
modules_coll=bpy.data.collections.new('MOD02_Modules');main.children.link(modules_coll)
root=bpy.data.objects.new('MOD01_WallRoot',None);main.objects.link(root);root.location=(0,0,0)

def copy_source(src):
 dup=src.copy();dup.data=src.data.copy();frame_coll.objects.link(dup);dup.parent=root;dup.matrix_world=src.matrix_world.copy()
 for i in range(len(dup.data.materials)):dup.data.materials[i]=oak
 bpy.context.view_layer.update();return dup
frame=[copy_source(o) for o in corners]
upper=copy_source(plate);mat=upper.matrix_world.copy();mat.translation.x=art['measured_wall']['new_frame_x'];upper.matrix_world=mat;bpy.context.view_layer.update();frame.append(upper)
for item in art['new_members']:frame.append(create_member(frame_coll,root,item['name'],item['endpoints_world'],item['thickness'],oak))
assert len(frame)==9

def fingerprint(objects):
 return hashlib.sha256(repr([(ob.name,tuple(tuple(v.co) for v in ob.data.vertices),tuple(tuple(p.vertices) for p in ob.data.polygons),tuple(tuple(round(float(x),6) for x in row) for row in ob.matrix_world)) for ob in objects]).encode()).hexdigest()
frame_hash=fingerprint(frame);frame_ids=[ob.as_pointer() for ob in frame]
rail_world=next(item['endpoints_world'][0][2] for item in art['new_members'] if item['name']=='ART01_MidRail')
window_bottom_world=rail_world+.12/2+.13
window_def=WallWindow(w['height'],w['thickness'],window_bottom_world-bottom)
plain_def=WallPlain(w['height'],w['thickness'])
win_width=edges[2]-edges[1]
l,r,b,t=window_def.opening(win_width)
assert window_bottom_world>rail_world+.06 and bottom+t<art['measured_wall']['plate_top_center']-.13
report={'source_sha256_before':source_sha,'mod01_reference_glb_sha256':sha(R/'experiments/mod01_modular_wall_poc/godot_test/assets/mod01_B_three_modules.glb'),
        'frame_before':frame_hash,'frame_member_count':9,'frame_member_triangles':108,
        'window_contract_measurements':{'full_width':win_width,'full_height':w['height'],'thickness':w['thickness'],'opening_local':[l,r,b,t],
          'opening_world':{'x_through':[w['x_min'],w['x_max']],'y_left_right':[edges[1]+l,edges[1]+r],'z_bottom_top':[bottom+b,bottom+t]},
          'shared_rail_center_z':rail_world,'shared_rail_top_z':rail_world+.06},'variants':{}}

scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
ld=bpy.data.lights.new('MOD02_sun','SUN');ld.energy=1.2
light=bpy.data.objects.new('MOD02_sun',ld);scene.collection.objects.link(light);light.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-25))
disposable={root,*frame};old_hidden={o:o.hide_render for o in scene.objects if o not in disposable}
for ob in old_hidden:ob.hide_render=True
for ob in disposable:ob.hide_render=True
root.hide_render=False;light.hide_render=False

def members(inst):return [inst['mesh'],*inst['parts']]
def render(name,visible,cam,target,scale):
 for ob in frame:ob.hide_render=ob not in visible
 for coll in modules_coll.children:
  for ob in coll.objects:ob.hide_render=ob not in visible
 camera=bpy.data.objects.new('MOD02_camera',bpy.data.cameras.new('MOD02_camera'));scene.collection.objects.link(camera)
 camera.location=cam;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale;scene.camera=camera
 scene.render.filepath=str(P/'screenshots'/(name+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(camera,do_unlink=True)

views={'side':((12,0,3.2),(xcenter,0,1.3),9.0),
       'iso':((8,-8,4.5),(xcenter,0,1.3),9.0),
       'detail':((7,-2.4,2.4),(xcenter,-1.2167,1.17),3.4),
       'distance300':((12,0,3.2),(xcenter,0,1.3),18.0)}
instances=[create_module(modules_coll,root,plain_def,'MOD01_Bay_'+str(i+1),edges[i],edges[i+1]-edges[i],xcenter,bottom,clay,i==0,i==2) for i in range(3)]
assert [inst['contract']['triangles'] for inst in instances]==[10,8,10]
neighbor_ids=[instances[i]['pivot'].as_pointer() for i in (0,2)]
for name,args in views.items():render('A_'+name,[*frame,*[m for inst in instances for m in members(inst)]],*args)
ref=R/'experiments/mod01_modular_wall_poc/godot_test/assets/mod01_B_three_modules.glb'
A=P/'godot_test/assets/mod02_A_three_plain.glb';shutil.copyfile(ref,A)
assert sha(ref)==sha(A)
report['variants']['A']={'meshes':12,'triangles':136,'glb_bytes':A.stat().st_size,'glb_sha256':sha(A)}
old_mid=instances.pop(1);old_contract=old_mid['contract'].copy();dispose_module(old_mid)
assert frame_hash==fingerprint(frame) and frame_ids==[ob.as_pointer() for ob in frame]
window=create_module(modules_coll,root,window_def,'MOD01_Bay_2',edges[1],win_width,xcenter,bottom,clay,False,False,oak)
instances.insert(1,window)
assert window['contract']['type']=='WALL_WINDOW' and window['contract']['connectors_local']==old_contract['connectors_local']
assert window['contract']['world_mount']==old_contract['world_mount'] and window['contract']['owned_meshes'][0]==old_contract['owned_meshes'][0]
assert len(window['parts'])==4 and len({ob.data.as_pointer() for ob in window['parts']})==4
assert [instances[i]['pivot'].as_pointer() for i in (0,2)]==neighbor_ids
assert frame_hash==fingerprint(frame) and frame_ids==[ob.as_pointer() for ob in frame]
report['window_contract']=window['contract'];report['frame_after_swap']=fingerprint(frame)
report['window_part_objects']=[{'role':p['role'],'name':window['parts'][i].name,'endpoints_local':[p['a'],p['b']],'thickness':p['thickness'],'triangles':12} for i,p in enumerate(window_def.member_specs(win_width))]
for name,args in views.items():render('B_'+name,[*frame,*[m for inst in instances for m in members(inst)]],*args)
win_visible=[*frame,*[m for inst in instances for m in members(inst)]]
render('B_window_front',win_visible,(10,0,2.8),(xcenter,0,bottom+(b+t)/2),3.8)
render('B_window_oblique',win_visible,(7,-2.7,3.1),(xcenter,0,bottom+(b+t)/2),4.4)
render('B_reveal_detail',win_visible,(5,-1.25,2.3),(xcenter,0,bottom+(b+t)/2),2.2)
# Freestanding C is generated through the same module interface, but WITH both
# outer caps: the mounted middle module intentionally omits its neighboring caps.
preview=create_module(modules_coll,root,window_def,'MOD02_StandaloneWindow',edges[1],win_width,xcenter,bottom,clay,True,True,oak)
report['standalone_contract']=preview['contract']
render('C_single_front',members(preview),(10,0,2.5),(xcenter,0,bottom+(b+t)/2),3.8)
render('C_single_oblique',members(preview),(6,-2.9,2.8),(xcenter,0,bottom+(b+t)/2),4.2)
render('C_single_back',members(preview),(-7,0,2.5),(xcenter,0,bottom+(b+t)/2),3.8)

args={'export_format':'GLB','use_selection':True,'export_yup':True,'export_apply':False,'export_materials':'EXPORT','export_cameras':False,'export_lights':False,'export_extras':True}
for variant,objects,filename in (
    ('B',[root,*frame,*[o for inst in instances for o in (inst['pivot'],*members(inst))]],'mod02_B_window_wall.glb'),
    ('C',[root,preview['pivot'],*members(preview)],'mod02_C_window_only.glb')):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=root;bpy.context.view_layer.update()
 path=P/'godot_test/assets'/filename;bpy.ops.export_scene.gltf(filepath=str(path),**args)
 meshes=[o for o in objects if o.type=='MESH']
 report['variants'][variant]={'meshes':len(meshes),'triangles':sum(len(p.vertices)-2 for ob in meshes for p in ob.data.polygons),
                              'glb_bytes':path.stat().st_size,'glb_sha256':sha(path),'materials':sorted({m.name for ob in meshes for m in ob.data.materials})}
 print('MOD02_EXPORT',variant,report['variants'][variant],flush=True)
assert report['variants']['B']['meshes']==16 and report['variants']['B']['triangles']==204
assert report['variants']['C']['meshes']==5 and report['variants']['C']['triangles']==80
dispose_module(preview)
# Replace window by the original plain definition with no frame or neighbor changes.
instances.pop(1);dispose_module(window)
restored=create_module(modules_coll,root,plain_def,'MOD01_Bay_2',edges[1],win_width,xcenter,bottom,clay,False,False)
instances.insert(1,restored)
assert restored['contract']['connectors_local']==old_contract['connectors_local']
assert restored['contract']['world_mount']==old_contract['world_mount']
assert [instances[i]['pivot'].as_pointer() for i in (0,2)]==neighbor_ids
assert fingerprint(frame)==frame_hash and [ob.as_pointer() for ob in frame]==frame_ids
render('A_restored',[*frame,*[o for inst in instances for o in members(inst)]],*views['side'])
report['swap_back']={'restored_type':restored['contract']['type'],'frame_hash_unchanged':True,'frame_object_ids_unchanged':True,'neighbor_pivot_ids_unchanged':True,'connectors_equal':True}
for inst in instances:dispose_module(inst)
for ob in frame:
 data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
bpy.data.objects.remove(root,do_unlink=True)
for coll in (modules_coll,frame_coll,main):bpy.data.collections.remove(coll)
for mat in (clay,oak):bpy.data.materials.remove(mat)
for ob,state in old_hidden.items():ob.hide_render=state
bpy.data.objects.remove(light,do_unlink=True);scene.camera=old_camera
bpy.ops.object.select_all(action='DESELECT')
for name,selected in old_sel[1]:bpy.data.objects[name].select_set(selected)
bpy.context.view_layer.objects.active=old_sel[0]
assert old_sel==(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects))
assert old_collections==tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
assert old_inventory==inventory()
assert foreign==tuple((o.name,len(o.data.vertices),len(o.data.polygons)) for o in scene.objects if o.type=='MESH' and o not in source_meshes)
assert sha(SOURCE)==source_sha
report['source_sha256_after']=sha(SOURCE);report['frame_after_swap_back']=frame_hash
(P/'assembly_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOD02_BLENDER_PASS',report['variants'],report['swap_back'],flush=True)
