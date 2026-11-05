"""Read-only inventory of select IRCSS node groups; source blend must never be saved."""
import bpy
from collections import Counter
for n in bpy.data.node_groups:
    if n.bl_idname != 'GeometryNodeTree':
        continue
    name = n.name.lower()
    if any(s in name for s in ('beam', 'wall', 'roof', 'house', 'curve', 'material', 'wood', 'plaster')):
        deps = sorted({v.node_tree.name for v in n.nodes if v.type == 'GROUP' and v.node_tree})
        print('COTTAGE_AUDIT', n.name, 'nodes', len(n.nodes), 'dependencies', deps, 'operations', dict(Counter(v.bl_idname for v in n.nodes).most_common(5)))
