"""Convex UV polygon overlap test (HouseOne evaluated quads)."""
import json, math
from pathlib import Path
out=Path('tests/baking/phase4')
def area(p): return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2 if p else 0
def cross(a,b,p): return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def intersect(poly,clip):
    result=poly
    if area(clip)<0: clip=list(reversed(clip))
    for a,b in zip(clip,clip[1:]+clip[:1]):
        points=result; result=[]
        if not points: break
        prev=points[-1]; dprev=cross(a,b,prev)
        for cur in points:
            dcur=cross(a,b,cur)
            if (dcur>=0)!=(dprev>=0):
                t=dprev/(dprev-dcur)
                result.append([prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])])
            if dcur>=0: result.append(cur)
            prev=cur; dprev=dcur
    return abs(area(result))
result={}
for name,polys in [('original',json.loads((out/'source_audit.json').read_text())['uv']['UVMap']['polygons']),('bake',json.loads((out/'bake_uv.json').read_text()))]:
    boxes=[(min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)) for p in polys]
    count=0; total=0; convex=True
    for p in polys:
        signs=[cross(p[i-2],p[i-1],p[i]) for i in range(len(p))]
        convex &= not(any(s>1e-9 for s in signs) and any(s< -1e-9 for s in signs))
    assert convex
    for i,p in enumerate(polys):
        a=boxes[i]
        for j in range(i):
            b=boxes[j]
            if min(a[2],b[2])<=max(a[0],b[0])+1e-10 or min(a[3],b[3])<=max(a[1],b[1])+1e-10: continue
            overlap=intersect(p,polys[j])
            if overlap>1e-10: count+=1; total+=overlap
    result[name]={'overlapping_face_pairs':count,'summed_pairwise_overlap_uv_area':total,'all_polygons_convex':convex}
(out/'uv_overlap.json').write_text(json.dumps(result,indent=2)); print(result)
polys=json.loads((out/'bake_uv.json').read_text())
parent=list(range(len(polys)))
def find(i):
    while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
    return i
edges={}
for i,p in enumerate(polys):
    for a,b in zip(p,p[1:]+p[:1]):
        key=tuple(sorted((tuple(round(c,6) for c in a),tuple(round(c,6) for c in b))))
        edges.setdefault(key,[]).append(i)
for faces in edges.values():
    for i in faces[1:]: parent[find(i)]=find(faces[0])
boundary=[(a,b,find(faces[0])) for (a,b),faces in edges.items() if len(faces)==1]
def pdist(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1]; length=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length)) if length else 0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
gap=1
for i,(a,b,group) in enumerate(boundary):
    for c,d,other in boundary[:i]:
        if group==other: continue
        if max(min(a[0],b[0])-max(c[0],d[0]),min(c[0],d[0])-max(a[0],b[0]),min(a[1],b[1])-max(c[1],d[1]),min(c[1],d[1])-max(a[1],b[1]))>=gap: continue
        gap=min(gap,pdist(a,c,d),pdist(b,c,d),pdist(c,a,b),pdist(d,a,b))
verts=json.loads((out/'source_audit.json').read_text())['plaster_vertices']
distortions=[]
for p,v in zip(polys,verts):
    ratios=[math.dist(a,b)/math.dist(c,d) for a,b,c,d in zip(p,p[1:]+p[:1],v,v[1:]+v[:1]) if math.dist(c,d)>1e-9]
    distortions.append(max(ratios)/min(ratios))
result['bake'].update({'uv_islands_by_shared_edges':len(set(find(i) for i in range(len(polys)))),'minimum_island_gap_pixels':gap*1024,'edge_scale_anisotropy_max':max(distortions),'edge_scale_anisotropy_median':sorted(distortions)[len(distortions)//2]})
(out/'uv_overlap.json').write_text(json.dumps(result,indent=2));print(result['bake'])
