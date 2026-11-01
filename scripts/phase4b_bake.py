"""HouseOne-only corrected experiment; runs independent fidelity controls first.
blender -b --factory-startup -t 4 -P scripts/phase4b_bake.py
"""
import runpy,sys,time,math,json,hashlib,struct
from pathlib import Path
import bpy
from mathutils import Vector
ctx=runpy.run_path(str(Path.cwd()/'scripts/phase4b_fidelity.py'))
r,out,scene,objects,base,mesh,offset,render,source,before=[ctx[k] for k in ('r','out','scene','objects','base','fixed','offset','render','source','before')]
report=ctx['report'];assert report['polygon_bijective_match']['unmatched_original']==report['polygon_bijective_match']['unmatched_realized']==0
assert report['generated_plaster_float_comparison']['corrected']['max_abs']<1e-5
obj=objects['corrected'];original=list(mesh.materials);slot=next(i for i,m in enumerate(original) if m and m.name=='UpperFloorsPaint')
for k,x in objects.items():x.hide_render=k!='corrected'
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='PlasterBake');mesh.uv_layers.active=uv
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_mode(type='FACE');bpy.ops.mesh.select_all(action='DESELECT')
import bmesh
bm=bmesh.from_edit_mesh(mesh)
for f in bm.faces:f.select_set(f.material_index==slot)
bmesh.update_edit_mesh(mesh)
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.02,margin_method='FRACTION',area_weight=0,correct_aspect=True,scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT');mesh.uv_layers['PlasterBake'].active_render=True
assert sum(p.select for p in mesh.polygons)==1105
uv_polygons=[[list(mesh.uv_layers['PlasterBake'].data[i].uv) for i in p.loop_indices] for p in mesh.polygons if p.material_index==slot]
(out/'bake_uv.json').write_text(json.dumps(uv_polygons))
image=bpy.data.images.new('HouseOne_Phase4B_BaseColor',width=1024,height=1024,alpha=False);image.colorspace_settings.name='sRGB';image.file_format='PNG';image.filepath_raw=str(out/'HouseOne_Plaster_BaseColor.png')
sink=bpy.data.images.new('Phase4B_Sink',width=1,height=1)
for i,m in enumerate(original):
 if m:
  m=m.copy();mesh.materials[i]=m;node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image if i==slot else sink;m.node_tree.nodes.active=node
scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True;scene.render.bake.margin=8;scene.render.bake.margin_type='EXTEND';scene.render.bake.use_clear=True
scene.cycles.samples=16;scene.cycles.use_denoising=True
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes=[];times=[]
for _ in range(2):
 start=time.perf_counter();bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},uv_layer='PlasterBake');times.append(time.perf_counter()-start);image.save();hashes.append(sha(Path(image.filepath_raw)))
assert hashes[0]==hashes[1]
# Existing Phase3 constant policy, extended only to the newly retained source slots.
p3=json.loads((r/'tests/materials/phase3/HouseOne_PBR.json').read_text());material_policy={}
for i,m in enumerate(original):
 if not m:continue
 shader=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 color=p3['original_linear_colors'].get(m.name,list(shader.inputs['Base Color'].default_value) if shader else [0.5,0.5,0.5,1])
 roughness=p3['roughness'].get(m.name,float(shader.inputs['Roughness'].default_value) if shader else .8)
 mat=bpy.data.materials.new(m.name+'_Phase4B');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Roughness'].default_value=roughness;mesh.materials[i]=mat
 material_policy[m.name]=dict(color=color,roughness=roughness,policy='Phase3 constant' if m.name in p3['original_linear_colors'] else 'original Principled defaults (not procedural appearance fidelity)')
 if i==slot:
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;uvnode=mat.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map='PlasterBake';mat.node_tree.links.new(uvnode.outputs['UV'],tex.inputs['Vector']);mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
# Render identical constant policy on original GN control? Keep actual original shader controls;
# corrected bake and prior GLB are separately aligned, not mistaken for all-material fidelity.
for view in ctx['views']:render('corrected',view,'bake4b')
# Prior bake on unchanged direct mesh, aligned to the same rig.
prior=objects['phase4'];bpy.ops.object.select_all(action='DESELECT')
# Import old GLB into isolated scene; retain GLB transform, add source placement shift.
prev=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(r/'tests/baking/phase4/HouseOne_Phase4.glb'))
new=[x for x in scene.objects if x not in prev];roots=[x for x in new if x.parent not in new]
for x in roots:x.location+=offset+ctx['o'].matrix_world.translation
for x in objects.values():x.hide_render=True
for view in ctx['views']:
 # render helper hides source objects; imported prior GLB stays visible.
 eye,target,scale=ctx['views'][view];shift=offset+ctx['o'].matrix_world.translation;ctx['cam'].location=Vector(eye)+shift;ctx['cam'].rotation_euler=(Vector(target)+shift-ctx['cam'].location).to_track_quat('-Z','Y').to_euler();ctx['cam'].data.ortho_scale=scale
 scene.render.filepath=str(out/f'bake4_{view}.png');bpy.ops.render.render(write_still=True)
for x in new:bpy.data.objects.remove(x,do_unlink=True)
# Center only by transform; retain local mesh coordinates and original Generated texspace.
obj.hide_render=False;obj.location=-offset;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
path=out/'HouseOne_Phase4B.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_vertex_color='NONE')
blob=path.read_bytes();length=struct.unpack_from('<I',blob,12)[0];gltf=json.loads(blob[20:20+length]);prims=[p for m in gltf['meshes'] for p in m['primitives']];triangles=sum(gltf['accessors'][p['indices']]['count']//3 for p in prims)
assert triangles==154602 and len(gltf['materials'])==12 and len(gltf['images'])==1
plaster=next(m for m in gltf['materials'] if m['name']=='UpperFloorsPaint_Phase4B');ref=plaster['pbrMetallicRoughness']['baseColorTexture'];uvindex=ref.get('texCoord',0)
assert all('TEXCOORD_'+str(uvindex) in p['attributes'] for p in prims if gltf['materials'][p['material']]==plaster)
img=gltf['images'][gltf['textures'][ref['index']]['source']];view=gltf['bufferViews'][img['bufferView']];start=20+length+8+view.get('byteOffset',0);assert blob[start:start+view['byteLength']]==Path(image.filepath_raw).read_bytes()
# Decode GLB independently of the exporter: compare material-specific positions both ways.
mesh.calc_loop_triangles()
from mathutils.kdtree import KDTree
def decode(index):
 a=gltf['accessors'][index];v=gltf['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];stride=v.get('byteStride',struct.calcsize('<'+fmt));start=28+length+v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from('<'+fmt,blob,start+i*stride) for i in range(a['count'])]
def kd_distance(a,b):
 tree=KDTree(len(b))
 for i,v in enumerate(b):tree.insert(v,i)
 tree.balance();return max(tree.find(v)[2] for v in a)
node=next(n for n in gltf['nodes'] if 'mesh' in n);assert not any(k in node for k in ('matrix','rotation','scale'));translation=Vector(node.get('translation',[0,0,0]));glb_positions={};export_checks={}
for p in prims:
 name=gltf['materials'][p['material']]['name'].removesuffix('_Phase4B');positions=[Vector(v)+translation for v in decode(p['attributes']['POSITION'])];positions=[Vector((v.x,-v.z,v.y))+offset for v in positions];indices=decode(p['indices']);glb_positions[name]=positions
 expected=list({i for face in mesh.polygons if original[face.material_index] and original[face.material_index].name==name for i in face.vertices});expected=[mesh.vertices[i].co.copy() for i in expected]
 error=max(kd_distance(expected,positions),kd_distance(positions,expected));assert error<1e-5
 count=sum(1 for t in mesh.loop_triangles if original[t.material_index] and original[t.material_index].name==name);assert len(indices)//3==count
 if name=='UpperFloorsPaint':
  coords=decode(p['attributes']['TEXCOORD_'+str(uvindex)]);assert all(0<=u<=1 and 0<=v<=1 for u,v in coords)
 export_checks[name]=dict(triangles=count,max_bidirectional_position_error=error)
# Original triplanar inputs must remain intact on every direct-mesh plaster corner.
attribute_errors={}
for name,domain in [('LocalPosition','POINT'),('LocalNormal','CORNER')]:
 a=base.attributes[name];b=mesh.attributes[name];indices={i for p in base.polygons if base.materials[p.material_index] and base.materials[p.material_index].name=='UpperFloorsPaint' for i in (p.vertices if domain=='POINT' else p.loop_indices)}
 error=max((a.data[i].vector-b.data[i].vector).length for i in indices);attribute_errors[name]=error;assert error==0
assert sha(source)==before
metrics=dict(export_checks=export_checks,plaster_attribute_max_errors=attribute_errors,source_sha256=before,triangles=triangles,materials=len(gltf['materials']),glb_sha256=sha(path),glb_bytes=len(blob),png_sha256_runs=hashes,bake_seconds=times,embedded_png_identical=True,texture_resolution=[1024,1024],texture_reference=ref,material_policy=material_policy,uv_polygons_equal_phase4=uv_polygons==json.loads((r/'tests/baking/phase4/bake_uv.json').read_text()),png_identical_phase4=sha(Path(image.filepath_raw))==sha(r/'tests/baking/phase4/HouseOne_Plaster_BaseColor.png'),gltf=gltf)
(out/'bake_measurements.json').write_text(json.dumps(metrics,indent=2));print('PHASE4B_BAKE_COMPLETE',json.dumps({k:v for k,v in metrics.items() if k!='gltf'}),flush=True)
