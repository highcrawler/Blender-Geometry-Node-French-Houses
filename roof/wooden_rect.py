"""One symmetric rectangular wooden-shingle roof. Phase-9D geometry, unchanged.

Coordinates are building-root local. No Cottage, addon, or global scene seed dependency.
"""
from dataclasses import dataclass
import math
import numbers
import random

import bmesh
import bpy


@dataclass(frozen=True)
class RoofSpec:
    width_m: float
    depth_m: float
    wall_height_m: float
    pitch_degrees: float
    seed: int
    appearance: str

    def validate(self):
        for name, lower, upper in (('width_m', 3.0, 8.0), ('depth_m', 2.8, 9.0),
                                   ('wall_height_m', 2.0, 3.0), ('pitch_degrees', 35.0, 60.0)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, numbers.Real) or not math.isfinite(value) or not lower <= value <= upper:
                raise ValueError(f'{name} must be a finite number in [{lower}, {upper}]')
        if type(self.seed) is not int or not 0 <= self.seed <= 2**31-1:
            raise ValueError('seed must be a nonnegative 32-bit integer')
        if self.appearance not in ('CLEAN', 'AGED') or type(self.appearance) is not str:
            raise ValueError('appearance must be CLEAN or AGED')


@dataclass(frozen=True)
class RoofResult:
    roof_collection: bpy.types.Collection
    deck_objects: tuple
    shingle_object: bpy.types.Object
    ridge_objects: tuple
    courses_per_side: int
    shingle_count: int


def _material(name, rgb, created):
    # Exact Phase-9A roof_material shader values and node defaults.
    mat = bpy.data.materials.new('09A_' + name)
    created.append(mat)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = .92
    bs.inputs['Metallic'].default_value = 0
    return mat


def _mesh(collection, name, vertices, faces, mat, meshes, objects):
    # Exact Phase-8A mesh.from_pydata / BMesh face-normal path used in 9A.
    data = bpy.data.meshes.new('08A_' + name)
    meshes.append(data)
    data.from_pydata(vertices, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    objects.append(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    bm = bmesh.new()
    try:
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(data)
    finally:
        bm.free()
    return ob


def _roof_geometry(coll, spec, aged, mats_created, meshes_created, objects_created):
    # The arithmetic and RNG consumption below follow 9D roof_geometry in order.
    rng = random.Random(spec.seed ^ 0x9A08)
    colors = ([(.29,.185,.105), (.35,.235,.141), (.245,.165,.105), (.32,.205,.12)] if not aged else
              [(.17,.155,.133), (.235,.21,.172), (.28,.245,.193), (.22,.265,.139)])
    mats = [_material(('AGED' if aged else 'CLEAN') + '_' + str(i), c, mats_created) for i,c in enumerate(colors)]
    eave_x = spec.width_m / 2 + .34
    y_end = spec.depth_m / 2 + .25
    ridge = spec.wall_height_m + spec.width_m / 2 * math.tan(math.radians(spec.pitch_degrees))
    # Substrate: thin closed plank under the shingle field, not the old straw shell.
    decks=[]
    for side in (-1, 1):
        vertices=[]
        for x,z in ((eave_x, spec.wall_height_m-.10), (0, ridge)):
            for y in (-y_end, y_end):
                for bottom in (True, False):
                    vertices.append((side*x,y,z+(-.13 if bottom else .012)))
        faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
        ob=_mesh(coll,'09A_Deck',vertices,faces,mats[0],meshes_created,objects_created); ob['role']='roof'
        decks.append(ob)
    # Each closed shingle has eight vertices and six quads. Courses overlap by ~42%.
    vertices=[]; faces=[]; indices=[]; moss=0; shingles=0
    slope_length=math.hypot(eave_x, ridge-(spec.wall_height_m-.10))
    course_step=.185
    shingle_length=.315
    n_courses=math.ceil(slope_length/course_step)
    courses_by_side=[]
    for side in (-1,1):
        side_courses=0
        for row in range(n_courses):
            start=row*course_step
            if start > slope_length-.06: continue
            before_row=shingles
            offset= (-.135 if row%2 else 0) + rng.uniform(-.018,.018)
            cursor=-y_end+offset
            while cursor < y_end:
                width=max(.205,min(.335,rng.gauss(.272,.029)))
                left=max(-y_end,cursor)
                right=min(y_end,cursor+width)
                cursor+=width+.006
                if right-left < .07: continue
                length=min(shingle_length+rng.uniform(-.016,.016),slope_length-start+.025)
                # End cuts vary a few millimeters; upper ends remain straight beneath next course.
                cut_l=rng.uniform(-.009,.009)
                cut_r=rng.uniform(-.009,.009)
                def point(distance,y,height):
                    t=distance/slope_length
                    return (side*(eave_x*(1-t)), y, spec.wall_height_m-.10+(ridge-(spec.wall_height_m-.10))*t+height)
                # Top face is slightly tapered in thickness; outward tip rides over the previous course.
                base=len(vertices)
                vertices.extend((point(start,left+cut_l,.115),point(start,right+cut_r,.115),
                                 point(start+length,right-.004,.073),point(start+length,left+.004,.073),
                                 point(start,left+cut_l,.085),point(start,right+cut_r,.085),
                                 point(start+length,right-.004,.049),point(start+length,left+.004,.049)))
                quads=((0,1,2,3),(7,6,5,4),(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3))
                faces.extend(tuple(base+i for i in q) for q in quads)
                # Aged moss is only a sparse material tint on existing shingles, biased to eave
                # and one damp slope. It introduces NO extra polygons or new roof geometry.
                damp=(row<4 and side<0) or (row>n_courses-4 and side<0)
                moss_roll=rng.random()  # same RNG consumption in both states
                use_moss=aged and damp and moss_roll<.19
                wood_tone=rng.randrange(3)
                tone=3 if use_moss else wood_tone
                indices.extend([tone]*6)
                moss+=int(use_moss)
                shingles+=1
            if shingles>before_row:side_courses+=1
        courses_by_side.append(side_courses)
    assert courses_by_side[0]==courses_by_side[1], courses_by_side
    cover=_mesh(coll,'09A_ShingleField',vertices,faces,mats[0],meshes_created,objects_created);cover['role']='roof'
    for mat in mats[1:]:cover.data.materials.append(mat)
    for face,idx in zip(cover.data.polygons,indices):face.material_index=idx
    # Two simple staggered ridge planks cover the seam and meet the slope naturally.
    caps=[]
    for side in (-1,1):
        verts=[]
        for x,z in ((.0,ridge+.07),(.235,ridge-.105)):
            for y in (-y_end-.035,y_end+.035):
                for under in (0,.035):verts.append((side*x,y,z-under))
        ob=_mesh(coll,'09A_RidgeCap',verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mats[1],meshes_created,objects_created);ob['role']='roof'
        caps.append(ob)
    return decks,cover,caps,courses_by_side[0],shingles


def build_rectangular_roof(spec: RoofSpec, building_root, building_collection) -> RoofResult:
    if not isinstance(spec, RoofSpec):
        raise TypeError('spec must be RoofSpec')
    spec.validate()
    if (not isinstance(building_collection, bpy.types.Collection) or
            not isinstance(building_root, bpy.types.Object) or building_root.type!='EMPTY'):
        raise ValueError('a per-building Collection and EMPTY root are required')
    if (tuple(building_root.users_collection)!=(building_collection,) or building_collection.users!=1 or
            building_root.parent is not None or building_root.rotation_mode!='XYZ' or
            sum(o.type=='EMPTY' and o.parent is None for o in building_collection.objects)!=1 or
            any(not math.isfinite(float(x)) for x in (*building_root.location,*building_root.rotation_euler,*building_root.scale)) or
            any(abs(s-1)>1e-8 for s in building_root.scale) or
            abs(building_root.rotation_euler.x)>1e-8 or abs(building_root.rotation_euler.y)>1e-8):
        raise ValueError('root must be uniquely owned, unparented, with unit scale and only Z rotation')
    if any(o.parent==building_root and o.get('role')=='roof' for o in building_root.children):
        raise ValueError('root already owns a roof')
    # A new Collection is always exclusively nested under the supplied owner.
    coll=bpy.data.collections.new('Wooden_Roof')
    mats_created=[];meshes_created=[];objects_created=[]
    try:
        building_collection.children.link(coll)
        decks,cover,caps,courses,shingles=_roof_geometry(coll,spec,spec.appearance=='AGED',
                                                    mats_created,meshes_created,objects_created)
        for ob,part in [(decks[0],'deck'),(decks[1],'deck'),(cover,'shingles'),
                        (caps[0],'ridge'),(caps[1],'ridge')]:
            ob.parent=building_root
            ob['roof_part']=part
        return RoofResult(coll,tuple(decks),cover,tuple(caps),courses,shingles)
    except Exception:
        for ob in reversed(objects_created):
            if ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)
        for data in reversed(meshes_created):
            if data.name in bpy.data.meshes and data.users==0:bpy.data.meshes.remove(data)
        if coll.name in bpy.data.collections:
            if coll.name in building_collection.children:building_collection.children.unlink(coll)
            bpy.data.collections.remove(coll)
        for mat in reversed(mats_created):
            if mat.name in bpy.data.materials and mat.users==0:bpy.data.materials.remove(mat)
        raise
