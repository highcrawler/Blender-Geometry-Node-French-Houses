"""Small MOD-01-only wall assembler; no Cottage/roof/export modifications."""
import bpy
import bmesh
from mathutils import Matrix, Vector
from wall_plain import WallPlain

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


def create_module(parent_collection, root, definition: WallPlain, module_id,
                  left_y, width, x_center, wall_bottom,
                  clay, cap_left, cap_right):
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
    assert (mesh.matrix_world @ mesh.data.vertices[0].co -
            Vector((x_center-definition.thickness/2,left_y,wall_bottom))).length < 1e-5
    record = definition.contract(module_id,width,(x_center,left_y,wall_bottom),name,cap_left,cap_right)
    record['blender_collection'] = coll.name
    record['pivot_object'] = pivot.name
    record['triangles'] = sum(len(p.vertices)-2 for p in mesh.data.polygons)
    return {'collection':coll,'pivot':pivot,'mesh':mesh,'contract':record}


def dispose_module(instance):
    mesh=instance['mesh'];data=mesh.data
    bpy.data.objects.remove(mesh,do_unlink=True)
    bpy.data.meshes.remove(data)
    bpy.data.objects.remove(instance['pivot'],do_unlink=True)
    bpy.data.collections.remove(instance['collection'])
