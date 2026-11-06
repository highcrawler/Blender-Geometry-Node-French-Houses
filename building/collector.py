"""Read-only owner-scoped geometry inventory; no exporters or geometry creation.

Ownership is Blender ID identity + exclusive collection containment + root ancestry.
Names, spatial overlap and material names never decide ownership.
"""
from collections import Counter
from dataclasses import dataclass
import math

import bpy
from mathutils import Vector, Matrix


class CollectorError(ValueError):
    """Unambiguous refusal with a stable diagnostic code."""

    def __init__(self, code, detail):
        self.code = code
        super().__init__(f'{code}: {detail}')


@dataclass(frozen=True)
class MaterialUsage:
    slot_index: int
    material: object
    polygons: int
    triangles: int


@dataclass(frozen=True)
class MeshRecord:
    obj: object
    role: str
    roof_part: str | None
    mesh: object
    matrix_local: Matrix
    matrix_world: Matrix
    export_local_matrix: Matrix
    triangles: int
    materials: tuple[MaterialUsage, ...]


@dataclass(frozen=True)
class BuildingGeometryResult:
    building_root: object
    building_collection: object
    mesh_objects: tuple
    body_objects: tuple
    roof_objects: tuple
    records: tuple[MeshRecord, ...]
    pivot_local: Vector
    pivot_world: Vector
    world_to_export_local: Matrix
    triangles: int
    materials: tuple
    diagnostics: tuple[str, ...]


def _fail(code, detail):
    raise CollectorError(code, detail)


def _finite_matrix(mat):
    return all(math.isfinite(float(v)) for row in mat for v in row)


def _descendants(collection):
    result = set()
    def walk(coll):
        if coll in result:
            _fail('COLLECTION_CYCLE', 'repeated collection in owner hierarchy')
        result.add(coll)
        if coll.users != 1:
            _fail('COLLECTION_SHARED', 'owner collection has multiple or no users')
        for child in coll.children:
            walk(child)
    walk(collection)
    return result


def _under_root(obj, root):
    seen = set()
    parent = obj.parent
    while parent is not None:
        if parent in seen:
            _fail('PARENT_CYCLE', 'cyclic parent ancestry')
        if parent == root:
            return True
        seen.add(parent)
        parent = parent.parent
    return False


def collect_building_geometry(building_root, building_collection) -> BuildingGeometryResult:
    """Inspect one already-owned building; reject ambiguity and unsupported geometry.

    Contract for current Cottage: an unparented unit-scale EMPTY at the ground
    footprint center, unique owner collection, roof parts tagged with roof_part.
    No fixed body-mesh count, bounding-box test, selection or scene mutation.
    """
    if not isinstance(building_root, bpy.types.Object) or building_root.type != 'EMPTY':
        _fail('ROOT_INVALID', 'expected an EMPTY Building Root object reference')
    if not isinstance(building_collection, bpy.types.Collection):
        _fail('COLLECTION_INVALID', 'expected a building Collection reference')
    root = building_root
    if (root.parent is not None or root.rotation_mode != 'XYZ' or
            not all(math.isfinite(float(v)) for v in (*root.location, *root.rotation_euler, *root.scale)) or
            any(abs(float(v) - 1) > 1e-8 for v in root.scale) or
            abs(root.rotation_euler.x) > 1e-8 or abs(root.rotation_euler.y) > 1e-8 or
            not _finite_matrix(root.matrix_world)):
        _fail('ROOT_TRANSFORM', 'finite unparented unit-scale XYZ/Z-yaw root required')
    if tuple(root.users_collection) != (building_collection,):
        _fail('ROOT_COLLECTION', 'root must be linked solely to its direct owner collection')
    collections = _descendants(building_collection)
    if sum(o.type == 'EMPTY' and o.parent is None for o in building_collection.objects) != 1:
        _fail('ROOT_AMBIGUOUS', 'owner collection must have exactly one unparented EMPTY')
    owner_objects = {ob for coll in collections for ob in coll.objects}
    if root not in owner_objects:
        _fail('ROOT_MISSING', 'root is not in owner hierarchy')
    for ob in owner_objects:
        if len(ob.users_collection) != 1 or ob.users_collection[0] not in collections:
            _fail('OBJECT_COLLECTION', f'object {ob.name!r} has multiple or foreign collection links')
        if ob != root and not _under_root(ob, root):
            _fail('OBJECT_PARENT', f'object {ob.name!r} is not descended from owner root')
        if ob != root and ob.type != 'MESH':
            _fail('NONMESH', f'unsupported owner object type {ob.type}')
    # A child may be parented to root but linked outside the owner's hierarchy.
    for ob in bpy.data.objects:
        if ob not in owner_objects and _under_root(ob, root):
            _fail('EXTERNAL_CHILD', f'root child {ob.name!r} lives outside owner collection')
        if ob != root and ob in owner_objects and ob.instance_type != 'NONE':
            _fail('INSTANCE_UNSUPPORTED', f'object {ob.name!r} instances geometry')
    roof_collections = set()
    body, roof = [], []
    for ob in owner_objects - {root}:
        if ob.get('role') == 'roof':
            if building_collection in ob.users_collection:
                _fail('ROOF_COLLECTION', 'roof must live in a child collection')
            roof_collections.add(ob.users_collection[0])
            roof.append(ob)
        else:
            if ob.get('roof_part') is not None:
                _fail('ROLE_CONFLICT', 'roof_part without roof role')
            body.append(ob)
    if not body or not roof or len(roof_collections) != 1:
        _fail('ROOF_INCOMPLETE', 'nonempty body and exactly one roof collection are required')
    roof_collection = next(iter(roof_collections))
    if not any(child == roof_collection for child in building_collection.children) or set(roof_collection.objects) != set(roof):
        _fail('ROOF_COLLECTION', 'roof collection must be a direct child containing only roof meshes')
    if any(ob.users_collection[0] != building_collection for ob in body):
        _fail('BODY_COLLECTION', 'body mesh must belong directly to building collection')
    parts = Counter(ob.get('roof_part') for ob in roof)
    if None not in parts and set(parts) <= {'deck', 'shingles', 'ridge'}:
        if parts != {'deck': 2, 'shingles': 1, 'ridge': 2}:
            _fail('ROOF_INCOMPLETE', f'current tagged rectangular roof parts incomplete: {dict(parts)}')
    elif any(ob.get('roof_part') is not None for ob in roof):
        _fail('ROOF_PARTS', 'mixed or unknown tagged roof parts')
    # A building may share a name with another, but never its mesh or material IDs.
    other_meshes = {ob.data for ob in bpy.data.objects if ob.type == 'MESH' and ob not in owner_objects}
    other_materials = {slot.material for ob in bpy.data.objects if ob.type == 'MESH' and ob not in owner_objects
                       for slot in ob.material_slots if slot.material is not None}
    if any(ob.data in other_meshes for ob in body + roof):
        _fail('MESH_SHARED', 'a mesh datablock is referenced by a foreign object')
    if any(slot.material in other_materials for ob in body + roof for slot in ob.material_slots if slot.material):
        _fail('MATERIAL_SHARED', 'a material datablock is referenced by a foreign mesh object')
    pivot_local = Vector((0.0, 0.0, 0.0))
    pivot_world = root.matrix_world @ pivot_local
    # For nonzero future footprint pivot: T(-pivot) @ inverse(root) @ world_mesh.
    world_to_local = Matrix.Translation(-pivot_local) @ root.matrix_world.inverted()
    ordered = sorted(body + roof, key=lambda ob: (ob.as_pointer()))
    records = []
    materials = set()
    for ob in ordered:
        if ob.modifiers:
            _fail('MODIFIER_UNSUPPORTED', f'{ob.name!r} has modifiers; unevaluated mesh is not export proof')
        if ob.data.shape_keys is not None or ob.constraints:
            _fail('EVALUATION_UNSUPPORTED', f'{ob.name!r} has shape keys or constraints; evaluated geometry/transform is not proven')
        if (not _finite_matrix(ob.matrix_local) or not _finite_matrix(ob.matrix_world) or
                abs(ob.matrix_world.determinant()) < 1e-12):
            _fail('OBJECT_TRANSFORM', f'{ob.name!r} has invalid or singular transform')
        mesh = ob.data
        if mesh is None or not mesh.polygons or not mesh.vertices:
            _fail('MESH_EMPTY', f'{ob.name!r} has no usable mesh geometry')
        if any(not all(math.isfinite(float(v)) for v in vert.co) for vert in mesh.vertices):
            _fail('MESH_NONFINITE', f'{ob.name!r} has non-finite vertex')
        # loop_triangles is a read-only tessellation cache; no mesh copies/temporary IDs.
        mesh.calc_loop_triangles()
        poly_counts = Counter(p.material_index for p in mesh.polygons)
        tri_counts = Counter(t.material_index for t in mesh.loop_triangles)
        if any(idx < 0 or idx >= len(ob.material_slots) for idx in set(poly_counts) | set(tri_counts)):
            _fail('MATERIAL_INDEX', f'{ob.name!r} has a polygon referencing an invalid slot')
        slots = []
        for idx, slot in enumerate(ob.material_slots):
            if slot.material is None:
                _fail('MATERIAL_MISSING', f'{ob.name!r} has an empty material slot {idx}')
            materials.add(slot.material)
            slots.append(MaterialUsage(idx, slot.material, poly_counts[idx], tri_counts[idx]))
        if not slots:
            _fail('MATERIAL_MISSING', f'{ob.name!r} has no material slots')
        if sum(tri_counts.values()) != len(mesh.loop_triangles):
            _fail('TRIANGULATION', f'{ob.name!r} has inconsistent triangulation')
        records.append(MeshRecord(ob, 'roof' if ob in roof else 'body', ob.get('roof_part'), mesh,
                                  ob.matrix_local.copy(), ob.matrix_world.copy(),
                                  (world_to_local @ ob.matrix_world).copy(), len(mesh.loop_triangles), tuple(slots)))
    return BuildingGeometryResult(root, building_collection, tuple(ordered),
                                  tuple(ob for ob in ordered if ob in body),
                                  tuple(ob for ob in ordered if ob in roof), tuple(records),
                                  pivot_local.copy(), pivot_world.copy(), world_to_local.copy(),
                                  sum(r.triangles for r in records), tuple(sorted(materials, key=lambda m: m.as_pointer())),
                                  ('exclusive_collection_and_root_ancestry', 'all_meshes_triangulated',
                                   'no_modifiers_or_instances', 'private_meshes_and_materials',
                                   'ground_center_pivot_root_local'))
