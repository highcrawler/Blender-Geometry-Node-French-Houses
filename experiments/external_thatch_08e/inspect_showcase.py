"""Read-only inventory of a user-supplied showcase; never saves or exports it.

blender -b "$SHOWCASE_BLEND" -t 4 -P experiments/external_thatch_08e/inspect_showcase.py
"""
import bpy
import hashlib
import json
from pathlib import Path

source = Path(bpy.data.filepath)
assert source.is_file() and source.read_bytes()[:7] == b'BLENDER'
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
groups = [g for g in bpy.data.node_groups if g.bl_idname == 'GeometryNodeTree']
mods = [m for o in bpy.data.objects for m in o.modifiers if m.type == 'NODES']
items = []
for o in meshes:
    items.append(dict(name=o.name, vertices=len(o.data.vertices),
                      polygons=len(o.data.polygons),
                      static_triangles=sum(len(f.vertices)-2 for f in o.data.polygons),
                      modifiers=[m.type for m in o.modifiers],
                      materials=[m.name for m in o.data.materials if m]))
images = []
for i in bpy.data.images:
    images.append(dict(name=i.name, source=i.source, resolution=list(i.size),
                       packed=bool(i.packed_file),
                       external_path_exists=bool(i.filepath and Path(bpy.path.abspath(i.filepath)).is_file())))
result = dict(product='3D Tudor - Blender 4 Hay Roof Geometry Node - Example Showcase',
              blender=bpy.app.version_string,
              file_blender_version=list(bpy.data.version),
              file_size_bytes=source.stat().st_size,
              file_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              geometry_node_groups=len(groups),
              node_group_names=[g.name for g in groups],
              geometry_nodes_modifiers=len(mods),
              meshes=items,
              material_names=[m.name for m in bpy.data.materials],
              images=images,
              linked_libraries=[l.filepath for l in bpy.data.libraries],
              text_block_names=[t.name for t in bpy.data.texts])
out = Path(__file__).resolve().parent/'inspection.json'
out.write_text(json.dumps(result, indent=2)+'\n')
print('08E_INSPECTION_COMPLETE', 'GN groups:', len(groups),
      'GN modifiers:', len(mods), 'meshes:', len(meshes), flush=True)
