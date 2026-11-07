"""ART-01 one-wall, disposable Long CLEAN A. Native Blender GLB; NEVER save source."""
import bpy,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[1];SOURCE=Path(bpy.data.filepath)
assert SOURCE.name=='three_owned_cottages.blend'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source_hash=sha(SOURCE);scene=bpy.context.scene
owner=next(c for c in scene.collection.children if any(o.type=='EMPTY' and o.parent is None and tuple(round(v,3) for v in o.location)==(0,0,0) for o in c.objects))
root=next(o for o in owner.objects if o.type=='EMPTY' and o.parent is None)
meshes=sorted((o for o in owner.all_objects if o.type=='MESH'),key=lambda o:o.name)
assert len(meshes)==37 and tuple(root.matrix_world.translation)==(0,0,0)
sys.path.insert(0,str(R));sys.dont_write_bytecode=True
from building import collect_building_geometry
collected=collect_building_geometry(root,owner)
assert (collected.triangles,len(collected.body_objects),len(collected.roof_objects))==(14054,32,5)
probe=json.loads((P/'baseline_geometry.json').read_text())
assert probe['source_sha256']==source_hash and probe['collector_triangles']==14054
mats={key:next(m for o in meshes for m in o.data.materials if m and m.name=='08A_09F_A_'+key) for key in ('clay','weathered_oak','stone','door')}
plate=next(o for o in meshes if o.name.startswith('08A_SideWallPlate') and o.matrix_world.translation.x>0)
wall=next(o for o in meshes if o.name.startswith('08A_SideClay') and max((o.matrix_world @ v.co).x for v in o.data.vertices)>2)
braces=tuple(o for o in meshes if o.name.startswith('08A_SideBrace') and o.matrix_world.translation.x>0)
assert len(braces)==2 and plate.name=='08A_SideWallPlate.001' and wall.name=='08A_SideClay.001'
assert all(probe['objects'][o.name]['center']==list(o.matrix_world.translation) for o in (plate,wall,*braces))
side=probe['objects'][wall.name];pl=probe['objects'][plate.name];sill=probe['objects']['08A_Sill']
wall_x=side['world_max'][0];y0,y1=side['world_min'][1],side['world_max'][1];length=y1-y0
z_top=(pl['world_min'][2]+pl['world_max'][2])/2;stone_top=sill['world_max'][2]
assert abs(length-7.3)<1e-4 and abs(wall_x-2.63)<1e-4 and abs(z_top-2.3)<1e-4 and abs(stone_top-.24)<1e-4
x=wall_x-.015;intermediates=[y0+length/3,y0+2*length/3]
z_sill=stone_top+.075;z_rail=side['world_min'][2]+.45*(z_top-side['world_min'][2])
# Preserve original source geometry, shader graphs, roof and foreign-house references.
def inventory(objects):
 return {o.name:{'vertices':tuple(tuple(v.co) for v in o.data.vertices),'polygons':tuple(tuple(p.vertices) for p in o.data.polygons),'slots':tuple(m.name for m in o.data.materials),'polygon_slots':tuple(p.material_index for p in o.data.polygons),'matrix':tuple(tuple(row) for row in o.matrix_world),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)} for o in objects}
original=inventory(meshes);foreign_meshes=tuple(o for o in scene.objects if o.type=='MESH' and o not in meshes);foreign=inventory(foreign_meshes)
original_selection=(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects));original_camera=scene.camera
original_collections=tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
def material_snapshot():
 result=[]
 for m in bpy.data.materials:
  if not m.use_nodes:result.append((m.name,tuple(m.diffuse_color),None));continue
  def val(i):
   v=getattr(i,'default_value',None)
   return tuple(v) if hasattr(v,'__iter__') and not isinstance(v,str) else v
  result.append((m.name,tuple(m.diffuse_color),tuple((n.name,n.type,tuple((i.name,val(i)) for i in n.inputs),tuple((e.position,tuple(e.color)) for e in n.color_ramp.elements) if n.type=='VALTORGB' else None) for n in m.node_tree.nodes),tuple(sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links))))
 return tuple(result)
original_materials=material_snapshot()
report={'source_sha256_before':source_hash,'measured_wall':{'side':'positive X, visible from Godot +X','wall_name':wall.name,'x_outer':wall_x,'y_min':y0,'y_max':y1,'wall_top':side['world_max'][2],'plate_top_center':z_top,'stone_sill_top':stone_top,'new_frame_x':x,'bay_width':length/3},'baseline':{'meshes':37,'triangles':14054,'roof_triangles':13692,'body_triangles':362},'removed_existing_braces':[o.name for o in braces],'moved_existing_plate':plate.name,'new_members':[]}

def solid(name,rgb,source_mat):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
 old=next(n for n in source_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1)
 for prop in ('Roughness','Metallic'):bs.inputs[prop].default_value=old.inputs[prop].default_value
 return m
colors={'clay':(.47,.38,.28),'weathered_oak':(.19,.125,.077),'stone':(.31,.29,.25),'door':(.25,.15,.085)}
names={'clay':'09I_A_clay_constant','weathered_oak':'09J_A_weathered_oak_constant','stone':'09K_A_stone_constant','door':'09K_A_door_constant'}
export_mats={key:solid(names[key],colors[key],mats[key]) for key in colors}

def new_box(coll,name,a,b,thick):
 length=(Vector(b)-Vector(a)).length;h=thick/2;L=length/2
 vertices=[(sx*h,sy*h,sz*L) for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)]
 faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();me.materials.append(export_mats['weathered_oak'])
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);coll.objects.link(ob)
 ob.location=(Vector(a)+Vector(b))/2;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=(Vector(b)-Vector(a)).to_track_quat('Z','Y')
 report['new_members'].append({'name':name,'endpoints_world':[list(a),list(b)],'thickness':thick,'triangles':12,'role':'load-bearing' if 'Post' in name or 'Sill' in name else ('lateral bracing' if 'Brace' in name else 'horizontal rail')})
 return ob

# Render only copies; same camera, sun, colors and render settings for A and B.
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
light_data=bpy.data.lights.new('ART01_sun','SUN');light_data.energy=1.2
light=bpy.data.objects.new('ART01_sun',light_data);scene.collection.objects.link(light);light.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-25))
original_hidden={o:o.hide_render for o in scene.objects}
for o in original_hidden:o.hide_render=True
light.hide_render=False

def render(variant,view,pos,target,ortho):
 cam=bpy.data.objects.new('ART01_camera',bpy.data.cameras.new('ART01_camera'));scene.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=ortho;scene.camera=cam
 scene.render.filepath=str(P/'screenshots'/f'blender_{variant}_{view}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)
views=[('side',(12,0,3.2),(0,0,1.3),9.0),('iso',(9,-10,7.5),(0,0,1.8),13.5),('detail',(8,-3.4,3.5),(x,-1.65,1.3),5.0),('distance300',(9,-10,7.5),(0,0,1.8),18.0)]
export_args={'export_format':'GLB','use_selection':True,'export_yup':True,'export_apply':False,'export_materials':'EXPORT','export_cameras':False,'export_lights':False,'export_extras':True}
for variant in ('A','B'):
 coll=bpy.data.collections.new('ART01_disposable_'+variant);scene.collection.children.link(coll)
 copies={}
 for src in (root,*meshes):
  dup=src.copy()
  if src.type=='MESH':dup.data=src.data.copy()
  coll.objects.link(dup);copies[src]=dup
 for src,dup in copies.items():
  if src.parent:dup.parent=copies[src.parent]
  dup.matrix_world=src.matrix_world.copy()
  if src.type=='MESH':
   for i,mat in enumerate(src.data.materials):
    for key,reference in mats.items():
     if mat is reference:dup.data.materials[i]=export_mats[key];break
 if variant=='B':
  # The two old long end braces cross a continuous mid-rail. Remove only these copies.
  for src in braces:
   ob=copies.pop(src);me=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
  cp=copies[plate];old_x=cp.matrix_world.translation.x;pos=cp.matrix_world.copy();pos.translation.x=x;cp.matrix_world=pos
  assert abs(old_x-wall_x+.08)<1e-4
  additions=[]
  def add(name,a,b,t):
   ob=new_box(coll,name,a,b,t)
   ob.parent=copies[root]
   bpy.context.view_layer.update()
   midpoint=(Vector(a)+Vector(b))/2
   assert (ob.matrix_world.translation-midpoint).length<1e-5,(name,list(ob.matrix_world.translation),list(midpoint))
   additions.append(ob)
  add('ART01_SideSill',(x,y0,z_sill),(x,y1,z_sill),.15)
  # Recess rail face 8 mm behind posts: avoid coplanar front faces and z-fighting at joints.
  add('ART01_MidRail',(x-.008,y0,z_rail),(x-.008,y1,z_rail),.12)
  for i,y in enumerate(intermediates):add('ART01_IntermediatePost_'+str(i+1),(x,y,z_sill),(x,y,z_top),.12)
  for i,y in enumerate(intermediates):
   sign=-1 if i==0 else 1
   add('ART01_KneeBrace_'+str(i+1),(x,y,z_rail+.20),(x,y+sign*length/3*.36,z_top-.025),.09)
 else:additions=[]
 active=list(copies.values())+additions
 for o in active:o.hide_render=False
 for view,pos,target,ortho in views:render(variant,view,pos,target,ortho)
 bpy.ops.object.select_all(action='DESELECT')
 for o in active:o.select_set(True)
 bpy.context.view_layer.objects.active=copies[root];bpy.context.view_layer.update()
 out=P/'godot_test/assets'/('art01_A_baseline.glb' if variant=='A' else 'art01_B_timber_frame.glb')
 bpy.ops.export_scene.gltf(filepath=str(out),**export_args)
 assert tuple(copies[root].matrix_world.translation)==(0,0,0)
 geometries=inventory([o for o in active if o.type=='MESH']);report[variant]={'mesh_count':len(geometries),'triangles':sum(v['triangles'] for v in geometries.values()),'glb_bytes':out.stat().st_size,'sha256':sha(out)}
 if variant=='B':
  original_copy={src:original[src.name] for src in meshes if src not in braces and src is not plate}
  for src,before in original_copy.items():
   now=geometries[copies[src].name]
   for key in ('vertices','polygons','polygon_slots','triangles'):
    assert now[key]==before[key],(src.name,key)
   assert max(abs(now['matrix'][r][c]-before['matrix'][r][c]) for r in range(4) for c in range(4))<2e-6,src.name
  report['unmodified_source_meshes_verified']=len(original_copy)
  assert geometries[copies[plate].name]['vertices']==original[plate.name]['vertices']
  assert abs(geometries[copies[plate].name]['matrix'][0][3]-x)<1e-5
  for item in report['new_members']:
   matrix=geometries[item['name']]['matrix']
   midpoint=(Vector(item['endpoints_world'][0])+Vector(item['endpoints_world'][1]))/2
   assert max(abs(matrix[i][3]-midpoint[i]) for i in range(3))<1e-5,item['name']
  assert (report['B']['mesh_count'],report['B']['triangles'])==(41,14102)
 for o in active:
  me=o.data if o.type=='MESH' else None;bpy.data.objects.remove(o,do_unlink=True)
  if me:bpy.data.meshes.remove(me)
 bpy.data.collections.remove(coll)
 print('ART01_EXPORT',variant,report[variant],flush=True)
for o,hidden in original_hidden.items():o.hide_render=hidden
bpy.data.objects.remove(light,do_unlink=True);scene.camera=original_camera
for material in export_mats.values():bpy.data.materials.remove(material)
bpy.ops.object.select_all(action='DESELECT')
for name,selected in original_selection[1]:bpy.data.objects[name].select_set(selected)
bpy.context.view_layer.objects.active=original_selection[0]
assert original_selection==(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects))
assert original_collections==tuple((c.name,tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections)
assert original==inventory(meshes) and foreign==inventory(foreign_meshes) and original_materials==material_snapshot()
assert sha(SOURCE)==source_hash
report['source_sha256_after']=sha(SOURCE);report['net_extra_meshes']=report['B']['mesh_count']-report['A']['mesh_count'];report['net_extra_triangles']=report['B']['triangles']-report['A']['triangles'];report['export_args']=export_args
(P/'geometry_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('ART01_BLENDER_PASS',report['net_extra_meshes'],report['net_extra_triangles'],flush=True)
