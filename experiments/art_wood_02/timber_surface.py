"""One module-local aged rail mesh and its long-axis UV for a 4-face oak atlas."""
import bpy,bmesh

def age(ob,length,thickness,report):
    # Divide ONLY the four longitudinal edges into 16 sections: flat end caps
    # and the same construction centerlines, without all-face subdivision.
    bm=bmesh.new();bm.from_mesh(ob.data)
    long_edges=[e for e in bm.edges if abs(e.verts[0].co.z-e.verts[1].co.z)>.9*length]
    assert len(long_edges)==4
    bmesh.ops.subdivide_edges(bm,edges=long_edges,cuts=15,use_grid_fill=True)
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    vg=ob.vertex_groups.new(name='WOOD02_EndFade')
    for vertex in ob.data.vertices:
        d=length/2-abs(vertex.co.z)
        vg.add([vertex.index],max(0.,min(1.,d/.55)),'REPLACE')
    tex=bpy.data.textures.new('WOOD02_clouds',type='CLOUDS')
    tex.noise_scale=.72;tex.noise_depth=2
    disp=ob.modifiers.new('WOOD02_subtle_end_faded_displace','DISPLACE')
    disp.texture=tex;disp.texture_coords='LOCAL';disp.strength=.003;disp.mid_level=.5;disp.vertex_group=vg.name
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=disp.name)
    # Three shallow axe-hewn top-edge facets; neither end nor the midpoint
    # connector axes move. They taper over ~0.5 m, not repeated box-wide waves.
    from math import exp
    for vertex in ob.data.vertices:
        if vertex.co.y > thickness*.40:
            z=vertex.co.z
            fade=min(1.,max(0.,(length/2-abs(z))/.70))
            dent=sum(depth*exp(-((z-center)/radius)**2)
                     for center,depth,radius in ((-2.55,.008,.32),(.37,.006,.51),(2.83,.011,.29)))
            vertex.co.y-=dent*fade
    ob.data.update()
    bevel=ob.modifiers.new('WOOD02_small_broken_edges','BEVEL')
    bevel.width=.004;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=.5
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    ob.data.update()
    mesh=bmesh.new();mesh.from_mesh(ob.data)
    assert all(e.is_manifold for e in mesh.edges) and mesh.calc_volume(signed=True)>0
    mesh.free()
    zs=[v.co.z for v in ob.data.vertices]
    assert abs(min(zs)+length/2)<1e-5 and abs(max(zs)-length/2)<1e-5
    report.update({'longitudinal_subdivision_cuts':15,'displace_type':'CLOUDS',
                   'displace_strength_m':.003,'clouds_scale_m':.72,'end_fade_m':.55,
                   'bevel_width_m':.004,'bevel_segments':2,'bevel_limit_radians':.5,
                   'applied_before_export':True,'hewn_top_facets':3,'max_facet_depth_m':.011,
                   'watertight_positive_volume':True,
                   'end_plane_z':[min(zs),max(zs)]})
    uv=ob.data.uv_layers.new(name='WOOD02_LocalZ_LongAxis')
    # Face normals select 1 of 4 side bands. U always follows +local Z;
    # V follows short side axis. End caps sample a neutral central atlas patch.
    for polygon in ob.data.polygons:
        n=polygon.normal
        if abs(n.z)>.70:
            band=3;ax=0
        elif abs(n.x)>=abs(n.y):
            band=0 if n.x>0 else 1;ax=1
        else:
            band=2 if n.y>0 else 3;ax=0
        for li in polygon.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            if abs(n.z)>.70:
                u=.97 if n.z>0 else .03;across=.5
            else:
                u=max(.005,min(.995,(v.z/length+.5)))
                across=max(.02,min(.98,(v[ax]/thickness+.5)))
            uv.data[li].uv=(u,(band+across)/4)
    report['uv']={'longitudinal_axis':'local Z → atlas U','face_strips':4,
                  'world_u_length_m':length,'atlas_uv_layer':uv.name}
    return tex

def atlas_material(name,oak_color,material_source,color_path,normal_path,report):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*oak_color,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=1.;bs.inputs['Metallic'].default_value=0
    color=bpy.data.images.load(str(color_path),check_existing=True);color.colorspace_settings.name='sRGB'
    normal=bpy.data.images.load(str(normal_path),check_existing=True);normal.colorspace_settings.name='Non-Color'
    nodes=m.node_tree.nodes;links=m.node_tree.links
    c=nodes.new('ShaderNodeTexImage');c.image=color;links.new(c.outputs['Color'],bs.inputs['Base Color'])
    n=nodes.new('ShaderNodeTexImage');n.image=normal
    nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.7
    links.new(n.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    report.update({'material':m.name,'color':str(color_path),'normal':str(normal_path),
                   'normal_strength':.7,'roughness':1.,'metallic':0,
                   'pipeline':'deterministic procedural atlas rasterization; direct native GLB image/normal nodes; no bake required'})
    return m
