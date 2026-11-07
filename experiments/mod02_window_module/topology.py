"""Pure-Python checks for the actual hole, reveal normals and assembled surface union."""
from collections import Counter
from pathlib import Path
import json,math,sys
P=Path(__file__).resolve().parent;R=P.parents[1]
sys.path.insert(0,str(P))
from wall_plain import WallPlain
from wall_window import WallWindow
old=json.loads((R/'experiments/mod01_modular_wall_poc/assembly_audit.json').read_text())
art=json.loads((R/'experiments/art01_medieval_timber_frame/geometry_audit.json').read_text())
w=old['wall_measurement'];edges_y=w['y_edges'];height=w['height'];thick=w['thickness']
rail_world=next(item['endpoints_world'][0][2] for item in art['new_members'] if item['name']=='ART01_MidRail')
bottom_world=rail_world+.12/2+.13
window=WallWindow(height,thick,bottom_world-w['bottom']);plain=WallPlain(height,thick)
width=edges_y[2]-edges_y[1];l,r,b,t=window.opening(width)
assert abs(width-2.4333334)<1e-5 and bottom_world>rail_world+.12/2
assert w['bottom']+t<art['measured_wall']['plate_top_center']-.13

def area_contains(tri,u,v):
 (ax,ay),(bx,by),(cx,cy)=tri
 det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
 if abs(det)<1e-10:return False
 alpha=((by-cy)*(u-cx)+(cx-bx)*(v-cy))/det
 beta=((cy-ay)*(u-cx)+(ax-cx)*(v-cy))/det
 gamma=1-alpha-beta
 return min(alpha,beta,gamma)>1e-7

wv,wf=window.geometry(width,True,True)
def oriented_component(face,axis):
 a,c,d=[wv[i] for i in face[:3]]
 p=[c[k]-a[k] for k in range(3)];q=[d[k]-a[k] for k in range(3)]
 return (p[1]*q[2]-p[2]*q[1],p[2]*q[0]-p[0]*q[2],p[0]*q[1]-p[1]*q[0])[axis]
# The last four quads are the left/right/bottom/top tunnel lining.
for face,axis,sign in zip(wf[-4:],(0,0,1,1),(1,-1,1,-1)):
 assert oriented_component(face,axis)*sign>1e-8,('wrong reveal normal',face)
for item in window.member_specs(width):
 a,c=item['a'],item['b'];half=item['thickness']/2
 # Check no frame timber crosses the clear center ray or contacts shared rail/plate.
 assert not (min(a[0],c[0])-half < (l+r)/2 < max(a[0],c[0])+half and
             min(a[1],c[1])-half < (b+t)/2 < max(a[1],c[1])+half)
 assert min(a[1],c[1])-half + w['bottom'] > rail_world+.06
 assert max(a[1],c[1])+half + w['bottom'] < art['measured_wall']['plate_top_center']-.065
# Every wood face at the reveal is inset 3 mm into the aperture, so it
# cannot be coplanar with a plaster reveal face (u=l/r or v=b/t).
specs={s['role']:s for s in window.member_specs(width)}
assert abs(specs['left_jamb']['a'][0]+.075/2-l-.003)<1e-7
assert abs(r-(specs['right_jamb']['a'][0]-.075/2)-.003)<1e-7
assert abs(t-(specs['head']['a'][1]-.09/2)-.003)<1e-7
assert abs(specs['sill']['a'][1]+.10/2-b-.003)<1e-7
for depth in (-thick/2,thick/2):
 front=[face for face in wf if len(face)==3 and all(abs(wv[i][2]-depth)<1e-9 for i in face)]
 assert len(front)==8
 assert not any(area_contains([(wv[i][0],wv[i][1]) for i in face],(l+r)/2,(b+t)/2) for face in front)
 assert any(area_contains([(wv[i][0],wv[i][1]) for i in face],l/2,(b+t)/2) for face in front)
 for face in front:
  p,q,z=[wv[i] for i in face]
  cross=(q[0]-p[0])*(z[1]-p[1])-(q[1]-p[1])*(z[0]-p[0])
  assert cross*(1 if depth>0 else -1)>1e-9,('incorrect front/back winding',face)

# The ring is sealed by four separate inner reveal quads; the *hole* is a tunnel,
# not an open mesh edge. Outer caps are included only at the two external bays.
def topology(instances):
 edges=Counter();tris=Counter();mesh_stats=[]
 for i,(definition,cap_l,cap_r) in enumerate(instances):
  width=edges_y[i+1]-edges_y[i];vertices,faces=definition.geometry(width,cap_l,cap_r)
  world=[tuple(round(q,5) for q in (w['x_center']+n,edges_y[i]+u,w['bottom']+v)) for u,v,n in vertices]
  for f in faces:
   for ids in ((f[0],f[1],f[2]),) if len(f)==3 else ((f[0],f[1],f[2]),(f[0],f[2],f[3])):
    tri=tuple(world[j] for j in ids);tris[tuple(sorted(tri))]+=1
    for k in range(3):edges[tuple(sorted((tri[k],tri[(k+1)%3])))]+=1
  mesh_stats.append({'type':'WALL_WINDOW' if isinstance(definition,WallWindow) else 'WALL_PLAIN','triangles':sum(len(f)-2 for f in faces)})
 return edges,tris,mesh_stats

all_edges,triangles,stats=topology([(plain,True,False),(window,False,False),(plain,False,True)])
assert [x['triangles'] for x in stats]==[10,28,10]
assert len(triangles)==48 and all(count==1 for count in triangles.values())
assert set(all_edges.values())=={2},Counter(all_edges.values())
# Evaluate standalone window mesh separately (no neighboring modules).
stand=Counter();sv,sf=window.geometry(width,True,True)
for f in sf:
 for ids in ((f[0],f[1],f[2]),) if len(f)==3 else ((f[0],f[1],f[2]),(f[0],f[2],f[3])):
  for k in range(3):stand[tuple(sorted((ids[k],ids[(k+1)%3])))]+=1
assert sum(len(f)-2 for f in sf)==32 and set(stand.values())=={2},Counter(stand.values())
report={'result':'PASS','source_window_width_m':r-l,'source_window_height_m':t-b,'local_opening':[l,r,b,t],
        'world_opening':{'x_through':[w['x_min'],w['x_max']],'y_left_right':[edges_y[1]+l,edges_y[1]+r],
                         'z_bottom_top':[w['bottom']+b,w['bottom']+t]},
        'opening_center_ray_hits_front_back_plaster':0,'independent_reveal_quads':4,'front_back_and_reveal_winding_correct':True,
        'wood_inset_into_aperture_m':.003,'wood_clear_of_shared_rail_and_plate':True,
        'assembled_plaster_triangles':len(triangles),'assembled_edge_multiplicities':dict(Counter(all_edges.values())),
        'duplicate_assembled_triangles':0,'open_assembled_edges':0,
        'standalone_window_plaster_triangles':32,'standalone_edge_multiplicities':dict(Counter(stand.values())),
        'module_counts':stats,'mesh_datablocks_welded':False}
(P/'topology.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOD02_TOPOLOGY_PASS',report['world_opening'],len(triangles),len(all_edges))
