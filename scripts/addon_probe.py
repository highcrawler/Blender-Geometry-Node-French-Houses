"""Read-only inspection for the add-on MVP; run inside Blender."""
import bpy, json, hashlib
from pathlib import Path
root = Path.cwd()
bpy.ops.wm.open_mainfile(filepath=str(root / 'GeometryNodesFrenchHous.blend'))
o = bpy.data.objects['HouseOne']
m = next(m for m in o.modifiers if m.type == 'NODES')
report = {'version': bpy.app.version_string, 'source_sha256': hashlib.sha256((root/'GeometryNodesFrenchHous.blend').read_bytes()).hexdigest(), 'matrix': [list(row) for row in o.matrix_world], 'vertices': [list(v.co) for v in o.data.vertices], 'edges': [list(e.vertices) for e in o.data.edges], 'faces': [list(p.vertices) for p in o.data.polygons], 'modifiers': [(m.name,m.type) for m in o.modifiers], 'inputs': []}
for s in m.node_group.interface.items_tree:
    if s.item_type == 'SOCKET' and s.in_out == 'INPUT':
        entry = dict(name=s.name, identifier=s.identifier, type=s.socket_type)
        try:
            inp = getattr(m.properties.inputs, s.identifier)
            value = inp.value
            entry.update(value=list(value) if hasattr(value,'__len__') and not isinstance(value,str) else str(value) if isinstance(value,bpy.types.ID) else value, rna=[p.identifier for p in inp.bl_rna.properties])
        except Exception as e: entry['error']=str(e)
        report['inputs'].append(entry)
(root/'tests/addon/phase5/probe.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
