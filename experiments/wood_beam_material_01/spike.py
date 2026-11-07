"""Disposable Blender 5.2.2 A-cottage beam comparison; NEVER save source .blend."""
import bpy,hashlib,json,math,sys,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[1];source=Path(bpy.data.filepath)
assert source.name=='three_owned_cottages.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_sha=sha(source);scene=bpy.context.scene
owner=next(c for c in scene.collection.children if any(o.type=='EMPTY' and o.parent is None and tuple(round(v,3) for v in o.location)==(0,0,0) for o in c.objects))
root=next(o for o in owner.objects if o.type=='EMPTY' and o.parent is None)
meshes=sorted((o for o in owner.all_objects if o.type=='MESH'),key=lambda o:o.name)
assert len(meshes)==37
sys.path.insert(0,str(R));sys.dont_write_bytecode=True
from building import collect_building_geometry
assert collect_building_geometry(root,owner).triangles==14054
mats={k:next(m for o in meshes for m in o.data.materials if m and m.name=='08A_09F_A_'+k) for k in ('clay','weathered_oak','stone','door')}
beam_types=('08A_CornerPost','08A_SideWallPlate','08A_EndWallPlate','08A_SideBrace','08A_GableRafter')
beams=[o for o in meshes if o.name.startswith(beam_types)]
assert len(beams)==16 and all(any(m is mats['weathered_oak'] for m in o.data.materials) for o in beams)
original_state={o.name:(tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world),tuple(m.name for m in o.data.materials)) for o in meshes}
mat_node_state={m.name:(tuple((n.name,n.type) for n in m.node_tree.nodes),tuple((l.from_node.name,l.to_node.name) for l in m.node_tree.links)) for m in mats.values()}
foreign={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in scene.objects if o.type=='MESH' and o not in meshes}
original_select=(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects))
original_camera=scene.camera
export_args={'export_format':'GLB','use_selection':True,'export_yup':True,'export_apply':False,'export_materials':'EXPORT','export_cameras':False,'export_lights':False,'export_extras':True}
report={'source_sha256_before':original_sha,'reference_09k_sha256':sha(R/'experiments/stone_door_export_09k/godot_test/assets/stone_door_constant_A.glb'),'baked':{},'beams':{},'export_args':export_args,'variants':{}}
assert report['reference_09k_sha256']==sha(P/'godot_test/assets/beam_A_baseline.glb')

# Bake a UV-space wood-wave node graph once, on a disposable plane; this is a bounded
# texture-bake trial, not a generator/material-pipeline change. Failing bake is reported.
def bake_procedural():
    image=bpy.data.images.new('WOOD01_bake_target',width=512,height=512,alpha=False)
    material=bpy.data.materials.new('WOOD01_wave_bake');material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
    tex=nodes.new('ShaderNodeTexCoord');wave=nodes.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='X'
    wave.inputs['Scale'].default_value=14;wave.inputs['Distortion'].default_value=2.0;wave.inputs['Detail'].default_value=2
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.105,.065,.038,1);ramp.color_ramp.elements[1].color=(.275,.177,.105,1)
    em=nodes.new('ShaderNodeEmission');out=nodes.new('ShaderNodeOutputMaterial');target=nodes.new('ShaderNodeTexImage');target.image=image
    links.new(tex.outputs['UV'],wave.inputs['Vector']);links.new(wave.outputs['Color'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],em.inputs['Color']);links.new(em.outputs[0],out.inputs['Surface']);nodes.active=target
    verts=[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)];me=bpy.data.meshes.new('WOOD01_bake_plane');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();me.uv_layers.new(name='UVMap')
    for i,uv in enumerate(((0,0),(1,0),(1,1),(0,1))):me.uv_layers.active.data[i].uv=uv
    ob=bpy.data.objects.new('WOOD01_bake_plane',me);scene.collection.objects.link(ob);me.materials.append(material)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.bake.use_clear=True;scene.render.bake.margin=4
    outcome={'resolution':[512,512],'engine':'CYCLES','type':'EMIT','wave_scale':14,'wave_distortion':2,'success':False}
    try:
        bpy.ops.object.bake(type='EMIT');image.filepath_raw=str(P/'textures/procedural_baked_512.png');image.file_format='PNG';image.save();outcome['success']=True;outcome['bytes']=(P/'textures/procedural_baked_512.png').stat().st_size
    except Exception as e:outcome['error']=str(e)
    bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me);bpy.data.materials.remove(material)
    return outcome
report['baked']=bake_procedural()
assert report['baked']['success'],report['baked']

def solid(name,rgb):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=1;bs.inputs['Metallic'].default_value=0
    return m
constants={'clay':solid('09I_A_clay_constant',(.47,.38,.28)),'weathered_oak':solid('09J_A_weathered_oak_constant',(.19,.125,.077)),'stone':solid('09K_A_stone_constant',(.31,.29,.25)),'door':solid('09K_A_door_constant',(.25,.15,.085))}

def mapped(name,texture,normal=None,rough=None):
    m=solid(name,(1,1,1));bs=m.node_tree.nodes.get('Principled BSDF');nodes=m.node_tree.nodes;links=m.node_tree.links
    bs.inputs['Base Color'].default_value=(1,1,1,1)
    img=nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(P/'textures'/texture),check_existing=True);img.image.colorspace_settings.name='sRGB';img.interpolation='Linear';links.new(img.outputs['Color'],bs.inputs['Base Color'])
    if normal:
        ni=nodes.new('ShaderNodeTexImage');ni.image=bpy.data.images.load(str(P/'textures'/normal),check_existing=True);ni.image.colorspace_settings.name='Non-Color';n=nodes.new('ShaderNodeNormalMap');links.new(ni.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],bs.inputs['Normal'])
    if rough:
        ri=nodes.new('ShaderNodeTexImage');ri.image=bpy.data.images.load(str(P/'textures'/rough),check_existing=True);ri.image.colorspace_settings.name='Non-Color';links.new(ri.outputs['Color'],bs.inputs['Roughness'])
    return m
B=mapped('WOOD01_B_rough_wood_PBR','rough_wood_diffuse_1k.jpg','rough_wood_normal_gl_1k.png','rough_wood_rough_1k.jpg')
C=mapped('WOOD01_C_wave_baked','procedural_baked_512.png')

# Box local +Z follows each beam independently of its world orientation. The same physical
# longitudinal scale (1.5 m / V tile) is used for upright, horizontal and diagonal beams.
def beam_uv(ob,variant):
    me=ob.data;uv=me.uv_layers.new(name='WOOD01_beam_local_Z');uv.active=True;coords=[v.co for v in me.vertices]
    xs=[v.x for v in coords];ys=[v.y for v in coords];zs=[v.z for v in coords]
    dx=max(xs)-min(xs);dy=max(ys)-min(ys);dz=max(zs)-min(zs)
    assert dx>0 and dy>0 and dz>0
    for poly in me.polygons:
        nx,ny,nz=poly.normal
        for li in poly.loop_indices:
            v=coords[me.loops[li].vertex_index]
            if abs(nz)>.8:u=(v.x-min(xs))/dx;vv=(v.y-min(ys))/dy
            else:
                across=((v.y-min(ys))/dy if abs(nx)>abs(ny) else (v.x-min(xs))/dx)
                u=.32+.16*across if variant=='B' else across
                vv=(v.z-min(zs))/1.5
            uv.data[li].uv=(u,vv)
    report['beams'].setdefault(variant,{})[ob.name]={'local_bounds_m':[round(dx,5),round(dy,5),round(dz,5)],'longitudinal_uv_span':round(dz/1.5,5),'long_axis_world':[round(x,5) for x in (ob.matrix_world.to_3x3() @ Vector((0,0,1))).normalized()],'uv_side_u_range':[.32,.48] if variant=='B' else [0,1]}

# Shared rendered light/camera; no source object, collection, mesh or material is changed.
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
light_data=bpy.data.lights.new('WOOD01_sun','SUN');light_data.energy=1.2
light=bpy.data.objects.new('WOOD01_sun',light_data);scene.collection.objects.link(light);light.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-25))
render_state={o:o.hide_render for o in scene.objects};
for o in render_state:o.hide_render=True
light.hide_render=False

def render(variant,view,position,target,scale):
    cam=bpy.data.objects.new('WOOD01_camera',bpy.data.cameras.new('WOOD01_camera'));scene.collection.objects.link(cam)
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.camera=cam
    scene.render.filepath=str(P/'screenshots'/f'blender_{variant}_{view}.png')
    bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True)

for variant,material,out_name in [('A',constants['weathered_oak'],None),('B',B,'beam_B_roughwood.glb'),('C',C,'beam_C_procedural.glb')]:
    coll=bpy.data.collections.new('WOOD01_disposable_'+variant);scene.collection.children.link(coll);copies={}
    for src in (root,*meshes):
        dup=src.copy();
        if src.type=='MESH':dup.data=src.data.copy()
        coll.objects.link(dup);copies[src]=dup
    for src,dup in copies.items():
        if src.parent:dup.parent=copies[src.parent]
        dup.matrix_world=src.matrix_world.copy()
        if src.type=='MESH':
            for i,mat in enumerate(src.data.materials):
                for key,original in mats.items():
                    if mat is original:dup.data.materials[i]=(material if key=='weathered_oak' and src in beams else constants[key]);break
            if src in beams and variant!='A':beam_uv(dup,variant)
            assert all(tuple(v.co)==tuple(src.data.vertices[j].co) for j,v in enumerate(dup.data.vertices))
    for dup in copies.values():dup.hide_render=False
    for view,pos,target,scale in [('detail',(5,-7,3.4),(0,-2,1.3),5.2),('distance300',(9,-10,7.5),(0,0,1.8),18.0)]:render(variant,view,pos,target,scale)
    if out_name:
        bpy.ops.object.select_all(action='DESELECT')
        for dup in copies.values():dup.select_set(True)
        bpy.context.view_layer.objects.active=copies[root];bpy.context.view_layer.update()
        out=P/'godot_test/assets'/out_name
        bpy.ops.export_scene.gltf(filepath=str(out),**export_args)
        report['variants'][variant]={'glb':out_name,'bytes':out.stat().st_size,'beam_material':material.name,'beam_mesh_count':len(beams),'beam_triangles':len(beams)*12}
    else:report['variants'][variant]={'glb':'beam_A_baseline.glb','bytes':(P/'godot_test/assets/beam_A_baseline.glb').stat().st_size,'beam_material':material.name,'beam_mesh_count':len(beams),'beam_triangles':len(beams)*12}
    for dup in copies.values():
        me=dup.data if dup.type=='MESH' else None;bpy.data.objects.remove(dup,do_unlink=True)
        if me:bpy.data.meshes.remove(me)
    bpy.data.collections.remove(coll)
    print('WOOD01_RENDER_EXPORT',variant,report['variants'][variant],flush=True)
for o,hidden in render_state.items():o.hide_render=hidden
bpy.data.objects.remove(light,do_unlink=True);scene.camera=original_camera
bpy.ops.object.select_all(action='DESELECT')
for name,selected in original_select[1]:bpy.data.objects[name].select_set(selected)
bpy.context.view_layer.objects.active=original_select[0]
assert original_select==(bpy.context.view_layer.objects.active,tuple((o.name,o.select_get()) for o in scene.objects))
assert foreign=={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in scene.objects if o.type=='MESH' and o not in meshes}
assert original_state=={o.name:(tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world),tuple(m.name for m in o.data.materials)) for o in meshes}
assert mat_node_state=={m.name:(tuple((n.name,n.type) for n in m.node_tree.nodes),tuple((l.from_node.name,l.to_node.name) for l in m.node_tree.links)) for m in mats.values()}
assert sha(source)==original_sha
report['source_sha256_after']=sha(source);report['mesh_count']=37;report['triangles']=14054
(P/'blender_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('WOOD01_BLENDER_PASS',report['baked'],flush=True)
