"""Small MOD-01-only wall assembler; no Cottage/roof/export modifications."""
import bpy
import bmesh
from mathutils import Matrix, Vector
from wall_plain import WallPlain
from wall_window import WallWindow

# Columns are local u(+world Y), v(+world Z), n(+world X).
LOCAL_TO_WORLD = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0)))
assert LOCAL_TO_WORLD.determinant() > 0.999999


def _mesh(coll, name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(material)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    ob = bpy.data.objects.new(name, mesh)
    coll.objects.link(ob)
    return ob


def create_member(coll, root, name, endpoints, thickness, oak):
    """Exact ART-01 centerline/thickness and elementary six-quad box convention."""
    a, b = (Vector(x) for x in endpoints)
    half = thickness / 2
    length = (b-a).length
    vertices = [(sx*half, sy*half, sz*length/2)
                for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
    faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),
             (2,6,7,3),(0,4,6,2),(1,3,7,5)]
    ob = _mesh(coll, name, vertices, faces, oak)
    ob.parent = root
    ob.location = (a+b)/2
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (b-a).to_track_quat('Z','Y')
    bpy.context.view_layer.update()
    assert (ob.matrix_world.translation - (a+b)/2).length < 1e-5
    return ob


def create_module(parent_collection, root, definition: WallPlain | WallWindow, module_id,
                  left_y, width, x_center, wall_bottom,
                  clay, cap_left, cap_right, oak=None):
    """Create separate pivot + private infill mesh; root and frame own no infill."""
    coll = bpy.data.collections.new(module_id+'_Collection')
    parent_collection.children.link(coll)
    pivot = bpy.data.objects.new(module_id+'_Pivot', None)
    coll.objects.link(pivot)
    pivot.parent = root
    pivot.location = (x_center, left_y, wall_bottom)
    pivot.rotation_mode = 'QUATERNION'
    pivot.rotation_quaternion = LOCAL_TO_WORLD.to_quaternion()
    vertices, faces = definition.geometry(width, cap_left, cap_right)
    name = module_id+'_Infill'
    mesh = _mesh(coll, name, vertices, faces, clay)
    mesh.parent = pivot
    mesh.location = (0,0,0)
    bpy.context.view_layer.update()
    expected = Vector((x_center,left_y,wall_bottom))
    assert (pivot.matrix_world.translation - expected).length < 1e-5
    v0=mesh.data.vertices[0].co
    assert (mesh.matrix_world @ v0 -
            Vector((x_center+v0.z,left_y+v0.x,wall_bottom+v0.y))).length < 1e-5
    record = definition.contract(module_id,width,(x_center,left_y,wall_bottom),name,cap_left,cap_right)
    record['blender_collection'] = coll.name
    record['pivot_object'] = pivot.name
    record['triangles'] = sum(len(p.vertices)-2 for p in mesh.data.polygons)
    instance = {'collection':coll,'pivot':pivot,'mesh':mesh,'parts':[],'contract':record}
    if isinstance(definition, WallWindow):
        if oak is None:
            raise ValueError('WALL_WINDOW requires the existing Weathered Oak material')
        for item in definition.member_specs(width):
            a,b=(Vector(item[k]) for k in ('a','b'))
            half=item['thickness']/2
            length=(b-a).length
            vertices=[(sx*half,sy*half,sz*length/2)
                      for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)]
            faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
            name=module_id+'_'+item['role']
            part=_mesh(coll,name,vertices,faces,oak)
            part.parent=pivot
            part.location=(a+b)/2
            part.rotation_mode='QUATERNION'
            part.rotation_quaternion=(b-a).to_track_quat('Z','Y')
            bpy.context.view_layer.update()
            assert (part.matrix_world.translation-(pivot.matrix_world @ ((a+b)/2))).length<1e-5
            instance['parts'].append(part)
            record['owned_meshes'].append(part.name)
        record['wood_part_triangles']=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in instance['parts'])
        assert record['wood_part_triangles']==48
    return instance


def dispose_module(instance):
    for obj in (instance['mesh'],*instance['parts']):
        data=obj.data
        bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.meshes.remove(data)
    bpy.data.objects.remove(instance['pivot'],do_unlink=True)
    bpy.data.collections.remove(instance['collection'])
