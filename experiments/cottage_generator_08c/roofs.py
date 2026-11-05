"""Phase 8C isolated roof construction spike; no changes to cottage.py.
Generate the 08B cottage first, then replace ONLY objects marked role=roof.
"""
import math
import random
import bpy
from mathutils import Vector


def roof_mesh(collection, name, vertices, faces, material):
    data=bpy.data.meshes.new('08C_'+name)
    data.from_pydata(vertices,[],faces)
    data.update()
    obj=bpy.data.objects.new('08C_'+name,data)
    collection.objects.link(obj)
    data.materials.append(material)
    obj['role']='roof'
    import bmesh
    bm=bmesh.new();bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)<0:
        bmesh.ops.reverse_faces(bm,faces=bm.faces)
    bm.to_mesh(data);bm.free()
    return obj


def shell(collection,name,positions,material):
    """Closed top/bottom structured surface, sewn on all four boundaries."""
    rows=len(positions);cols=len(positions[0][0]);assert rows>=2 and cols>=2
    assert all(len(row[0])==cols and len(row[1])==cols for row in positions)
    verts=[v for layer in (0,1) for row in positions for v in row[layer]]
    n=rows*cols
    faces=[]
    for layer in (0,1):
        for i in range(rows-1):
            for j in range(cols-1):
                a=layer*n+i*cols+j
                q=(a,a+cols,a+cols+1,a+1)
                faces.append(q if layer==0 else tuple(reversed(q)))
    perimeter=[]
    for i in range(rows-1):perimeter.append((i*cols,(i+1)*cols))
    for j in range(cols-1):perimeter.append(((rows-1)*cols+j,(rows-1)*cols+j+1))
    for i in range(rows-1,0,-1):perimeter.append((i*cols+cols-1,(i-1)*cols+cols-1))
    for j in range(cols-1,0,-1):perimeter.append((j,j-1))
    faces.extend((a,b,b+n,a+n) for a,b in perimeter)
    return roof_mesh(collection,name,verts,faces,material)


def straw_shader(source, name, strength=1.0):
    """Directed fiber-color shader: y-frequency high, slope-frequency low.
    No image textures; Blender procedural nodes are NOT available in GLB.
    """
    mat=source.copy();mat.name='08C_Fibrous_'+name
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    for link in list(bs.inputs['Base Color'].links):nt.links.remove(link)
    tex=nt.nodes.new('ShaderNodeTexCoord')
    vec=nt.nodes.new('ShaderNodeVectorMath');vec.operation='MULTIPLY'
    vec.inputs[1].default_value=(.55,22.0,.55)
    noise=nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=3.2
    noise.inputs['Detail'].default_value=2.0
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    rgb=tuple(mat.diffuse_color[:3]);
    ramp.color_ramp.elements[0].position=.29
    ramp.color_ramp.elements[0].color=(*[c*(1-.27*strength) for c in rgb],1)
    ramp.color_ramp.elements[1].position=.73
    ramp.color_ramp.elements[1].color=(*[min(c*(1+.18*strength),1) for c in rgb],1)
    nt.links.new(tex.outputs['Object'],vec.inputs[0])
    nt.links.new(vec.outputs['Vector'],noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.12*strength
    bump.inputs['Distance'].default_value=.014
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat


def ridge_roll(collection,p,mat,seed):
    rng=random.Random(seed^0xC835)
    w,d,h=p.width,p.depth,p.wall_height
    height=h+(w/2)*math.tan(math.radians(p.roof_pitch))
    yend=d/2+.25
    rings=8; sides=12
    heights=[0.0]+[rng.uniform(-.016,0) for _ in range(rings)]
    verts=[]
    for j in range(rings+1):
        y=-yend+2*yend*j/rings
        for k in range(sides):
            a=k*2*math.pi/sides
            verts.append((.20*math.cos(a),y,height+.015+heights[j]+.115*math.sin(a)))
    faces=[tuple(range(sides-1,-1,-1)),tuple(range(rings*sides,(rings+1)*sides))]
    faces.extend((j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k)
                 for j in range(rings) for k in range(sides))
    return roof_mesh(collection,'RidgeRoll',verts,faces,mat)


def build_base(collection,p,mat,segments=20,steps=5):
    """Continuous watertight support shell, same pitch/ridge as 08B."""
    rng=random.Random(p.seed^0xC820)
    w,d,h=p.width,p.depth,p.wall_height
    ridge=h+(w/2)*math.tan(math.radians(p.roof_pitch))
    eave=w/2+.34;yend=d/2+.25
    objects=[]
    for side in (-1,1):
        anchors=[rng.uniform(-.022,.018) for _ in range(segments+1)]
        positions=[]
        for i in range(steps+1):
            t=i/steps
            row=[[],[]]
            for j in range(segments+1):
                y=-yend+2*yend*j/segments
                fringe=(1-t)**5
                x=side*(eave*(1-t)+fringe*(.01+anchors[j]))
                z=h-.10+(ridge-h+.10)*t+fringe*anchors[j]
                row[0].append((x,y,z))
                row[1].append((x,y,z-(.22+.045*fringe)))
            positions.append(row)
        objects.append(shell(collection,'SupportThatch',positions,mat))
    return objects


def build_a(collection,p,mat):
    """Overlapping puffy volumes; subtle directed fiber shade is secondary."""
    mat=straw_shader(mat,'Long_A',strength=.35)
    build_base(collection,p,mat,segments=23,steps=6)
    rng=random.Random(p.seed^0xC8A1)
    w,d,h=p.width,p.depth,p.wall_height
    ridge=h+(w/2)*math.tan(math.radians(p.roof_pitch))
    eave=w/2+.34;yend=d/2+.25
    # Nine rows per slope, 19 depth intervals: an intentional modest layer budget.
    for side in (-1,1):
        for row_no in range(9):
            lower=row_no/9
            upper=min(1.,(row_no+1)/9+.028)
            depth_steps=19
            offsets=[rng.uniform(-.013,.013) for _ in range(depth_steps+1)]
            lengths=[rng.uniform(-.013,.015) for _ in range(depth_steps+1)]
            positions=[]
            for i in range(4):
                s=i/3
                cross=[[],[]]
                for j in range(depth_steps+1):
                    y=-yend+2*yend*j/depth_steps
                    # Slope-direction overlap is small; volume stays anchored
                    # *inside* the support surface at its underside.
                    t=max(0,min(1,lower+(upper-lower)*s+lengths[j]*(1-s)**3))
                    x=side*(eave*(1-t))
                    base=h-.10+(ridge-h+.10)*t
                    cap=.017+.063*math.sin(math.pi*s)+offsets[j]*math.sin(math.pi*s)
                    cross[0].append((x,y,base+cap))
                    cross[1].append((x,y,base-.006))
                positions.append(cross)
            shell(collection,'Layer_%02d'%row_no,positions,mat)
    ridge_roll(collection,p,mat,p.seed)


def build_b(collection,p,source_mat):
    """Cheap continuous shell, directional shader and few embedded short rolls."""
    mat=straw_shader(source_mat,'Long')
    build_base(collection,p,mat,segments=20,steps=6)
    rng=random.Random(p.seed^0xC8B1)
    w,d,h=p.width,p.depth,p.wall_height
    ridge=h+(w/2)*math.tan(math.radians(p.roof_pitch))
    eave=w/2+.34;yend=d/2+.25
    # Exactly 12 long narrow tapered rolls per slope, integrated into the
    # surface by placing their undersides 0.012 m below the support shell.
    for side in (-1,1):
        for j in range(12):
            y=-yend+(j+.5)*(2*yend/12)+rng.uniform(-.09,.09)
            width=.045+rng.uniform(0,.028)
            start=rng.uniform(.035,.075)
            verts=[]
            for t in (start,start+.14,start+.27+rng.uniform(-.015,.02)):
                x=side*(eave*(1-t))
                z=h-.10+(ridge-h+.10)*t
                for yy,zz in ((y-width/2,z-.045),(y,z+.025),(y+width/2,z-.045)):
                    verts.append((x,yy,zz))
            faces=[]
            for i in range(2):
                for k in range(2):
                    a=i*3+k
                    faces.append((a,a+3,a+4,a+1))
            roof_mesh(collection,'TaperedRoll',verts,faces,mat)
    ridge_roll(collection,p,mat,p.seed)


def replace(collection,p,variant):
    assert variant in ('A','B')
    roofs=[obj for obj in collection.objects if obj.get('role')=='roof']
    assert len(roofs)>2
    # Extract the existing color before deleting its objects; materials remain
    # datablocks. Non-roof geometry and material IDs are left untouched.
    source=next(o.data.materials[0] for o in roofs if o.name.startswith('08A_ThickThatch'))
    for obj in roofs:bpy.data.objects.remove(obj,do_unlink=True)
    if variant=='A':build_a(collection,p,source)
    else:build_b(collection,p,source)
