"""Check that the geometric union of 3 separate infill meshes has no holes/duplicate faces."""
import json
from collections import Counter
from pathlib import Path
from wall_plain import WallPlain
P=Path(__file__).resolve().parent
s=json.loads((P/'assembly_audit.json').read_text())
wall=s['wall_measurement'];definition=WallPlain(wall['height'],wall['thickness'])
edges=Counter();triangles=Counter();summaries=[]
for inst in s['instances']:
 verts,faces=definition.geometry(inst['width_m'],inst['assembled_cap_left'],inst['assembled_cap_right'])
 x,left,bottom=inst['world_mount']
 global_verts=[tuple(round(q,5) for q in (x+n,left+u,bottom+v)) for u,v,n in verts]
 for face in faces:
  for tri_idx in ((0,1,2),(0,2,3)):
   tri=tuple(global_verts[face[k]] for k in tri_idx)
   triangles[tuple(sorted(tri))]+=1
   for j in range(3):edges[tuple(sorted((tri[j],tri[(j+1)%3])))]+=1
 summaries.append({'id':inst['id'],'triangles':len(faces)*2,'world_range_y':[round(left,5),round(left+inst['width_m'],5)]})
counts=Counter(edges.values())
assert len(triangles)==28 and all(n==1 for n in triangles.values())
assert set(counts)=={2},('unmatched or duplicate union edges',counts)
assert summaries[0]['world_range_y'][1]==summaries[1]['world_range_y'][0]
assert summaries[1]['world_range_y'][1]==summaries[2]['world_range_y'][0]
assert summaries[0]['world_range_y'][0]==round(wall['y_edges'][0],5)
assert summaries[2]['world_range_y'][1]==round(wall['y_edges'][-1],5)
report={'result':'PASS','definition':'three separate meshes, union evaluated after coincident-vertex welding conceptually; mesh datablocks remain separate',
        'faces_triangles':28,'unique_triangles':len(triangles),'edge_multiplicities':dict(counts),'nonmanifold_or_open_union_edges':0,
        'duplicate_coplanar_triangles':0,'modules':summaries,'mesh_datablocks_welded':False}
(P/'surface_union.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOD01_SURFACE_UNION_PASS',report['faces_triangles'],len(edges))
