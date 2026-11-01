"""Bounded HouseOne experiment. Source is read, never saved; all edits are RAM copies.
Run from repo root with Blender -b --factory-startup -t 4 -P this_script.
"""
import bpy, json, hashlib, struct, math, sys
from pathlib import Path
from collections import Counter
from mathutils import Vector
r=Path.cwd();out=r/'tests/baking/phase4b';out.mkdir(parents=True,exist_ok=True)
source=r/'GeometryNodesFrenchHous.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects['HouseOne'];deps=bpy.context.evaluated_depsgraph_get()
# Snapshot evaluated direct mesh and all leaf meshes owned by HouseOne before adding copies.
def snapshot(obj):return bpy.data.meshes.new_from_object(obj,preserve_all_data_layers=True,depsgraph=deps)
base=snapshot(o.evaluated_get(deps));parts=[(base,o.matrix_world.copy())];instances=[];leaf_cache={}
for inst in deps.object_instances:
 if inst.is_instance and inst.parent and inst.parent.original==o and inst.show_self:
  assert inst.object.type=='MESH',inst.object.type
  key=inst.object.data.as_pointer()
  if key not in leaf_cache:leaf_cache[key]=inst.object.data.copy()
  m=leaf_cache[key];parts.append((m,inst.matrix_world.copy()));instances.append(dict(persistent_id=list(inst.persistent_id),matrix=[list(x) for x in inst.matrix_world],materials=[x.name if x else None for x in m.materials],vertices=len(m.vertices),faces=len(m.polygons)))
# Independent C: append a fresh wrapper, never edit GenerateHouse or its subgroups.
c=o.copy();c.data=o.data.copy();bpy.context.scene.collection.objects.link(c)
g=bpy.data.node_groups.new('Phase4B_ExportOnly_Realize','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
a=g.nodes.new('NodeGroupInput');b=g.nodes.new('GeometryNodeRealizeInstances');z=g.nodes.new('NodeGroupOutput');g.links.new(a.outputs['Geometry'],b.inputs['Geometry']);g.links.new(b.outputs['Geometry'],z.inputs['Geometry']);b.inputs['Realize All'].default_value=True
mod=c.modifiers.new('Phase4B_ExportOnly','NODES');mod.node_group=g;deps.update();real=snapshot(c.evaluated_get(deps));bpy.data.objects.remove(c,do_unlink=True)
def stats(meshes):
 pts=[];v=f=t=0;mats=Counter()
 for m,matrix in meshes:
  m.calc_loop_triangles();v+=len(m.vertices);f+=len(m.polygons);t+=len(m.loop_triangles)
  pts.extend(matrix@x.co for x in m.vertices)
  mats.update(m.materials[x.material_index].name if m.materials[x.material_index] else '<none>' for x in m.loop_triangles)
 return dict(vertices=v,faces=f,triangles=t,material_triangles=dict(mats),materials=len(mats),bounds=[[min(x[i] for x in pts),max(x[i] for x in pts)] for i in range(3)])
# Surface comparison invariant to vertex splitting/order; quantize at 1e-5 BU.
def surface(meshes):
 result=Counter()
 for m,matrix in meshes:
  # polygons, not tessellation-dependent diagonals
  for p in m.polygons:
   mat=m.materials[p.material_index];verts=[]
   for i in p.vertices:
    v=matrix@m.vertices[i].co;verts.append(tuple(round(x,5) for x in v))
   result[(mat.name if mat else '<none>',tuple(sorted(verts)))]+=1
 return result
sa=surface(parts);sc=surface([(real,o.matrix_world)]);diff=sum((sa-sc).values())+sum((sc-sa).values())
# Match every polygon bijectively at a geometric tolerance, avoiding grid-boundary false positives.
from mathutils.kdtree import KDTree
def records(meshes):
 result=[]
 for m,matrix in meshes:
  for p in m.polygons:
   pts=[matrix@m.vertices[i].co for i in p.vertices];mat=m.materials[p.material_index]
   result.append((mat.name if mat else '<none>',pts,sum(pts,Vector())/len(pts)))
 return result
ra=records(parts);rc=records([(real,o.matrix_world)]);tree=KDTree(len(rc))
for i,(_,_,center) in enumerate(rc):tree.insert(center,i)
tree.balance();used=set();unmatched=0;max_error=0
for mat,pts,center in ra:
 best=None
 for _,index,distance in tree.find_range(center,1e-4):
  if index in used or rc[index][0]!=mat or len(rc[index][1])!=len(pts):continue
  other=rc[index][1];error=max(min((p-q).length for q in other) for p in pts)
  if error<1e-4 and (best is None or error<best[0]):best=(error,index)
 if best is None:unmatched+=1
 else:used.add(best[1]);max_error=max(max_error,best[0])
report=dict(polygon_bijective_match=dict(tolerance=1e-4,unmatched_original=unmatched,unmatched_realized=len(rc)-len(used),max_corner_error=max_error),source_sha256=before,blender=bpy.app.version_string,original=stats(parts),phase4=stats([(base,o.matrix_world)]),realized=stats([(real,o.matrix_world)]),instance_count=len(instances),unique_leaf_mesh_datablocks=len(leaf_cache),unique_persistent_paths=len({tuple(x['persistent_id']) for x in instances}),instance_mesh_types=dict(Counter(str((x['vertices'],x['faces'],x['materials'])) for x in instances)),surface_polygon_symmetric_difference=diff,original_matrix=[list(x) for x in o.matrix_world],source_texspace=dict(location=list(o.data.texspace_location),size=list(o.data.texspace_size)),phase4_texspace=dict(location=list(base.texspace_location),size=list(base.texspace_size)))
# Quantization boundaries may differ at the last digit; a second nearest point proof is added externally if needed.
(out/'geometry.json').write_text(json.dumps(report,indent=2));(out/'instances.json').write_text(json.dumps(instances,indent=2))
print('GEOMETRY',json.dumps(report),flush=True)
scene=bpy.data.scenes.new('Phase4B_Isolated');bpy.context.window.scene=scene
lo=Vector([min(v.co[i] for v in base.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in base.vertices) for i in range(3)]);offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
objects={}
control=o;scene.collection.objects.link(control);objects['original']=control
for name,m in [('phase4',base),('realized',real)]:
 x=bpy.data.objects.new('Phase4B_'+name,m);scene.collection.objects.link(x);x.matrix_world=o.matrix_world.copy();objects[name]=x
fixed=real.copy();fixed.use_auto_texspace=False;fixed.texspace_location=base.texspace_location;fixed.texspace_size=base.texspace_size
x=bpy.data.objects.new('Phase4B_corrected',fixed);scene.collection.objects.link(x);x.matrix_world=o.matrix_world.copy();objects['corrected']=x
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.seed=0;scene.cycles.use_denoising=False
scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.view_settings.view_transform='Standard'
scene.world=bpy.data.worlds.new('Phase4B_World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
cam=bpy.data.objects.new('Phase4B_Camera',bpy.data.cameras.new('Phase4B_Camera'));scene.collection.objects.link(cam);cam.data.type='ORTHO';scene.camera=cam
light=bpy.data.objects.new('Phase4B_Light',bpy.data.lights.new('Phase4B_Light','AREA'));scene.collection.objects.link(light);light.location=Vector((2,-3,12))+offset+o.matrix_world.translation;light.data.energy=1800;light.data.size=9
views={'iso':((12,-15,12),(0,0,3.7),15),'front':((16,0,5.2),(0,0,3.7),12),'side':((0,-16,5.2),(0,0,3.7),12),'facade':((11,-5,4.8),(0,-.4,4.2),6)}
def render(name,view,label):
 for k,x in objects.items():x.hide_render=k!=name
 eye,target,scale=views[view];shift=offset+o.matrix_world.translation;cam.location=Vector(eye)+shift;cam.rotation_euler=(Vector(target)+shift-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 scene.render.filepath=str(out/f'{label}_{name}_{view}.png');bpy.ops.render.render(write_still=True)
clay=bpy.data.materials.new('Phase4B_WhiteEmission');clay.use_nodes=True;n=clay.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1,1,1,1);output=n.new('ShaderNodeOutputMaterial');clay.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
scene.view_layers[0].material_override=clay
for name in ('original','phase4','realized'):
 for view in views:render(name,view,'silhouette')
# Generated diagnostic deliberately scaled to avoid clipping; no fitted scale/offset.
coord=clay.copy();coord.name='Phase4B_GeneratedDiagnostic';n=coord.node_tree.nodes;tc=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.01;coord.node_tree.links.new(tc.outputs['Generated'],scale.inputs[0]);coord.node_tree.links.new(scale.outputs[0],n.get('Emission').inputs['Color']);scene.view_layers[0].material_override=coord
for name in objects:
 render(name,'facade','generated')
# Float Generated-coordinate proof on actually visible plaster, independent of lighting.
from mathutils.bvhtree import BVHTree
real.calc_loop_triangles();triangles=[tuple(t.vertices) for t in real.loop_triangles]
bvh=BVHTree.FromPolygons([v.co for v in real.vertices],triangles,all_triangles=True)
mask=[];eye,target,view_scale=views['facade'];shift=offset+o.matrix_world.translation
rotation=cam.rotation_euler.to_matrix();right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0));direction=rotation@Vector((0,0,-1))
inv=o.matrix_world.inverted();origin=cam.location
for y in range(480):
 for px in range(640):
  start=origin+right*((px+.5-320)*view_scale/640)+up*((y+.5-240)*view_scale/640)
  hit,normal,index,distance=bvh.ray_cast(inv@start,inv.to_3x3()@direction)
  mask.append(index is not None and real.materials[real.loop_triangles[index].material_index] is not None and real.materials[real.loop_triangles[index].material_index].name=='UpperFloorsPaint')
# Exclude anti-aliased boundaries (two pixel erosion).
mask=[value and all(mask[yy*640+xx] for yy in range(max(0,y-2),min(480,y+3)) for xx in range(max(0,px-2),min(640,px+3))) for y in range(480) for px,value in enumerate(mask[y*640:(y+1)*640])]
scale.inputs[3].default_value=1
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP'
float_pixels={}
for name in objects:
 render(name,'facade','coordinates_float')
 path=out/f'coordinates_float_{name}_facade.png' # Blender uses filename verbatim plus .exr
 actual=Path(str(path)+'.exr') if not path.exists() else path
 # Blender replaces the extension for write_still.
 if not actual.exists():actual=out/f'coordinates_float_{name}_facade.exr'
 image=bpy.data.images.load(str(actual),check_existing=False);float_pixels[name]=list(image.pixels);bpy.data.images.remove(image)
metrics={}
for name in ('phase4','realized','corrected'):
 errors=[abs(float_pixels['original'][4*i+c]-float_pixels[name][4*i+c]) for i,yes in enumerate(mask) if yes for c in range(3)]
 metrics[name]=dict(visible_plaster_pixels=sum(mask),mae=sum(errors)/len(errors),max_abs=max(errors))
report['generated_plaster_float_comparison']=metrics
(out/'geometry.json').write_text(json.dumps(report,indent=2))
maskimage=bpy.data.images.new('PlasterVisibleMask',width=640,height=480,alpha=True);maskimage.pixels=[v for yes in mask for v in ((1,1,1,1) if yes else (0,0,0,1))];maskimage.filepath_raw=str(out/'plaster_mask_facade.png');maskimage.file_format='PNG';maskimage.save()
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8'
scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.view_layers[0].material_override=None
for name in objects:
 for view in views:render(name,view,'shader')
# Preserve exact setup in a separate file? No: script is the reproducible artifact.
assert sha(source)==before
print('RENDERS_COMPLETE',flush=True)
