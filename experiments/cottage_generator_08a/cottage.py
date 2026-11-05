"""Cottage Prototype 01: independent, deterministic Blender 5.2 mesh generator.
Run from Blender: blender -b -t 2 -P experiments/cottage_generator_08a/build_examples.py
"""
from dataclasses import dataclass
import math
import random
import bpy
from mathutils import Vector

VERSION = '08b.1'  # refine_eave=False preserves the Phase 8A geometry for comparisons.

@dataclass(frozen=True)
class Cottage:
    width: float = 5.0
    depth: float = 4.0
    wall_height: float = 2.4
    roof_pitch: float = 48.0
    seed: int = 1

    def validate(self):
        if not 3.0 <= self.width <= 8.0 or not 2.8 <= self.depth <= 9.0:
            raise ValueError('Width 3..8 m, depth 2.8..9 m')
        if not 2.0 <= self.wall_height <= 3.0 or not 35 <= self.roof_pitch <= 60:
            raise ValueError('Wall height 2..3 m, roof pitch 35..60 degrees')
        if not 0 <= self.seed <= 2**31 - 1:
            raise ValueError('Seed must be nonnegative 32-bit integer')


def material(name, rgb, rough=1.0, variation=0.0):
    m = bpy.data.materials.new('08A_' + name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value = rough
    if variation:
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 5.0
        noise.inputs['Detail'].default_value = 2.0
        tex = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tex.outputs['Generated'], noise.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .24
        ramp.color_ramp.elements[0].color = (*tuple(max(0, c * (1-variation)) for c in rgb), 1)
        ramp.color_ramp.elements[1].position = .78
        ramp.color_ramp.elements[1].color = (*tuple(min(1, c * (1+variation)) for c in rgb), 1)
        nt.links.new(noise.outputs['Fac'], ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    else:
        bs.inputs['Base Color'].default_value = (*rgb, 1)
    return m


def mesh(collection, name, vertices, faces, mat):
    data = bpy.data.meshes.new('08A_' + name)
    data.from_pydata(vertices, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    # Correct face winding for every independently constructed closed part.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(data)
    bm.free()
    return ob


def box(collection, name, center, size, mat):
    x,y,z = center; a,b,c = (v/2 for v in size)
    verts = [(x+sx*a,y+sy*b,z+sz*c) for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)]
    return mesh(collection,name,verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)


def beam(collection, name, a, b, thickness, mat):
    mid = (Vector(a)+Vector(b))*0.5
    ob = box(collection,name,(0,0,0),(thickness,thickness,(Vector(b)-Vector(a)).length),mat)
    ob.location = mid
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = Vector(b).__sub__(Vector(a)).to_track_quat('Z','Y')
    return ob


def generate(p, name, offset=(0,0,0), *, refine_eave=True):
    p.validate()
    rng = random.Random(p.seed)
    coll = bpy.data.collections.new('08A_'+name)
    bpy.context.scene.collection.children.link(coll)
    w,d,h = p.width,p.depth,p.wall_height
    half_w,half_d = w/2,d/2
    ridge = h + half_w * math.tan(math.radians(p.roof_pitch))
    plaster = material(name+'_clay',(.47,.38,.28),variation=.08)
    timber = material(name+'_weathered_oak',(.19,.125,.077),variation=.12)
    straw = material(name+'_straw',(.47+rng.uniform(-.025,.025),.36,.19),variation=.18)
    stone = material(name+'_stone',(.31,.29,.25),variation=.09)
    door_mat = material(name+'_door',(.25,.15,.085),variation=.09)
    mats = [plaster,timber,straw,stone,door_mat]
    box(coll,'08A_Sill', (0,0,.12),(w+.22,d+.22,.24),stone)
    wall_bottom=.25
    # Front opening 0.92 x 1.85 m: jambs + lintel, no wall behind the door.
    door_width=.92; door_top=2.03
    for sign in (-1,1):
        span=(w-door_width)/2
        box(coll,'08A_FrontClay', (sign*(door_width/2+span/2),-half_d,(h+wall_bottom)/2),(span,.16,h-wall_bottom),plaster)
    box(coll,'08A_FrontLintelClay',(0,-half_d,(door_top+h)/2),(door_width,.16,h-door_top),plaster)
    box(coll,'08A_RearClay',(0,half_d,(h+wall_bottom)/2),(w,.16,h-wall_bottom),plaster)
    for sign in (-1,1):
        box(coll,'08A_SideClay',(sign*half_w,0,(h+wall_bottom)/2),(.16,d,h-wall_bottom),plaster)
    # Gable triangle sits directly under the roof; no missing wall wedge.
    for y in (-half_d,half_d):
        mesh(coll,'08A_GableClay',[(-half_w,y,h),(half_w,y,h),(0,y,ridge)],[(0,1,2)],plaster)
        beam(coll,'08A_GableRafterL',(-half_w,y-.10,h),(0,y-.10,ridge),.115,timber)
        beam(coll,'08A_GableRafterR',(0,y-.10,ridge),(half_w,y-.10,h),.115,timber)
    # Sparse, structural timbers rather than imported urban-house ornamentation.
    for x in (-half_w,half_w):
        for y in (-half_d,half_d):
            beam(coll,'08A_CornerPost',(x,y,.24),(x,y,h+.08),.16,timber)
    for y in (-half_d,half_d):
        beam(coll,'08A_EndWallPlate',(-half_w,y,h),(half_w,y,h),.13,timber)
    for x in (-half_w,half_w):
        beam(coll,'08A_SideWallPlate',(x,-half_d,h),(x,half_d,h),.13,timber)
        # Braces confined to one side-wall bay and offset toward outside.
        side = x + (1 if x>0 else -1)*.09
        for y0, direction in ((-half_d+.18,1),(half_d-.18,-1)):
            beam(coll,'08A_SideBrace',(side,y0,.8),(side,y0+direction*.63,h-.10),.09,timber)
    for sign in (-1,1):
        beam(coll,'08A_DoorJamb',(sign*.51,-half_d-.12,.26),(sign*.51,-half_d-.12,door_top+.07),.12,timber)
    beam(coll,'08A_DoorLintel',(-.56,-half_d-.12,door_top+.06),(.56,-half_d-.12,door_top+.06),.13,timber)
    box(coll,'08A_Door',(0,-half_d-.115,(door_top+.25)/2),(.88,.055,door_top-.25),door_mat)
    for x in (-.24,0,.24):
        box(coll,'08A_DoorBoard',(x,-half_d-.153,1.14),(.022,.012,1.66),timber)
    # Closed roof shells: one per side. Indexed slope x depth grid, with a variable
    # eave line and a rounded, over-thickened edge. Roof is NOT a recolored plane.
    nx,ny=9,max(12,round(d*4))
    eave_x=half_w+.34
    y_end=half_d+.25
    for side in (-1,1):
        # Independent eave RNG: original material, roof and bundle streams remain intact.
        eave_rng=random.Random((p.seed << 2) ^ (0x8B51 if side < 0 else 0x8B52))
        anchors=[eave_rng.uniform(-.038,.006) for _ in range(ny+1)]
        mids=[(anchors[j]+anchors[j+1])*.5+eave_rng.uniform(-.085,.008)
              for j in range(ny)]
        outreach=[eave_rng.uniform(.09,.15) for _ in range(ny)]
        vertices=[]
        rows=[]
        for layer in (0,1):
            layer_rows=[]
            if refine_eave:
                # A short connected apron outside the original roof edge. It
                # keeps the old roof untouched and avoids long triangular spikes.
                row=[]
                for j in range(ny+1):
                    y=-y_end+2*y_end*j/ny
                    row.append(len(vertices))
                    vertices.append((side*(eave_x+.085),y,h-.10+anchors[j]-(.27 if layer else 0)))
                    if j<ny:
                        row.append(len(vertices))
                        vertices.append((side*(eave_x+outreach[j]),y+y_end/ny,
                                         h-.10+mids[j]-(.205 if layer else 0)))
                layer_rows.append(row)
            for i in range(nx+1):
                t=i/nx
                x=side*(eave_x*(1-t))
                base=h-.10+(ridge-h+.10)*t
                row=[]
                for j in range(ny+1):
                    y=-y_end + 2*y_end*j/ny
                    fringe=(1-t)**5
                    edge_var=fringe*(.052*math.sin(j*1.71+p.seed*.43+side)+rng.uniform(-.016,.016))
                    ripple=.017*math.sin(i*1.8+j*.69+p.seed*.35)*math.sin(math.pi*t)
                    thickness=.21+.06*fringe
                    row.append(len(vertices))
                    vertices.append((x+side*edge_var,y,base+ripple-(thickness if layer else 0)))
                layer_rows.append(row)
            rows.append(layer_rows)
        faces=[]
        for layer in (0,1):
            for i in range(len(rows[layer])-1):
                outer=rows[layer][i]; inner=rows[layer][i+1]
                for j in range(ny):
                    if refine_eave and i==0:
                        a,m,b=outer[2*j:2*j+3]
                        c,d2=inner[j:j+2]
                        patches=[(a,c,d2),(a,d2,m),(m,d2,b)]
                        faces.extend(tuple(reversed(face)) if layer else face for face in patches)
                    else:
                        a,b=outer[j:j+2]; c,d2=inner[j:j+2]
                        face=(a,c,d2,b)
                        faces.append(tuple(reversed(face)) if layer else face)
        # Sew the roof perimeter in index order. Every top/bottom boundary edge
        # has exactly one side wall; no floating overlays or open mesh seams.
        boundary=[]
        for i in range(len(rows[0])-1): boundary.append((rows[0][i][0],rows[0][i+1][0]))
        last=rows[0][-1]
        for j in range(ny): boundary.append((last[j],last[j+1]))
        for i in range(len(rows[0])-1,0,-1): boundary.append((rows[0][i][-1],rows[0][i-1][-1]))
        first=rows[0][0]
        for j in range(len(first)-1,0,-1): boundary.append((first[j],first[j-1]))
        # The two layers have identical indexing even at the refined lip.
        layer_size=len(vertices)//2
        faces.extend((a,b,b+layer_size,a+layer_size) for a,b in boundary)
        roof=mesh(coll,'08A_ThickThatch',vertices,faces,straw)
        roof['role']='roof'
        # Limited bundles projecting down from the eaves; stable size regardless of roof pitch.
        for j in range(ny):
            y=-y_end+(j+.5)*2*y_end/ny
            length=.13+.08*rng.random()
            beam_ob=beam(coll,'08A_EaveBundle',(side*(eave_x+.015),y,h-.08),
                         (side*(eave_x+.035),y,h-.08-length),.045,straw)
            beam_ob['role']='roof'
    # Rounded, low-poly thatch roll conceals the seam without a timber-looking plank.
    ring=12
    cap_vertices=[(.20*math.cos(k*2*math.pi/ring),y,ridge+.015+.115*math.sin(k*2*math.pi/ring))
                  for y in (-y_end,y_end) for k in range(ring)]
    cap_faces=[tuple(range(ring-1,-1,-1)),tuple(range(ring,2*ring))]
    cap_faces.extend((k,(k+1)%ring,(k+1)%ring+ring,k+ring) for k in range(ring))
    ridge_cap=mesh(coll,'08A_RidgeRoll',cap_vertices,cap_faces,straw)
    ridge_cap['role']='roof'
    for ob in coll.objects:
        ob.location += Vector(offset)
    return coll, mats
