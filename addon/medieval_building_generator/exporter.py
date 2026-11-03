"""Selected-house export. Original generator, scene and materials are never edited."""
import json
import math
import os
from pathlib import Path
import re
import struct
import tempfile
from collections import Counter

import bpy
from mathutils import Vector
from .assets import AssetError, HOUSE_TAG, generator_modifier, socket, validate


class ExportError(RuntimeError):
    pass


def valid_house(context, obj):
    return bool(obj and context.active_object == obj and obj.get(HOUSE_TAG) and obj.type == 'MESH'
                and obj.name in context.view_layer.objects
                and generator_modifier(obj) and context.mode == 'OBJECT')


def filename_for(obj):
    name = re.sub(r'[^\w-]+', '_', obj.name, flags=re.UNICODE).strip('_')
    return (name or 'Medieval_House')[:120] + '.glb'


def _input_pivot(obj):
    """Input footprint AABB center in XY and lowest input elevation, never decorations."""
    used = {i for face in obj.data.polygons for i in face.vertices}
    if len(used) < 3:
        raise ExportError('Kein gültiger flächiger Eingabegrundriss vorhanden.')
    pts = [obj.data.vertices[i].co for i in used]
    if not all(math.isfinite(c) for p in pts for c in p):
        raise ExportError('Grundriss enthält ungültige Koordinaten.')
    lo = Vector(tuple(min(p[i] for p in pts) for i in range(3)))
    hi = Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    if min(hi.x-lo.x, hi.y-lo.y) < 1e-5 or hi.z-lo.z > .1*min(hi.x-lo.x, hi.y-lo.y):
        raise ExportError('Eingabe ist kein annähernd ebener Hausgrundriss; Export abgebrochen.')
    return Vector(((lo.x+hi.x)/2, (lo.y+hi.y)/2, lo.z))


def _support_pivot(obj, context=None):
    """Bounded fallback: lower band of the known IRCSS supporting-wall material."""
    dg = (context or bpy.context).evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(dg)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
    try:
        used = {i for p in mesh.polygons
                if p.material_index < len(mesh.materials) and mesh.materials[p.material_index]
                and re.sub(r'\.\d{3}$', '', mesh.materials[p.material_index].name) == 'GroundFloorWalls'
                for i in p.vertices}
        pts = [mesh.vertices[i].co.copy() for i in used]
        if not pts or not all(math.isfinite(c) for p in pts for c in p):
            raise ExportError('Kein endlicher tragender IRCSS-Gebäudekörper für einen sicheren Pivot vorhanden.')
        bottom = min(p.z for p in pts)
        band = max(.001, .01*(max(p.z for p in pts)-bottom))
        base = [p for p in pts if p.z <= bottom+band]
        lo = Vector((min(p.x for p in base), min(p.y for p in base), bottom))
        hi = Vector((max(p.x for p in base), max(p.y for p in base), bottom))
        if len(base) < 3 or min(hi.x-lo.x, hi.y-lo.y) < 1e-5:
            raise ExportError('Tragende Basisflächen erlauben keinen eindeutigen Boden-Pivot.')
        return Vector(((lo.x+hi.x)/2, (lo.y+hi.y)/2, bottom))
    finally:
        evaluated.to_mesh_clear()


def footprint_pivot(obj, *, with_method=False, context=None):
    try:
        pivot = _input_pivot(obj)
        method = 'input_footprint'
    except ExportError:
        try:
            pivot = _support_pivot(obj, context)
            method = 'supporting_body_fallback'
        except Exception as exc:
            raise ExportError(f'Kein zuverlässiger Grundriss-/Boden-Pivot: {exc}') from exc
    return (pivot, method) if with_method else pivot


def mesh_counts(mesh):
    mesh.calc_loop_triangles()
    counts = Counter()
    for tri in mesh.loop_triangles:
        mat = mesh.materials[tri.material_index] if tri.material_index < len(mesh.materials) else None
        counts[mat.name if mat else '<none>'] += 1
    return counts


def owned_counts(context, obj):
    """Filter before collecting geometry; parent.original is GN occurrence ownership."""
    dg = context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(dg)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
    try:
        result = mesh_counts(mesh)
    finally:
        evaluated.to_mesh_clear()
    direct = sum(result.values())
    instances = 0
    cache = {}
    for inst in dg.object_instances:
        if not (inst.is_instance and inst.parent and inst.parent.original == obj and inst.show_self):
            continue
        if inst.object.type != 'MESH':
            raise ExportError('Nicht unterstützte Nicht-Mesh-Instanz am ausgewählten Haus.')
        key = inst.object.data.as_pointer()
        if key not in cache:
            cache[key] = mesh_counts(inst.object.data)
        result.update(cache[key])
        instances += 1
    return result, direct, instances


def realize_group():
    group = bpy.data.node_groups.new('MBG_TEMP_Realize', 'GeometryNodeTree')
    try:
        group.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        a = group.nodes.new('NodeGroupInput')
        b = group.nodes.new('GeometryNodeRealizeInstances')
        c = group.nodes.new('NodeGroupOutput')
        b.inputs['Realize All'].default_value = True
        group.links.new(a.outputs['Geometry'], b.inputs['Geometry'])
        group.links.new(b.outputs['Geometry'], c.inputs['Geometry'])
        return group
    except Exception:
        # The caller cannot clean up an ID that was not returned yet.
        bpy.data.node_groups.remove(group)
        raise


# Explicit, bounded approximation for the original IRCSS slots. Never edit source shaders.
PALETTE = {
    'GroundFloorWalls': (.40355, .30638, .21388, 1),
    'Stone': (.50878, .45853, .37517, 1),
    'WindowGlass': (.12, .23, .30, 1),
    'Greenery': (.075, .24, .035, 1),
    'GreenSta': (.10, .30, .055, 1),
    'Material': (.48, .19, .065, 1),  # small plant/decoration slots, not shader fidelity
}
FLOWERS = {'Material.001': (.85,.14,.045,1), 'Material.002': (.95,.48,.035,1),
           'Material.003': (.36,.065,.30,1), 'Material.005': (.68,.09,.12,1)}


def convert_materials(mesh, obj, created):
    mod = generator_modifier(obj)
    colors = {name: tuple(socket(mod, source).value) for name, source in
              [('Roof','RoofColor'), ('UpperFloorsPaint','PaintColor'), ('Beam','BeamCollor')]}
    policy = {}
    used_slots = {p.material_index for p in mesh.polygons}
    for index, original in enumerate(list(mesh.materials)):
        name = original.name if original else '<none>'
        # Appending can add numeric suffixes. Flower IDs themselves include a suffix.
        role = name
        if role not in FLOWERS:
            role = re.sub(r'\.\d{3}$', '', role)
            if role not in PALETTE and role not in colors and role not in FLOWERS:
                role = re.sub(r'\.\d{3}$', '', role)
        color = colors.get(role, FLOWERS.get(role, PALETTE.get(role, (.32,.20,.12,1))))
        known = role in colors or role in FLOWERS or role in PALETTE
        mat = bpy.data.materials.new('MBG_PBR_' + name)
        created.append(mat)
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = color
        shader.inputs['Roughness'].default_value = .88 if role == 'Roof' else .25 if role == 'WindowGlass' else .95
        shader.inputs['Metallic'].default_value = 0
        mat.diffuse_color = color
        mesh.materials[index] = mat
        policy[name] = dict(color=list(color), role=role, used=index in used_slots,
                            policy='house input' if role in colors else 'explicit approximation' if known else 'brown fallback')
    return policy


def export_house(context, obj, filepath, *, overwrite=False):
    """Transaction: freeze at source location, center frozen mesh, atomic GLB commit.

    Called only on execute, never while browsing/cancelling. No source file is saved.
    """
    if not valid_house(context, obj):
        raise ExportError('Bitte ein gültiges Medieval-Building-Generator-Haus aktiv auswählen (Object Mode).')
    path = Path(bpy.path.abspath(str(filepath))).expanduser().absolute()
    if path.suffix.lower() != '.glb' or not path.stem:
        raise ExportError('Bitte einen Dateinamen mit der Endung .glb wählen.')
    if not path.parent.is_dir():
        raise ExportError('Der Zielordner existiert nicht. Bitte einen vorhandenen Ordner wählen.')
    if path.exists() and not overwrite:
        raise ExportError('Zieldatei existiert bereits. Überschreiben im Dateidialog bestätigen.')
    if path.is_dir():
        raise ExportError('Der gewählte Zielpfad ist ein Ordner.')
    try:
        mod = validate(obj)
        if socket(mod, 'Object').value != obj:
            raise ExportError('Der Object-Eingang verweist nicht auf dieses Haus. Keine sichere Exportzuordnung.')
    except AssetError as exc:
        raise ExportError(str(exc)) from exc
    if not obj.visible_get(view_layer=context.view_layer):
        raise ExportError('Das aktive Haus ist in diesem View Layer nicht sichtbar.')
    pivot, pivot_method = footprint_pivot(obj, with_method=True, context=context)
    try:
        expected, direct, instance_count = owned_counts(context, obj)
        matrix = obj.evaluated_get(context.evaluated_depsgraph_get()).matrix_world.copy()
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(f'Geometry-Nodes-Auswertung fehlgeschlagen: {exc}') from exc
    if not expected:
        raise ExportError('Das ausgewählte Haus liefert keine exportierbare Geometrie.')
    if abs(matrix.determinant()) < 1e-12:
        raise ExportError('Haus besitzt eine singuläre Transformation (Skalierung null).')
    source_scene = context.window.scene
    source_layer = context.window.view_layer
    selected = list(context.selected_objects)
    active = source_layer.objects.active
    clone = input_mesh = group = mesh = export_obj = export_scene = None
    created_materials = []
    temporary = None
    try:
        clone = obj.copy()
        input_mesh = obj.data.copy()
        clone.data = input_mesh
        clone.name = 'MBG_TEMP_Evaluate'
        clone.animation_data_clear()
        clone.parent = None
        clone.constraints.clear()
        clone.matrix_world = matrix
        source_scene.collection.objects.link(clone)
        group = realize_group()
        wrapper = clone.modifiers.new('MBG_TEMP_Realize', 'NODES')
        wrapper.node_group = group
        # Keep Object input referencing original at its original world transform.
        context.view_layer.update()
        dg = context.evaluated_depsgraph_get()
        mesh = bpy.data.meshes.new_from_object(clone.evaluated_get(dg),
                                              preserve_all_data_layers=True, depsgraph=dg)
        actual = mesh_counts(mesh)
        if actual != expected:
            raise ExportError('Realisierung stimmt nicht mit den zugehörigen Haus-Instanzen überein; kein Export geschrieben.')
        bpy.data.objects.remove(clone, do_unlink=True)
        clone = None
        # Only frozen geometry is transformed. World placement is removed, but
        # source rotation/scale (including mirrored winding) remain baked in mesh.
        transform = matrix.copy()
        transform.translation -= matrix @ pivot
        mesh.transform(transform)
        if transform.determinant() < 0:
            mesh.flip_normals()
        mesh.update()
        policy = convert_materials(mesh, obj, created_materials)
        export_scene = bpy.data.scenes.new('MBG_TEMP_Export')
        export_obj = bpy.data.objects.new('MedievalBuilding', mesh)
        export_scene.collection.objects.link(export_obj)
        context.window.scene = export_scene
        export_obj.select_set(True)
        context.view_layer.objects.active = export_obj
        fd, temporary = tempfile.mkstemp(prefix='.mbg_', suffix='.glb', dir=str(path.parent))
        os.close(fd)
        result = bpy.ops.export_scene.gltf(
            filepath=temporary, export_format='GLB', use_selection=True, use_active_scene=True,
            export_animations=False, export_skins=False, export_cameras=False, export_lights=False,
            export_extras=False, export_yup=True, export_vertex_color='NONE')
        if result != {'FINISHED'}:
            raise ExportError('Blender hat den GLB-Export nicht abgeschlossen.')
        blob = Path(temporary).read_bytes()
        if blob[:4] != b'glTF':
            raise ExportError('Exporter lieferte keine gültige GLB-Datei.')
        length = struct.unpack_from('<I', blob, 12)[0]
        gltf = json.loads(blob[20:20+length])
        triangles = sum(gltf['accessors'][p['indices']]['count']//3
                        for m in gltf.get('meshes', []) for p in m['primitives'])
        if triangles != sum(expected.values()) or len(gltf.get('meshes', [])) != 1:
            raise ExportError('GLB-Geometrieprüfung fehlgeschlagen; Zieldatei bleibt unverändert.')
        if overwrite:
            os.replace(temporary, path)
        else:
            # Atomic no-clobber commit, even if another process creates the path.
            os.link(temporary, path)
            os.unlink(temporary)
        temporary = None
        return dict(path=str(path), bytes=len(blob), triangles=triangles,
                    direct_triangles=direct, owned_instances=instance_count,
                    material_triangles=dict(expected), pivot_local=list(pivot), pivot_method=pivot_method,
                    pivot_world=list(matrix @ pivot), material_policy=policy,
                    fallback_materials=[name for name, info in policy.items()
                                        if info['used'] and info['policy'] == 'brown fallback'])
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(f'Hausexport fehlgeschlagen: {exc}') from exc
    finally:
        context.window.scene = source_scene
        context.window.view_layer = source_layer
        if export_obj:
            bpy.data.objects.remove(export_obj, do_unlink=True)
        if clone:
            bpy.data.objects.remove(clone, do_unlink=True)
        if export_scene:
            bpy.data.scenes.remove(export_scene)
        for data in (mesh, input_mesh):
            if data is not None:
                bpy.data.meshes.remove(data)
        if group:
            bpy.data.node_groups.remove(group)
        for mat in created_materials:
            bpy.data.materials.remove(mat)
        for other in list(context.selected_objects):
            other.select_set(False)
        for other in selected:
            other.select_set(True)
        source_layer.objects.active = active
        if temporary and Path(temporary).exists():
            Path(temporary).unlink()
