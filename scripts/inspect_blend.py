"""Read-only Blender data inventory; run: blender -b GeometryNodesFrenchHous.blend -P scripts/inspect_blend.py."""
import bpy
import json
from collections import Counter
from pathlib import Path

out = {'blender': bpy.app.version_string, 'objects': [], 'groups': [], 'images': [], 'materials': [], 'missing_files': []}
for obj in bpy.data.objects:
    mods = []
    for mod in obj.modifiers:
        if mod.type == 'NODES':
            try:
                properties = {k: str(mod[k])[:120] for k in mod.keys() if not k.startswith('_')}
            except TypeError:
                properties = {}
            mods.append({'name': mod.name, 'group': mod.node_group.name if mod.node_group else None,
                         'inputs': properties})
    if mods:
        out['objects'].append({'name': obj.name, 'type': obj.type, 'mesh_vertices': len(obj.data.vertices) if obj.type == 'MESH' else None,
                               'modifiers': mods, 'location': list(obj.location), 'dimensions': list(obj.dimensions)})
for group in bpy.data.node_groups:
    if group.bl_idname != 'GeometryNodeTree':
        continue
    nodes = list(group.nodes)
    inputs = [{'name': i.name, 'identifier': i.identifier, 'type': i.socket_type,
               'default': str(getattr(i, 'default_value', ''))[:100]} for i in group.interface.items_tree if i.item_type == 'SOCKET' and i.in_out == 'INPUT']
    out['groups'].append({'name': group.name, 'node_count': len(nodes), 'links': len(group.links), 'types': dict(Counter(n.bl_idname for n in nodes)),
                          'dependencies': sorted(set(n.node_tree.name for n in nodes if n.type == 'GROUP' and n.node_tree)), 'inputs': inputs})
for im in bpy.data.images:
    out['images'].append({'name': im.name, 'source': im.source, 'filepath': im.filepath, 'packed': bool(im.packed_file)})
    if im.source == 'FILE' and not im.packed_file and not im.has_data:
        out['missing_files'].append(im.name)
out['materials'] = [m.name for m in bpy.data.materials]
Path('docs').mkdir(exist_ok=True)
Path('docs/blender_inventory.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
print('INVENTORY', len(out['groups']), 'groups', len(out['objects']), 'GN objects', len(out['materials']), 'materials', 'missing', len(out['missing_files']))
