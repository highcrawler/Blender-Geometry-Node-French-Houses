"""Phase 8D Hybrid Thatch: one 8C-B-style closed base + eave modules + fiber shader.
Does not alter the original cottage or existing roof variants.
"""
import math
import random
import bpy
from mathutils import Vector
from roofs import build_base, ridge_roll, roof_mesh


def fiber_material(original):
    m=bpy.data.materials.new('08D_Hybrid_Straw')
    m.diffuse_color=original.diffuse_color[:]
    m.use_nodes=True
    nt=m.node_tree
    nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Metallic'].default_value=0
    bs.inputs['Roughness'].default_value=.88
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    coord=nt.nodes.new('ShaderNodeTexCoord')
    broad=nt.nodes.new('ShaderNodeTexNoise')
    broad.inputs['Scale'].default_value=1.8
    broad.inputs['Detail'].default_value=2.0
    nt.links.new(coord.outputs['Object'],broad.inputs['Vector'])
    warp=nt.nodes.new('ShaderNodeMapRange')
    warp.inputs['From Min'].default_value=0
    warp.inputs['From Max'].default_value=1
    warp.inputs['To Min'].default_value=-.032
    warp.inputs['To Max'].default_value=.032
    nt.links.new(broad.outputs['Fac'],warp.inputs['Value'])
    bend=nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(warp.outputs['Result'],bend.inputs['Y'])
    add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD'
    nt.links.new(coord.outputs['Object'],add.inputs[0]);nt.links.new(bend.outputs['Vector'],add.inputs[1])
    direction=nt.nodes.new('ShaderNodeVectorMath');direction.operation='MULTIPLY'
    direction.inputs[1].default_value=(.75,27,.75)
    nt.links.new(add.outputs['Vector'],direction.inputs[0])
    fine=nt.nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value=3.5
    fine.inputs['Detail'].default_value=2.0
    nt.links.new(direction.outputs['Vector'],fine.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    r,g,b=tuple(original.diffuse_color[:3])
    ramp.color_ramp.elements[0].position=.26
    ramp.color_ramp.elements[0].color=(r*.76,g*.78,b*.79,1)
    ramp.color_ramp.elements[1].position=.76
    ramp.color_ramp.elements[1].color=(min(r*1.14,1),min(g*1.13,1),min(b*1.10,1),1)
    nt.links.new(fine.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    rough=nt.nodes.new('ShaderNodeMapRange')
    rough.inputs['To Min'].default_value=.83
    rough.inputs['To Max'].default_value=.95
    nt.links.new(fine.outputs['Fac'],rough.inputs['Value'])
    nt.links.new(rough.outputs['Result'],bs.inputs['Roughness'])
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.055
    bump.inputs['Distance'].default_value=.006
    nt.links.new(fine.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m


def strip_vertices(p,side,y_center,width,tip_t,turn,thickness=.023):
    """A three-section tapered oval-ish closed reed tuft (20 tris); parent module packs 2-3.
    Tip is narrow, curls into the drip; rear is embedded under the cover surface.
    """
    eave=p.width/2+.34
    ridge=p.wall_height+(p.width/2)*math.tan(math.radians(p.roof_pitch))
    rise=ridge-p.wall_height+.10
    vertices=[]
    for t,waist,offset in ((.21,.62,-.009),(.058,1.0,.018),(tip_t,.52,-.014)):
        x=side*eave*(1-t)
        y=y_center+turn*(.21-t)
        base=p.wall_height-.10+rise*t+offset
        for zsub in (0,thickness):
            for lateral in (-1,1):
                vertices.append((x,y+lateral*width*.5*waist,base-zsub))
    # Vertex order per section: top left/right, underside left/right.
    faces=[]
    for section in range(2):
        a=section*4;b=(section+1)*4
        faces.extend(((a,b,b+1,a+1),(a+2,a+3,b+3,b+2),
                      (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    faces.append((0,1,3,2))
    faces.append((8,10,11,9))
    return vertices,faces


def make_bundles(collection,p,mat):
    """Module spacing follows *depth*, never a fixed number of teeth.
    Three slim touching/inset strips create one irregular tuft, merged as one
    low-object-count mesh per slope. Support shell remains closed underneath.
    """
    rng=random.Random(p.seed^0x8D51)
    yend=p.depth/2+.25
    modules=max(18,round((2*yend)/.19))
    total_strips=0
    for side in (-1,1):
        vs=[];fs=[]
        spacing=2*yend/modules
        for j in range(modules):
            base_y=-yend+(j+.5)*spacing+rng.uniform(-.013,.013)
            parts=2+(1 if rng.random()<.65 else 0)
            total_strips+=parts
            for k in range(parts):
                # Neighbouring strips overlap sideways; the support roof covers
                # any remaining tiny channel and anchors the root of each tip.
                u=(k+.5)/parts-.5
                y=base_y+u*spacing*.85+rng.uniform(-.012,.012)
                width=spacing*(.58 if parts==2 else .42)
                tip=-rng.uniform(.013,.045)
                turn=rng.uniform(-.035,.035)
                verts,faces=strip_vertices(p,side,y,width,tip,turn)
                base=len(vs);vs.extend(verts)
                fs.extend(tuple(base+v for v in f) for f in faces)
        mesh=roof_mesh(collection,'EaveTufts',vs,fs,mat)
        mesh['bundle_modules']=modules
        mesh['component_strips']=total_strips
    return modules*2,total_strips


def replace_with_hybrid(collection,p):
    old=[o for o in collection.objects if o.get('role')=='roof']
    assert len(old)>2
    source=next(o.data.materials[0] for o in old if o.name.startswith('08A_ThickThatch'))
    for o in old:bpy.data.objects.remove(o,do_unlink=True)
    material=fiber_material(source)
    foundation=build_base(collection,p,material,segments=max(18,round(p.depth*3)),steps=6)
    modules,strips=make_bundles(collection,p,material)
    ridge=ridge_roll(collection,p,material,p.seed)
    assert len(foundation)==2 and ridge
    return {'bundle_modules':modules,'component_strips':strips,
            'support_objects':foundation,'bundle_objects':[o for o in collection.objects if o.name.startswith('08C_EaveTufts')],
            'ridge_object':ridge}
