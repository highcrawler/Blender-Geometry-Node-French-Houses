"""HouseOne-only original plaster color proof. Never saves or edits source datablocks.
Run: blender -b --factory-startup -t 4 -P scripts/bake_houseone_plaster.py -- --render
"""
import argparse, hashlib, json, math, struct, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

parser=argparse.ArgumentParser()
parser.add_argument('--render',action='store_true')
parser.add_argument('--repeat',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path.cwd(); out=root/'tests/baking/phase4'; out.mkdir(parents=True,exist_ok=True)
source=root/'GeometryNodesFrenchHous.blend'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source_hash=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
obj=bpy.data.objects['HouseOne']; deps=bpy.context.evaluated_depsgraph_get()
mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
mesh.calc_loop_triangles()
assert len(mesh.loop_triangles)==50944
original=list(mesh.materials)
slot=next(i for i,m in enumerate(original) if m and m.name=='UpperFloorsPaint')
def geometry_hash():
    h=hashlib.sha256()
    for v in mesh.vertices: h.update(struct.pack('<3f',*v.co))
    for p in mesh.polygons: h.update(struct.pack('<%dI'%(len(p.vertices)+1),p.material_index,*p.vertices))
    return h.hexdigest()
before=geometry_hash()
lo=Vector(tuple(min(v.co[i] for v in mesh.vertices) for i in range(3)))
hi=Vector(tuple(max(v.co[i] for v in mesh.vertices) for i in range(3)))
offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
scene=bpy.data.scenes.new('Phase4_Comparison'); bpy.context.window.scene=scene
copy=bpy.data.objects.new('HouseOne_Phase4',mesh); scene.collection.objects.link(copy)
# Keep original local vertices for Generated and GN attributes. Center with object transform.
copy.location=-offset
bpy.context.view_layer.objects.active=copy; copy.select_set(True)
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=16
scene.cycles.seed=0; scene.cycles.use_denoising=True
scene.render.resolution_x=960; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('Phase4_World'); scene.world.use_nodes=True
bg=scene.world.node_tree.nodes['Background']; bg.inputs['Color'].default_value=(.65,.68,.72,1); bg.inputs['Strength'].default_value=.8
cam=bpy.data.objects.new('Phase4_Camera',bpy.data.cameras.new('Phase4_Camera')); scene.collection.objects.link(cam); scene.camera=cam; cam.data.type='ORTHO'
light=bpy.data.objects.new('Phase4_Area',bpy.data.lights.new('Phase4_Area','AREA')); scene.collection.objects.link(light)
light.location=(2,-3,12); light.data.energy=1800; light.data.shape='DISK'; light.data.size=9
views={'iso':((12,-15,12),(0,0,3.7),15),'front':((16,0,5.2),(0,0,3.7),12),'facade':((11,-5,4.8),(0,-.4,4.2),6)}
def render(label):
    for view,(eye,target,scale) in views.items():
        cam.location=eye; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
        scene.render.filepath=str(out/f'blender_{label}_{view}.png'); bpy.ops.render.render(write_still=True)
if args.render:
    # Actual GN object copy is an independent control for Generated-coordinate fidelity.
    control=obj.copy(); scene.collection.objects.link(control); control.matrix_world=copy.matrix_world.copy()
    copy.hide_render=True; render('gn_control'); control.hide_render=True; copy.hide_render=False
    bpy.data.objects.remove(control,do_unlink=True)
    render('original')
# New layer only: original UVMap and all geometry/attributes are retained.
bpy.ops.object.select_all(action='DESELECT')
copy.select_set(True); bpy.context.view_layer.objects.active=copy
uv=mesh.uv_layers.new(name='PlasterBake'); mesh.uv_layers.active=uv
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_mode(type='FACE')
bpy.ops.mesh.select_all(action='DESELECT')
import bmesh
bm=bmesh.from_edit_mesh(mesh)
for face in bm.faces: face.select_set(face.material_index==slot)
bmesh.update_edit_mesh(mesh)
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.02,margin_method='FRACTION',area_weight=0,correct_aspect=True,scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT')
uv=mesh.uv_layers['PlasterBake']; uv.active_render=True
assert sum(p.select for p in mesh.polygons)==1105
uv_polygons=[[list(uv.data[i].uv) for i in p.loop_indices] for p in mesh.polygons if p.material_index==slot]
assert len(set(tuple(tuple(v) for v in p) for p in uv_polygons))==1105
assert all(abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))>1e-12 for p in uv_polygons)
(out/'bake_uv.json').write_text(json.dumps(uv_polygons))
image=bpy.data.images.new('HouseOne_Plaster_BaseColor',width=1024,height=1024,alpha=False)
image.colorspace_settings.name='sRGB'; image.file_format='PNG'; image.filepath_raw=str(out/'HouseOne_Plaster_BaseColor.png')
# Bake only the original plaster, with harmless sinks on other slots; no source node edits.
for i,m in enumerate(original):
    if m:
        m=m.copy(); mesh.materials[i]=m
        node=m.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image
        m.node_tree.nodes.active=node; node.select=True
scene.render.bake.use_pass_direct=False; scene.render.bake.use_pass_indirect=False; scene.render.bake.use_pass_color=True
scene.render.bake.margin=8; scene.render.bake.margin_type='EXTEND'; scene.render.bake.use_clear=True
# Other materials use a 1px sink, so they cannot overwrite plaster UVs.
sink=bpy.data.images.new('UnusedMaterialSink',width=1,height=1)
for i,m in enumerate(mesh.materials):
    if m and i!=slot: m.node_tree.nodes.active.image=sink
bake_times=[]; hashes=[]
for run in range(2 if args.repeat else 1):
    start=time.perf_counter(); bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},uv_layer='PlasterBake'); bake_times.append(time.perf_counter()-start)
    assert max(list(image.pixels)[0::4])>.1, 'Empty color bake'
    image.save(); hashes.append(sha(Path(image.filepath_raw)))
# Exactly the Phase-3 constant PBR values for the remaining surfaces.
phase3=json.loads((root/'tests/materials/phase3/HouseOne_PBR.json').read_text())
pbr=[]
for m in original:
    if not m: pbr.append(None); continue
    mat=bpy.data.materials.new(m.name+'_Phase4'); mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=phase3['original_linear_colors'][m.name]
    shader.inputs['Roughness'].default_value=phase3['roughness'][m.name]
    shader.inputs['Metallic'].default_value=0
    pbr.append(mat)
for i,m in enumerate(pbr): mesh.materials[i]=m
if args.render: render('phase3')
mat=pbr[slot]; shader=mat.node_tree.nodes.get('Principled BSDF')
tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=image
uvnode=mat.node_tree.nodes.new('ShaderNodeUVMap'); uvnode.uv_map='PlasterBake'
mat.node_tree.links.new(uvnode.outputs['UV'],tex.inputs['Vector']); mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
if args.render: render('phase4')
assert geometry_hash()==before
bpy.ops.object.select_all(action='DESELECT'); copy.select_set(True); bpy.context.view_layer.objects.active=copy
start=time.perf_counter(); path=out/'HouseOne_Phase4.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_vertex_color='NONE')
export_seconds=time.perf_counter()-start
blob=path.read_bytes(); length=struct.unpack_from('<I',blob,12)[0]; gltf=json.loads(blob[20:20+length])
prims=[p for m in gltf['meshes'] for p in m['primitives']]
triangles=sum(gltf['accessors'][p['indices']]['count']//3 for p in prims)
assert triangles==50944 and len(gltf['materials'])==5
assert len(gltf['images'])==len(gltf['textures'])==1
plaster=next(m for m in gltf['materials'] if m['name']=='UpperFloorsPaint_Phase4')
ref=plaster['pbrMetallicRoughness']['baseColorTexture']; uvindex=ref.get('texCoord',0)
assert all('TEXCOORD_'+str(uvindex) in p['attributes'] for p in prims if gltf['materials'][p['material']]==plaster)
img=gltf['images'][gltf['textures'][ref['index']]['source']]; view=gltf['bufferViews'][img['bufferView']]
bin_start=20+length+8; embedded=blob[bin_start+view.get('byteOffset',0):bin_start+view.get('byteOffset',0)+view['byteLength']]
assert embedded==Path(image.filepath_raw).read_bytes()
assert sha(source)==source_hash
report={'blender':bpy.app.version_string,'source_sha256':source_hash,'geometry_sha256_before':before,'geometry_sha256_after':geometry_hash(),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'triangles':triangles,'glb_bytes':len(blob),'materials':len(gltf['materials']),'images':len(gltf['images']),'texture_resolution':[1024,1024],'png_bytes':Path(image.filepath_raw).stat().st_size,'png_sha256_runs':hashes,'bake_seconds':bake_times,'export_seconds':export_seconds,'bake_margin':8,'uv_island_margin_fraction':.02,'glb_texture_reference':ref,'embedded_png_identical':True,'gltf':gltf}
(out/'measurements.json').write_text(json.dumps(report,indent=2))
print('PHASE4_COMPLETE',json.dumps({k:v for k,v in report.items() if k!='gltf'}),flush=True)
