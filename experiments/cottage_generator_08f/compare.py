"""Blender 5.2.2: blender -b -t 4 -P experiments/cottage_generator_08f/compare.py"""
import bpy
import hashlib
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'cottage_generator_08d'
sys.path[:0] = [str(SOURCE), str(ROOT.parent / 'cottage_generator_08a'),
                str(ROOT.parent / 'cottage_generator_08c')]
from cottage import Cottage, generate
from hybrid import replace_with_hybrid

assert bpy.app.version[:2] == (5, 2)
p = Cottage(**json.loads((SOURCE / 'long.json').read_text()))
assert (p.width, p.depth, p.wall_height, p.roof_pitch, p.seed) == (5.1, 7.3, 2.3, 40, 23)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
(ROOT / 'screenshots').mkdir(exist_ok=True)


def roofs(collection):
    return [o for o in collection.objects if o.get('role') == 'roof']


def mesh_id(o):
    """Mesh geometry only, independently of material/UV, object naming and ordering."""
    h = hashlib.sha256()
    for v in o.data.vertices:
        h.update(repr(tuple(round(float(x), 6) for x in o.matrix_basis @ v.co)).encode())
    for face in o.data.polygons:
        h.update(repr(tuple(face.vertices)).encode())
    return h.hexdigest()


def fingerprints(objs):
    return Counter(mesh_id(o) for o in objs)


def triangles(objs):
    return sum(len(f.vertices)-2 for o in objs for f in o.data.polygons)


def material_count(collection):
    return len({m.as_pointer() for o in collection.objects for m in o.data.materials})


def make_cc0():
    m = bpy.data.materials.new('08F_PolyHaven_Thatch_Roof_Angled_CC0')
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    links = m.node_tree.links
    out = n.new('ShaderNodeOutputMaterial')
    bs = n.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Metallic'].default_value = 0.0
    links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    uv = n.new('ShaderNodeUVMap')
    uv.uv_map = '08F_RoofSlope'
    mapping = {'diff': ('jpg', 'sRGB', 'Base Color'),
               'rough': ('png', 'Non-Color', 'Roughness'),
               'nor_gl': ('png', 'Non-Color', None)}
    images = {}
    for channel, (ext, colorspace, socket) in mapping.items():
        filename = f'thatch_roof_angled_{channel}_2k.{ext}'
        path = ROOT / 'textures' / filename
        assert path.is_file(), path
        im = bpy.data.images.load(str(path), check_existing=True)
        assert tuple(im.size) == (2048, 2048), (path, im.size)
        im.colorspace_settings.name = colorspace
        # Keep absolute path while the unsaved scene renders; switch to project-
        # relative paths only immediately before saving the final .blend.
        im.filepath = str(path)
        tex = n.new('ShaderNodeTexImage')
        tex.label = channel
        tex.image = im
        tex.extension = 'REPEAT'
        links.new(uv.outputs['UV'], tex.inputs['Vector'])
        if socket:
            links.new(tex.outputs['Color'], bs.inputs[socket])
        else:
            normal = n.new('ShaderNodeNormalMap')
            normal.space = 'TANGENT'
            normal.inputs['Strength'].default_value = 1.0
            links.new(tex.outputs['Color'], normal.inputs['Color'])
            links.new(normal.outputs['Normal'], bs.inputs['Normal'])
        images[channel] = dict(filename=filename, colorspace=colorspace,
                               dimensions=list(im.size), bytes=path.stat().st_size,
                               sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    assert len([node for node in n if node.type == 'TEX_IMAGE']) == 3
    return m, images


def apply_slope_uv(collection, material):
    """Loop UV only; no vertex displacement, remesh, normals or new roof parts.

    Texture's reeds run vertically in the source image (V). V rises from the
    ridge toward each eave; U follows the cottage's long axis. The tile is
    0.9 m in projected roof coordinates, not per-object normalized UVs.
    """
    tile_m = .9
    cos_pitch = math.cos(math.radians(p.roof_pitch))
    bounds = []
    for obj in roofs(collection):
        uv = obj.data.uv_layers.get('08F_RoofSlope') or obj.data.uv_layers.new(name='08F_RoofSlope')
        material_slots = obj.data.materials
        material_slots.clear()
        material_slots.append(material)
        for face in obj.data.polygons:
            for li in face.loop_indices:
                vertex = obj.data.vertices[obj.data.loops[li].vertex_index].co
                if abs(face.normal.y) > .8 and obj.name.startswith('08C_RidgeRoll'):
                    coords = (vertex.x/tile_m, vertex.z/tile_m)  # round end cap
                elif abs(face.normal.y) > .8:  # gable end: use its actual height as U
                    coords = (vertex.z/tile_m, abs(vertex.x)/(cos_pitch*tile_m))
                elif abs(face.normal.x) > .95:  # overhanging eave cut edge
                    coords = (vertex.y/tile_m, vertex.z/tile_m)
                else:  # two slopes: image fibers along V from ridge to eave
                    coords = (vertex.y/tile_m, abs(vertex.x)/(cos_pitch*tile_m))
                uv.data[li].uv = coords
                bounds.append(tuple(coords))
        assert len(uv.data) == len(obj.data.loops)
        assert all(math.isfinite(k) for pair in bounds for k in pair)
    collapsed = 0
    for obj in roofs(collection):
        uv = obj.data.uv_layers['08F_RoofSlope']
        for face in obj.data.polygons:
            points = [uv.data[i].uv for i in face.loop_indices]
            twice_area = sum(points[i].x*points[(i+1)%len(points)].y -
                             points[(i+1)%len(points)].x*points[i].y
                             for i in range(len(points)))
            if abs(twice_area) < 1e-8:
                collapsed += 1
    assert collapsed == 0, ('UV faces collapsed', collapsed)
    return {'uv_map': '08F_RoofSlope', 'tile_m': tile_m, 'collapsed_uv_faces': collapsed, 'u_range':
            [round(min(x for x, _ in bounds), 4), round(max(x for x, _ in bounds), 4)],
            'v_range': [round(min(y for _, y in bounds), 4), round(max(y for _, y in bounds), 4)],
            'objects_with_uv': len(roofs(collection)), 'loops_mapped': len(bounds)}


collections = {}
create_ms = {}
for label in ('BASELINE', 'CC0'):
    start = time.perf_counter()
    c, _ = generate(p, '08F_'+label)
    info = replace_with_hybrid(c, p)
    bpy.context.view_layer.update()
    assert info['bundle_modules'] == 82 and info['component_strips'] == 219
    create_ms[label] = round((time.perf_counter()-start)*1000, 2)
    collections[label] = c
baseline, cc0 = collections.values()
assert fingerprints(baseline.objects) == fingerprints(cc0.objects)
assert fingerprints(roofs(baseline)) == fingerprints(roofs(cc0))
assert triangles(roofs(baseline)) == triangles(roofs(cc0)) == 5872
assert triangles(baseline.objects) == triangles(cc0.objects) == 6234
# Independently verify the existing 8D H geometry without altering the archive.
archived = SOURCE / 'variant_h_meshes.blend'
with bpy.data.libraries.load(str(archived), link=False) as (src, loaded):
    assert '08A_08D_VARIANT_H' in src.collections
    loaded.collections = ['08A_08D_VARIANT_H']
old = loaded.collections[0]
assert fingerprints(old.objects) == fingerprints(baseline.objects)
for obj in list(old.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.collections.remove(old)
material, image_metrics = make_cc0()
uv_metrics = apply_slope_uv(cc0, material)
assert fingerprints(baseline.objects) == fingerprints(cc0.objects)
assert all(o.data.uv_layers.get('08F_RoofSlope') for o in roofs(cc0))
assert all(not o.data.uv_layers.get('08F_RoofSlope') for o in roofs(baseline))
assert material_count(baseline) == material_count(cc0) == 5
for c in collections.values():
    assert all(o.data.materials for o in c.objects)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 800
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.19, .195, .21, 1)
bg.inputs['Strength'].default_value = .75


def area(name, xyz, power, size):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = power
    d.shape = 'DISK'
    d.size = size
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = xyz
    o.rotation_euler = (Vector((0, 0, 2))-o.location).to_track_quat('-Z', 'Y').to_euler()

area('08F_Key', (0, -5, 9), 1000, 7)
area('08F_Fill', (-6, 1, 6), 430, 6)
camdata = bpy.data.cameras.new('08F_Camera')
camdata.type = 'ORTHO'
cam = bpy.data.objects.new('08F_Camera', camdata)
scene.collection.objects.link(cam)
scene.camera = cam
views = {'iso': ((9, -11, 8), (0, 0, 1.7), 11.5),
         'front': ((0, -13, 4), (0, 0, 2), 10.4),
         'detail': ((5, -3.5, 5.8), (1.9, -1.5, 3.0), 4.8),
         'eave': ((5, -3.5, 4.5), (2.15, -1.2, 2.9), 4.0)}
for kind, (eye, target, scale) in views.items():
    scene.render.resolution_x, scene.render.resolution_y = (480, 360) if kind == 'iso_300' else (800, 600)
    for label, collection in collections.items():
        for other_label, other in collections.items():
            for obj in other.objects:
                obj.hide_render = other_label != label
        bpy.context.view_layer.update()
        cam.location = eye
        cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z', 'Y').to_euler()
        camdata.ortho_scale = scale
        scene.render.filepath = str(ROOT/'screenshots'/f'{label.lower()}_{kind}.png')
        bpy.ops.render.render(write_still=True)
        print('08F_RENDER', label, kind, flush=True)
    if kind == 'iso':
        # Render native 480x360 output, never resize the high-resolution image.
        scene.render.resolution_x, scene.render.resolution_y = 480, 360
        for label, collection in collections.items():
            for other_label, other in collections.items():
                for obj in other.objects:
                    obj.hide_render = other_label != label
            bpy.context.view_layer.update()
            cam.location = eye
            cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z', 'Y').to_euler()
            camdata.ortho_scale = scale
            scene.render.filepath = str(ROOT/'screenshots'/f'{label.lower()}_iso_300.png')
            bpy.ops.render.render(write_still=True)
            print('08F_RENDER', label, 'iso_300', flush=True)
        scene.render.resolution_x, scene.render.resolution_y = 800, 600

metrics = {'blender': bpy.app.version_string, 'source_commit': 'e6ec104',
           'configuration': vars(p), 'images': image_metrics, 'uv': uv_metrics,
           'variants': {label: {'roof_triangles': triangles(roofs(c)),
                                'total_triangles': triangles(c.objects),
                                'roof_meshes': len(roofs(c)),
                                'materials': material_count(c),
                                'creation_ms_single_run': create_ms[label],
                                'matches_archived_08d_mesh': True if label == 'BASELINE' else None}
                        for label, c in collections.items()}}
metrics['geometry_unchanged'] = fingerprints(baseline.objects) == fingerprints(cc0.objects)
metrics['texture_disk_bytes'] = sum(x['bytes'] for x in image_metrics.values())
(ROOT/'measurements.json').write_text(json.dumps(metrics, indent=2)+'\n')
# Save two side-by-side but do not use the displaced inspection scene for the renders.
for label, collection in collections.items():
    for obj in collection.objects:
        obj.hide_render = False
        if label == 'CC0':
            obj.location.y += 9
scene.render.resolution_x, scene.render.resolution_y = 800, 600
bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version = 0
for item in image_metrics.values():
    bpy.data.images[item['filename']].filepath = '//textures/' + item['filename']
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Cottage_CC0_08F.blend'))
print('08F_PASS', json.dumps(metrics), flush=True)
