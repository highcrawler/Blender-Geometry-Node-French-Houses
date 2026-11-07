"""One ART-01 knee brace only: A original, B aged geometry, C aged geometry and baked procedural oak."""
import bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[1];SOURCE=Path(bpy.data.filepath)
assert SOURCE.name=='three_owned_cottages.blend'
sys.path.insert(0,str(P));sys.path.insert(0,str(R));sys.dont_write_bytecode=True
from assemble import create_member,create_module,dispose_module
from wall_plain import WallPlain
from wall_window import WallWindow
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
source_sha=sha(SOURCE);scene=bpy.context.scene
src_owner=next(c for c in scene.collection.children if any(o.type=='EMPTY' and o.parent is None and tuple(round(v,3) for v in o.location)==(0,0,0) for o in c.objects))
source_meshes=sorted((o for o in src_owner.all_objects if o.type=='MESH'),key=lambda o:o.name)
assert len(source_meshes)==37
original={o.name:(tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world)) for o in source_meshes}
original_hidden={o.name:o.hide_render for o in scene.objects}
original_selected=(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects));original_camera=scene.camera
art=json.loads((R/'experiments/art01_medieval_timber_frame/geometry_audit.json').read_text())
mod=json.loads((R/'experiments/mod01_modular_wall_poc/assembly_audit.json').read_text());w=mod['wall_measurement'];edges=w['y_edges']
brace_spec=next(item for item in art['new_members'] if item['name']=='ART01_KneeBrace_1')
a,b=[Vector(v) for v in brace_spec['endpoints_world']];length=(b-a).length;thick=brace_spec['thickness'];unit=(b-a).normalized()
assert abs(thick-.09)<1e-7 and length>1.2
material_source={key:next(m for o in source_meshes for m in o.data.materials if m and m.name=='08A_09F_A_'+key) for key in ('clay','weathered_oak')}
def solid(name,rgb,src):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1)
 for field in ('Metallic','Roughness'):bs.inputs[field].default_value=next(n for n in src.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs[field].default_value
 return m
clay=solid('09I_A_clay_constant',(.47,.38,.28),material_source['clay']);oak=solid('09J_A_weathered_oak_constant',(.19,.125,.077),material_source['weathered_oak'])
report={'source_sha256_before':source_sha,'MOD02_reference_sha256':sha(R/'experiments/mod02_window_module/godot_test/assets/mod02_B_window_wall.glb'),
        'brace':{'name':brace_spec['name'],'endpoints_world':[list(a),list(b)],'length_m':length,'thickness_m':thick,
                 'local_Z_world':list(unit),'local_X_world':None,'local_Y_world':None,
                 'original_vertices':8,'original_triangles':12,'material':oak.name},'variants':{},'modifiers':{},'bake':{}}
main=bpy.data.collections.new('ART_BEAM_01_disposable');scene.collection.children.link(main)
frame_coll=bpy.data.collections.new('ART_BEAM_01_Frame');main.children.link(frame_coll)
modules_coll=bpy.data.collections.new('ART_BEAM_01_Modules');main.children.link(modules_coll)
root=bpy.data.objects.new('MOD01_WallRoot',None);main.objects.link(root)
plate=next(o for o in source_meshes if o.name==art['moved_existing_plate'])
corners=sorted((o for o in source_meshes if o.name.startswith('08A_CornerPost') and o.matrix_world.translation.x>0),key=lambda o:o.matrix_world.translation.y)
def copy_source(ob):
 out=ob.copy();out.data=ob.data.copy();frame_coll.objects.link(out);out.parent=root;out.matrix_world=ob.matrix_world.copy()
 for i in range(len(out.data.materials)):out.data.materials[i]=oak
 bpy.context.view_layer.update();return out
frame=[copy_source(o) for o in corners];top=copy_source(plate);m=top.matrix_world.copy();m.translation.x=art['measured_wall']['new_frame_x'];top.matrix_world=m;bpy.context.view_layer.update();frame.append(top)
for spec in art['new_members']:frame.append(create_member(frame_coll,root,spec['name'],spec['endpoints_world'],spec['thickness'],oak))
brace=next(o for o in frame if o.name==brace_spec['name'])
assert len(frame)==9 and len(brace.data.vertices)==8 and len(brace.data.polygons)==6
matrix=brace.matrix_world.to_3x3().normalized()
report['brace']['local_X_world']=list(matrix @ Vector((1,0,0)));report['brace']['local_Y_world']=list(matrix @ Vector((0,1,0)))
assert ((matrix@Vector((0,0,1)))-unit).length<1e-5
assert (brace.matrix_world.translation-(a+b)/2).length<1e-5
assert max(abs(v.co.z) for v in brace.data.vertices)-length/2<1e-6
rail=next(s['endpoints_world'][0][2] for s in art['new_members'] if s['name']=='ART01_MidRail')
window=WallWindow(w['height'],w['thickness'],rail+.06+.13-w['bottom']);plain=WallPlain(w['height'],w['thickness'])
instances=[create_module(modules_coll,root,window if i==1 else plain,'MOD01_Bay_'+str(i+1),edges[i],edges[i+1]-edges[i],w['x_center'],w['bottom'],clay,i==0,i==2,oak if i==1 else None) for i in range(3)]
initial_non_target=[o for o in frame if o is not brace]+[o for instance in instances for o in (instance['mesh'],*instance['parts'])]
def digest(objects):return hashlib.sha256(repr([(o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(round(float(t),6) for t in row) for row in o.matrix_world),tuple(m.name for m in o.data.materials)) for o in objects]).encode()).hexdigest()
untouched=digest(initial_non_target);id_list=[o.as_pointer() for o in initial_non_target];original_brace_mesh=brace.data
for name in original_hidden:bpy.data.objects[name].hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
light_data=bpy.data.lights.new('ART_BEAM_sun','SUN');light_data.energy=1.2
light=bpy.data.objects.new('ART_BEAM_sun',light_data);scene.collection.objects.link(light);light.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-25))

def render(label,view,cam,target,scale,isolated=False):
 for o in (*frame,*[mesh for inst in instances for mesh in (inst['mesh'],*inst['parts'])]):o.hide_render=(isolated and o is not brace)
 c=bpy.data.objects.new('ART_BEAM_camera',bpy.data.cameras.new('ART_BEAM_camera'));scene.collection.objects.link(c)
 c.location=cam;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;scene.camera=c
 scene.render.filepath=str(P/'screenshots'/f'blender_{label}_{view}.png');bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True)
views={'distance300':((12,0,3.2),(w['x_center'],0,1.3),18.,False),
       'side':((12,0,3.2),(w['x_center'],0,1.3),9.,False),
       'joint':((5,-3,2.8),tuple((a+b)/2),1.7,False),
       'isolated':((5,-3,2.8),tuple((a+b)/2),1.7,True)}

def bake_uv(target):
 bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025)
 bpy.ops.object.mode_set(mode='OBJECT');assert target.data.uv_layers.active is not None

def aged_geometry(ob):
 # Subdivide first to give Clouds actual midspan vertices; vgroup fades both ends.
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True);bm.to_mesh(ob.data);bm.free();ob.data.update()
 vg=ob.vertex_groups.new(name='ART_BEAM_end_fade')
 for vertex in ob.data.vertices:
  d=length/2-abs(vertex.co.z);vg.add([vertex.index],max(0.,min(1.,d/.16)),'REPLACE')
 tex=bpy.data.textures.new('ART_BEAM_displacement_clouds',type='CLOUDS');tex.noise_scale=.23;tex.noise_depth=2
 disp=ob.modifiers.new('ART_BEAM_Clouds_ends_faded','DISPLACE');disp.texture=tex;disp.texture_coords='LOCAL';disp.strength=.0015;disp.mid_level=.5;disp.vertex_group=vg.name
 bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=disp.name)
 bevel=ob.modifiers.new('ART_BEAM_edge_break','BEVEL');bevel.width=.004;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.5
 bpy.ops.object.modifier_apply(modifier=bevel.name)
 ob.data.update()
 bm=bmesh.new();bm.from_mesh(ob.data)
 assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
 bm.free()
 bake_uv(ob)
 # Geometric end planes: no shifted end-face center, no retreat of end cuts.
 zs=[v.co.z for v in ob.data.vertices]
 assert min(zs)>=-length/2-1e-5 and max(zs)<=length/2+1e-5
 assert abs(min(zs)+length/2)<1e-4 and abs(max(zs)-length/2)<1e-4
 assert all(abs(v.co.x)<thick/2+.004 and abs(v.co.y)<thick/2+.004 for v in ob.data.vertices)
 report['modifiers']={'subdivision_cuts':2,'subdivision_grid_fill':True,'displace_type':'CLOUDS','displace_strength_m':.0015,
                      'displace_noise_scale_m':.23,'displace_noise_depth':2,'vertex_fade_end_length_m':.16,
                      'bevel_width_m':.004,'bevel_segments':3,'bevel_angle_limit_radians':.5,'modifier_applied_before_GLTF':True}
 return tex

def procedural():
 m=solid('ART_BEAM_C_bake_source',(.19,.125,.077),material_source['weathered_oak']);nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
 coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(5.,5.,.05)
 vor=nodes.new('ShaderNodeTexVoronoi');vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=1.
 noise_map=nodes.new('ShaderNodeMapping');noise_map.inputs['Scale'].default_value=(11.,11.,.4)
 noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.;noise.inputs['Detail'].default_value=2.
 links.new(coord.outputs['Object'],mapping.inputs['Vector']);links.new(mapping.outputs['Vector'],vor.inputs['Vector'])
 links.new(coord.outputs['Object'],noise_map.inputs['Vector']);links.new(noise_map.outputs['Vector'],noise.inputs['Vector'])
 ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=0.;ramp.color_ramp.elements[0].color=(0,0,0,1)
 ramp.color_ramp.elements[1].position=.020;ramp.color_ramp.elements[1].color=(1,1,1,1)
 links.new(vor.outputs['Distance'],ramp.inputs['Fac'])
 # Dark = recessed crack; bright = warm surface. Noise adds only slight weathering.
 weather=nodes.new('ShaderNodeValToRGB');weather.color_ramp.elements[0].position=.30;weather.color_ramp.elements[0].color=(.145,.09,.056,1)
 weather.color_ramp.elements[1].position=.72;weather.color_ramp.elements[1].color=(.235,.162,.112,1)
 links.new(noise.outputs['Fac'],weather.inputs['Fac'])
 mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(.055,.029,.017,1)
 links.new(ramp.outputs['Color'],mix.inputs[0]);links.new(weather.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
 bump1=nodes.new('ShaderNodeBump');bump1.inputs['Strength'].default_value=.05;bump1.inputs['Distance'].default_value=.001
 links.new(noise.outputs['Fac'],bump1.inputs['Height'])
 bump2=nodes.new('ShaderNodeBump');bump2.inputs['Strength'].default_value=.18;bump2.inputs['Distance'].default_value=.0018
 links.new(ramp.outputs['Color'],bump2.inputs['Height']);links.new(bump1.outputs['Normal'],bump2.inputs['Normal']);links.new(bump2.outputs['Normal'],bs.inputs['Normal'])
 report['shader']={'voronoi_feature':'DISTANCE_TO_EDGE','coordinates':'Object local XYZ','mapping_scale':[5.,5.,.05],
                   'crack_ramp_black_at':0.,'crack_ramp_white_at':.020,'dark_is_recessed':True,
                   'grain_noise_mapping':[11.,11.,.4],'grain_noise_scale':3.,'noise_bump_strength':.05,'noise_bump_distance_m':.001,
                   'crack_bump_strength':.18,'crack_bump_distance_m':.0018,'metallic':0.,'roughness':1.,'pointiness':False}
 return m

def bake_both(ob,src):
 # Bake on evaluated, modifier-applied geometry using its final UV islands.
 image=bpy.data.images.new('ART_BEAM_color_512',width=512,height=512,alpha=False)
 ns=src.node_tree.nodes;target=ns.new('ShaderNodeTexImage');target.image=image;ns.active=target
 ob.data.materials.clear();ob.data.materials.append(src)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 scene.cycles.samples=16;scene.render.bake.use_clear=True;scene.render.bake.margin=8
 scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
 bpy.ops.object.bake(type='DIFFUSE');image.filepath_raw=str(P/'textures/beam_color_512.png');image.file_format='PNG';image.save()
 normal=bpy.data.images.new('ART_BEAM_normal_512',width=512,height=512,alpha=False,float_buffer=False)
 target.image=normal;ns.active=target
 scene.render.bake.normal_space='TANGENT';bpy.ops.object.bake(type='NORMAL')
 normal.filepath_raw=str(P/'textures/beam_normal_512.png');normal.file_format='PNG';normal.save()
 m=solid('ART_BEAM_C_baked',(.19,.125,.077),material_source['weathered_oak']);nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
 c=nodes.new('ShaderNodeTexImage');c.image=image;c.image.colorspace_settings.name='sRGB';links.new(c.outputs['Color'],bs.inputs['Base Color'])
 n=nodes.new('ShaderNodeTexImage');n.image=normal;n.image.colorspace_settings.name='Non-Color';nm=nodes.new('ShaderNodeNormalMap')
 links.new(n.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 report['bake']={'method':'Cycles DIFFUSE color-only + NORMAL tangent-space','resolution':[512,512],'margin_px':8,'cycles_samples':16,
                 'color_png_bytes':(P/'textures/beam_color_512.png').stat().st_size,
                 'normal_png_bytes':(P/'textures/beam_normal_512.png').stat().st_size,'glTF_node_chain':'Image Texture sRGB > Principled Base Color; Image Texture Non-Color > Normal Map > Principled Normal'}
 return m

args={'export_format':'GLB','use_selection':True,'export_yup':True,'export_apply':False,'export_materials':'EXPORT','export_cameras':False,'export_lights':False,'export_extras':True}
owned=[root,*frame,*[o for inst in instances for o in (inst['pivot'],inst['mesh'],*inst['parts'])]]
reference=R/'experiments/mod02_window_module/godot_test/assets/mod02_B_window_wall.glb'
textures=[];extra_materials=[]
for label in ('A','B','C'):
 if label=='B':
  brace.data=original_brace_mesh.copy();textures.append(aged_geometry(brace))
 if label=='C':
  src=procedural();extra_materials.append(src);baked=bake_both(brace,src);extra_materials.append(baked)
  brace.data.materials.clear();brace.data.materials.append(baked)
 for view,(cam,target,scale,isolated) in views.items():render(label,view,cam,target,scale,isolated)
 out=P/'godot_test/assets'/f'beam_{label}.glb'
 if label=='A':
  out.write_bytes(reference.read_bytes());assert sha(out)==report['MOD02_reference_sha256']
 else:
  bpy.ops.object.select_all(action='DESELECT')
  for ob in owned:ob.select_set(True)
  bpy.context.view_layer.objects.active=root;bpy.context.view_layer.update();bpy.ops.export_scene.gltf(filepath=str(out),**args)
 assert digest(initial_non_target)==untouched and [o.as_pointer() for o in initial_non_target]==id_list
 assert (brace.matrix_world.translation-(a+b)/2).length<1e-5
 ntri=sum(len(poly.vertices)-2 for poly in brace.data.polygons)
 report['variants'][label]={'brace_vertices':len(brace.data.vertices),'brace_triangles':ntri,'wall_triangles':204-12+ntri,'mesh_count':16,
                           'material_count':3 if label=='C' else 2,'texture_count':2 if label=='C' else 0,
                           'glb_bytes':out.stat().st_size,'glb_sha256':sha(out),'brace_matrix':[[float(v) for v in row] for row in brace.matrix_world],
                           'endpoints_unchanged':True,'untouched_digest':untouched,'end_plane_z':[min(v.co.z for v in brace.data.vertices),max(v.co.z for v in brace.data.vertices)]}
 print('ART_BEAM_EXPORT',label,report['variants'][label]['brace_vertices'],ntri,out.stat().st_size,flush=True)
# Unlink every disposable object, without saving the original .blend.
for item in instances:dispose_module(item)
for ob in frame:
 data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
 if data is not original_brace_mesh:pass
bpy.data.objects.remove(root,do_unlink=True)
for coll in (modules_coll,frame_coll,main):bpy.data.collections.remove(coll)
for name,state in original_hidden.items():bpy.data.objects[name].hide_render=state
bpy.data.objects.remove(light,do_unlink=True);scene.camera=original_camera
bpy.ops.object.select_all(action='DESELECT')
for name,selected in original_selected[1]:bpy.data.objects[name].select_set(selected)
bpy.context.view_layer.objects.active=original_selected[0]
assert original=={o.name:(tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world)) for o in source_meshes}
assert sha(SOURCE)==source_sha
report['source_sha256_after']=sha(SOURCE)
(P/'assembly_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('ART_BEAM_BLENDER_PASS',source_sha,flush=True)
