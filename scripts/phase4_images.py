"""Measured UV diagnostics and labeled contact sheets; standard Python + Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat
import json
out=Path('tests/baking/phase4')
r=json.loads((out/'source_audit.json').read_text())
summary={}
for name,polygons in [('original',r['uv']['UVMap']['polygons']),('bake',json.loads((out/'bake_uv.json').read_text()))]:
    image=Image.new('RGB',(1024,1024),'#161c25'); draw=ImageDraw.Draw(image)
    canonical=[tuple(sorted(tuple(round(c,7) for c in v) for v in p)) for p in polygons]
    areas=[abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2 for p in polygons]
    for p in polygons:
        xy=[(u*1023,(1-v)*1023) for u,v in p]
        draw.polygon(xy,outline='#7ed5dd')
    image.save(out/f'uv_{name}.png')
    summary[name]={'faces':len(polygons),'unique_uv_polygons':len(set(canonical)),'exact_duplicate_faces':len(polygons)-len(set(canonical)),'zero_area_faces':sum(a<1e-12 for a in areas),'total_uv_area':sum(areas),'min_face_area_pixels':min(areas)*1024**2,'max_face_area_pixels':max(areas)*1024**2}
(out/'uv_measurements.json').write_text(json.dumps(summary,indent=2))
comparisons={}
for view in ['iso','front','facade']:
    labels=['original','phase3','phase4']
    if (out/f'godot_pbr_{view}.png').exists(): labels.append('godot')
    sheet=Image.new('RGB',(960*len(labels),750),'#202020'); d=ImageDraw.Draw(sheet)
    for i,label in enumerate(labels):
        path=out/(f'godot_pbr_{view}.png' if label=='godot' else f'blender_{label}_{view}.png')
        sheet.paste(Image.open(path).convert('RGB'),(i*960,30)); d.text((i*960+10,9),label,fill='white')
    sheet.save(out/f'comparison_{view}.png')
print(summary)
