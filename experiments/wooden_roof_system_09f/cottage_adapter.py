"""Thin first caller. The historical Cottage generator is read-only and intact."""
from dataclasses import dataclass
import math
import bpy
from mathutils import Vector
from roof.wooden_rect import RoofSpec, build_rectangular_roof
from cottage import Cottage, generate


@dataclass(frozen=True)
class CottageBuild:
    building_root: bpy.types.Object
    building_collection: bpy.types.Collection
    body_objects: tuple
    roof: object


def build_cottage(p: Cottage, name: str, appearance: str, location=(0,0,0), yaw=0.0):
    if not isinstance(p,Cottage):raise TypeError('p must be a Cottage')
    p.validate()
    spec=RoofSpec(p.width,p.depth,p.wall_height,p.roof_pitch,p.seed,appearance)
    spec.validate()
    xyz=tuple(location)
    if len(xyz)!=3 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in xyz):
        raise ValueError('finite 3D location required')
    if isinstance(yaw,bool) or not isinstance(yaw,(int,float)) or not math.isfinite(yaw):
        raise ValueError('finite Z yaw required')
    existing_materials=set(bpy.data.materials)
    coll=None
    try:
        # Zero historical offset: all original basis transforms remain local.
        coll,_=generate(p,name,offset=(0,0,0),refine_eave=False)
        # Remove only the historical thatch roof; preserve all Cottage body objects.
        for ob in list(coll.objects):
            if ob.get('role')=='roof':
                data=ob.data
                bpy.data.objects.remove(ob,do_unlink=True)
                if data.users==0:bpy.data.meshes.remove(data)
        for mat in set(bpy.data.materials)-existing_materials:
            if mat.users==0:bpy.data.materials.remove(mat)
        body=tuple(coll.objects)
        root=bpy.data.objects.new('Building_Root',None)
        coll.objects.link(root)
        roof=build_rectangular_roof(spec,root,coll)
        for ob in body:ob.parent=root
        root.location=Vector(xyz)
        root.rotation_euler.z=yaw
        return CottageBuild(root,coll,body,roof)
    except Exception:
        if coll is not None:
            for child in list(coll.children):
                for ob in list(child.objects):
                    data=ob.data
                    bpy.data.objects.remove(ob,do_unlink=True)
                    if data.users==0:bpy.data.meshes.remove(data)
                coll.children.unlink(child)
                bpy.data.collections.remove(child)
            for ob in list(coll.objects):
                data=ob.data if ob.type=='MESH' else None
                bpy.data.objects.remove(ob,do_unlink=True)
                if data and data.users==0:bpy.data.meshes.remove(data)
            bpy.data.collections.remove(coll)
        for mat in set(bpy.data.materials)-existing_materials:
            if mat.users==0:bpy.data.materials.remove(mat)
        raise
