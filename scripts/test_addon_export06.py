"""Phase 6 integration: installed ZIP, five houses, full owned polygons and GLB decode."""
import bpy, importlib, json, hashlib, struct, math
from pathlib import Path
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT = Path.cwd()
OUT = ROOT/'tests/addon/phase6'
MODULE = 'bl_ext.mbg_export_test.medieval_building_generator'
E = importlib.import_module(MODULE+'.exporter')
A = importlib.import_module(MODULE+'.assets')
REPORT = dict(version=bpy.app.version_string, exports={}, errors={})


def stable(v):
    if isinstance(v,bpy.types.ID):return v.name_full
    if hasattr(v,'__len__') and not isinstance(v,str):return list(v)
    return v


def state():
    bpy.context.view_layer.update()
    houses = {}
    for obj in bpy.context.scene.objects:
        values = {}
        mod = A.generator_modifier(obj)
        if mod:
            for name in A.REQUIRED:
                v = A.socket(mod,name).value
                values[name] = v.name if isinstance(v,bpy.types.ID) else list(v) if hasattr(v,'__len__') and not isinstance(v,str) else v
        houses[obj.name] = dict(matrix=[list(row) for row in obj.matrix_world],
             mesh=hashlib.sha256(str([tuple(v.co) for v in obj.data.vertices]).encode()).hexdigest() if obj.type=='MESH' else None,
             modifiers=[(m.name,m.type,m.node_group.name if m.type=='NODES' else None) for m in obj.modifiers], values=values)
    return dict(objects=houses, scene=bpy.context.scene.name, layer=bpy.context.view_layer.name,
        active=bpy.context.active_object.name if bpy.context.active_object else None,
        selected=sorted(o.name for o in bpy.context.selected_objects), filepath=bpy.data.filepath,
        ids={name:sorted(d.name for d in getattr(bpy.data,name)) for name in
             ('objects','meshes','collections','materials','node_groups','scenes','images')},
        asset_transforms={o.name:[list(row) for row in o.matrix_world] for o in bpy.data.objects if not o.get(A.HOUSE_TAG)},
        group_references={g.name:[(n.name,n.bl_idname,n.node_tree.name if n.type=='GROUP' and n.node_tree else None,
            [(s.name,stable(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]) for n in g.nodes] for g in bpy.data.node_groups},
        materials={m.name:dict(diffuse=list(m.diffuse_color),
            nodes=[(n.name,n.bl_idname,[(s.name,stable(s.default_value)) for s in list(n.inputs)+list(n.outputs) if hasattr(s,'default_value')]) for n in m.node_tree.nodes] if m.node_tree else [],
            links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.node_tree else []) for m in bpy.data.materials})


def owned_surface(obj):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pivot = obj.matrix_world @ E.footprint_pivot(obj)
    records=[]
    positions=defaultdict(list)
    triangles=Counter()
    occurrences=[]
    def add(mesh,matrix):
        mesh.calc_loop_triangles()
        for p in mesh.polygons:
            mat=mesh.materials[p.material_index].name
            pts=[matrix@mesh.vertices[i].co-pivot for i in p.vertices]
            records.append((mat,pts,sum(pts,Vector())/len(pts)))
            positions[mat].extend(pts)
        for t in mesh.loop_triangles:triangles[mesh.materials[t.material_index].name]+=1
    ev=obj.evaluated_get(dg)
    direct=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
    add(direct,ev.matrix_world)
    ev.to_mesh_clear()
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent and inst.parent.original==obj and inst.show_self:
            assert inst.object.type=='MESH'
            add(inst.object.data,inst.matrix_world)
            occurrences.append(dict(owner=inst.parent.original.name,persistent_id=list(inst.persistent_id)))
    return records,positions,triangles,occurrences


def polygon_match(reference, mesh):
    actual=[]
    for p in mesh.polygons:
        pts=[mesh.vertices[i].co.copy() for i in p.vertices]
        actual.append((mesh.materials[p.material_index].name,pts,sum(pts,Vector())/len(pts)))
    tree=KDTree(len(actual))
    for i,(_,_,center) in enumerate(actual):tree.insert(center,i)
    tree.balance(); used=set(); maximum=0
    for mat,pts,center in reference:
        best=None
        for _,i,_ in tree.find_range(center,2e-4):
            other=actual[i]
            if i in used or other[0]!=mat or len(other[1])!=len(pts):continue
            err=max(min((p-q).length for q in other[1]) for p in pts)
            if err<2e-4 and (best is None or err<best[0]):best=(err,i)
        assert best is not None, (mat,list(center))
        used.add(best[1]);maximum=max(maximum,best[0])
    assert len(used)==len(actual)==len(reference)
    return dict(polygons=len(actual),unmatched=0,max_corner_error=maximum,tolerance=2e-4)


def decode_glb(path):
    blob=Path(path).read_bytes(); length=struct.unpack_from('<I',blob,12)[0]
    g=json.loads(blob[20:20+length]); binary=28+length
    def accessor(index):
        a=g['accessors'][index]; v=g['bufferViews'][a['bufferView']]
        fmt='<'+{5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        stride=v.get('byteStride',struct.calcsize(fmt));offset=binary+v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from(fmt,blob,offset+i*stride) for i in range(a['count'])]
    return g,accessor


def kd_error(a,b):
    tree=KDTree(len(b))
    for i,p in enumerate(b):tree.insert(p,i)
    tree.balance()
    return max(tree.find(p)[2] for p in a)


def checked_export(obj,name):
    before=state()
    source,positions,triangles,instances=owned_surface(obj)
    convert=E.convert_materials
    polygon_report={}
    def checked_materials(mesh,obj,created):
        polygon_report.update(polygon_match(source,mesh))
        return convert(mesh,obj,created)
    E.convert_materials=checked_materials
    try:result=E.export_house(bpy.context,obj,OUT/(name+'.glb'),overwrite=True)
    finally:E.convert_materials=convert
    assert state()==before, 'scene changed'
    g,read=decode_glb(result['path'])
    assert len(g['meshes'])==1 and not g.get('images') and not g.get('textures')
    nodes=[n for n in g['nodes'] if 'mesh' in n]
    assert len(nodes)==1 and not any(k in nodes[0] for k in ('matrix','translation','rotation','scale'))
    errors={}
    support_bounds={}
    normal_count=0
    for p in g['meshes'][0]['primitives']:
        exported_material=g['materials'][p['material']]
        mat=exported_material['name'].removeprefix('MBG_PBR_')
        color_socket={'Roof':'RoofColor','UpperFloorsPaint':'PaintColor','Beam':'BeamCollor'}.get(mat)
        if color_socket:
            wanted=tuple(A.socket(A.generator_modifier(obj),color_socket).value)
            factor=exported_material['pbrMetallicRoughness'].get('baseColorFactor',[1,1,1,1])
            assert max(abs(a-b) for a,b in zip(wanted,factor))<1e-6, (mat,wanted,factor)
        assert len(read(p['indices']))//3==triangles[mat]
        pts=[Vector((v[0],-v[2],v[1])) for v in read(p['attributes']['POSITION'])]
        errors[mat]=max(kd_error(pts,positions[mat]),kd_error(positions[mat],pts))
        assert errors[mat]<2e-4,(mat,errors[mat])
        normals=read(p['attributes']['NORMAL'])
        assert all(all(math.isfinite(c) for c in n) and abs(sum(c*c for c in n)-1)<.001 for n in normals)
        normal_count+=len(normals)
        if mat=='GroundFloorWalls':
            a=g['accessors'][p['attributes']['POSITION']]
            support_bounds=dict(min=a['min'],max=a['max'])
            assert abs(a['min'][1])<1e-5  # Blender Z becomes glTF/Godot Y.
    assert result['triangles']==sum(triangles.values())
    result.update(polygon_bijection=polygon_report,glb_position_errors=errors,
        glb_sha256=hashlib.sha256(Path(result['path']).read_bytes()).hexdigest(),
        glb_materials=g['materials'],original_unchanged=True,identity_mesh_node=True,
        supporting_body_bounds_gltf=support_bounds,unit_finite_normals=normal_count)
    REPORT['exports'][name]=result
    (OUT/(name+'_ownership.json')).write_text(json.dumps(dict(house=obj.name,instances=instances),indent=2))
    return result


# Source is never opened as a working file and never saved.
bpy.context.preferences.addons[MODULE].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
positions=[(0,0,0),(20,0,0),(40,15,0),(-30,10,0),(15,-25,0)]
houses=[]
for i,pos in enumerate(positions):
    bpy.context.scene.cursor.location=pos
    assert bpy.ops.mbg.create_house()=={'FINISHED'}
    obj=bpy.context.active_object;obj.name=f'Library House {i+1}'
    obj.mbg_settings.seed=[29,83,17,56,102][i]
    obj.mbg_settings.floors=[2,3,2,1,3][i]
    obj.mbg_settings.roof_color=[(.48,.055,.11,1),(.1,.4,.2,1),(.035,.16,.55,1),(.3,.15,.05,1),(.3,.06,.38,1)][i]
    obj.mbg_settings.paint_color=(.72-i*.06,.58-i*.05,.38-i*.03,1)
    obj.mbg_settings.beam_color=(.045+i*.015,.02+i*.01,.01+i*.004,1)
    houses.append(obj)
    if i==0:
        obj.mbg_settings.seed=83
        obj.mbg_settings.floors=3
        obj.mbg_settings.roof_color=(.1,.4,.2,1)
        checked_export(obj,'single_house')
        obj.mbg_settings.seed=29
        obj.mbg_settings.floors=2
        obj.mbg_settings.roof_color=(.48,.055,.11,1)
# Deliberately select all houses plus unrelated object; only active house 3 may export.
bpy.ops.mesh.primitive_cube_add(location=(95,32,0));foreign=bpy.context.active_object
for obj in houses:obj.select_set(True)
bpy.context.view_layer.objects.active=houses[2]
checked_export(houses[2],'house3')
for i in (0,4):
    bpy.context.view_layer.objects.active=houses[i]
    checked_export(houses[i],f'house{i+1}')
# Transformed house: yaw, nonuniform/mirrored scale. Original world placement removed.
houses[1].rotation_euler.z=.47;houses[1].scale=(-1.2,.8,1.1)
bpy.context.view_layer.objects.active=houses[1]
checked_export(houses[1],'transformed_house2')


def expect_error(label,fn):
    before=state()
    try:fn()
    except (E.ExportError,RuntimeError) as exc:REPORT['errors'][label]=str(exc)
    else:raise AssertionError('Expected failure: '+label)
    assert state()==before, label


obj=houses[2]
bpy.context.view_layer.objects.active=obj
expect_error('invalid_object',lambda:E.export_house(bpy.context,foreign,OUT/'invalid.glb'))
expect_error('no_active',lambda:E.export_house(bpy.context,None,OUT/'none.glb'))
expect_error('missing_directory',lambda:E.export_house(bpy.context,obj,OUT/'absent/new.glb'))
old_hash=hashlib.sha256((OUT/'house3.glb').read_bytes()).hexdigest()
expect_error('overwrite_unconfirmed',lambda:E.export_house(bpy.context,obj,OUT/'house3.glb'))
assert hashlib.sha256((OUT/'house3.glb').read_bytes()).hexdigest()==old_hash
owned=E.owned_counts
E.owned_counts=lambda *a:(_ for _ in ()).throw(RuntimeError('Injected evaluation failure'))
try:expect_error('initial_depsgraph_failure',lambda:E.export_house(bpy.context,obj,OUT/'failed_eval.glb'))
finally:E.owned_counts=owned
# Construction error before the helper returns its group: real partial ID must
# be deleted by the helper itself (the transaction cannot yet know that ID).
from types import SimpleNamespace
real_bpy=E.bpy
class FailingGroups:
    def new(self,*args):
        self.real=real_bpy.data.node_groups.new(*args)
        self.proxy=SimpleNamespace(interface=SimpleNamespace(new_socket=self.fail))
        return self.proxy
    def fail(self,**kwargs):raise RuntimeError('Injected node-construction failure')
    def remove(self,group):
        assert group is self.proxy
        real_bpy.data.node_groups.remove(self.real)
E.bpy=SimpleNamespace(data=SimpleNamespace(node_groups=FailingGroups()))
try:expect_error('partial_group_construction_failure',E.realize_group)
finally:E.bpy=real_bpy
original_group=E.realize_group

def broken_realize():
    group=original_group()
    for link in list(group.links):group.links.remove(link)
    return group

E.realize_group=broken_realize
try:expect_error('geometry_realization_failure',lambda:E.export_house(bpy.context,obj,OUT/'failed_geometry.glb'))
finally:E.realize_group=original_group
assert not (OUT/'failed_geometry.glb').exists()
link=E.os.link
E.os.link=lambda *a,**k:(_ for _ in ()).throw(OSError('Injected disk commit failure'))
try:expect_error('disk_failure_after_gltf',lambda:E.export_house(bpy.context,obj,OUT/'failed_disk.glb'))
finally:E.os.link=link
assert not (OUT/'failed_disk.glb').exists() and not list(OUT.glob('.mbg_*'))
# Force the primary-pivot-unavailable path as a controlled fallback test.
primary=E._input_pivot
E._input_pivot=lambda *a:(_ for _ in ()).throw(E.ExportError('Injected ambiguous footprint'))
try:
    fallback=checked_export(obj,'fallback_house3')
    assert fallback['pivot_method']=='supporting_body_fallback'
    support=E._support_pivot
    E._support_pivot=lambda *a:(_ for _ in ()).throw(E.ExportError('No supporting body'))
    try:expect_error('no_reliable_pivot',lambda:E.export_house(bpy.context,obj,OUT/'failed_pivot.glb'))
    finally:E._support_pivot=support
finally:E._input_pivot=primary
# Repeat exports are geometrically identical. Binary hash may reflect exporter metadata.
repeat=checked_export(obj,'house3_repeat')
assert repeat['triangles']==REPORT['exports']['house3']['triangles']
obj.name='Renamed / Castle : 03'
assert E.filename_for(obj)=='Renamed_Castle_03.glb'
# Programmatic operator path, no dialog, target selected by marker not name.
operator_path=OUT/'runtime/operator.glb'
operator_path.unlink(missing_ok=True)
pre=state()
assert bpy.ops.mbg.export_house(filepath=str(operator_path))=={'FINISHED'}
assert pre==state()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'runtime/library.blend'))
REPORT['state_before_reload']=state()
REPORT['zero_user_ids']={name:[d.name for d in getattr(bpy.data,name) if d.users==0]
    for name in REPORT['state_before_reload']['ids']}
REPORT['source_sha256']=hashlib.sha256((ROOT/'GeometryNodesFrenchHous.blend').read_bytes()).hexdigest()
(OUT/'integration.json').write_text(json.dumps(REPORT,indent=2))
print('PHASE6_INTEGRATION_PASS',json.dumps({n:dict(triangles=v['triangles'],bytes=v['bytes'],instances=v['owned_instances']) for n,v in REPORT['exports'].items()}),flush=True)
