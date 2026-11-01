"""Aligned evidence boards and bounded image metrics (Pillow only)."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat,ImageFilter
import json,hashlib
out=Path('tests/baking/phase4b');metrics={}
def board(files,labels,path):
 canvas=Image.new('RGB',(640*len(files),504),(28,28,28));draw=ImageDraw.Draw(canvas)
 for i,(file,label) in enumerate(zip(files,labels)):
  image=Image.open(out/file).convert('RGBA');background=Image.new('RGBA',image.size,(28,28,28,255));background.alpha_composite(image);canvas.paste(background.convert('RGB'),(i*640,24));draw.text((i*640+8,6),label,fill='white')
 canvas.save(out/path)
for view in ('iso','front','side','facade'):
 board([f'shader_original_{view}.png',f'shader_phase4_{view}.png',f'shader_corrected_{view}.png'],['A: actual original GN','B: Phase4 mesh / original shaders','C: realized + fixed texspace / original shaders'],f'geometry_{view}.png')
 board([f'shader_original_{view}.png',f'bake4_{view}.png',f'bake4b_corrected_{view}.png'],['Actual original GN / all procedural','Phase4 GLB / baked plaster','Phase4B / baked plaster + full geometry'],f'comparison_{view}.png')
 board([f'godot_phase4_{view}.png',f'godot_phase4b_{view}.png'],['Godot: Phase4','Godot: Phase4B'],f'godot_comparison_{view}.png')
 a=Image.open(out/f'silhouette_original_{view}.png').convert('RGBA');b=Image.open(out/f'silhouette_realized_{view}.png').convert('RGBA');p=Image.open(out/f'silhouette_phase4_{view}.png').convert('RGBA')
 diff=ImageChops.difference(a,b);alpha_a=list(a.getchannel('A').point(lambda v:255 if v>127 else 0).getdata());alpha_p=list(p.getchannel('A').point(lambda v:255 if v>127 else 0).getdata());union=sum(bool(x or y) for x,y in zip(alpha_a,alpha_p));intersection=sum(bool(x and y) for x,y in zip(alpha_a,alpha_p))
 overlay=Image.new('RGB',a.size);overlay.putdata([(180,180,180) if x and y else (255,40,180) if x else (40,180,255) if y else (20,20,20) for x,y in zip(alpha_a,alpha_p)]);overlay.save(out/f'silhouette_delta_{view}.png')
 metrics[view]=dict(original_realized_rgba_mae=ImageStat.Stat(diff).mean,original_realized_identical=a.tobytes()==b.tobytes(),phase4_silhouette_iou=intersection/union,phase4_missing_silhouette_pixels=sum(bool(x and not y) for x,y in zip(alpha_a,alpha_p)))
mask=Image.open(out/'plaster_mask_facade.png').convert('L');visible=[x>127 for x in mask.getdata()]
def damage(path):
 rgb=list(Image.open(out/path).convert('RGB').getdata());return [yes and rr-bb>7 and rr-gg>1 for yes,(rr,gg,bb) in zip(visible,rgb)]
a=damage('shader_original_facade.png')
for name in ('bake4_facade.png','bake4b_corrected_facade.png','shader_corrected_facade.png'):
 b=damage(name);union=sum(x or y for x,y in zip(a,b));intersection=sum(x and y for x,y in zip(a,b));metrics[name]=dict(heuristic_warm_brick_mask_iou=intersection/union,reference_pixels=sum(a),test_pixels=sum(b),note='lit RGB heuristic, not ground truth segmentation; R-B>7 and R-G>1/255 within eroded visible plaster')
 overlay=Image.new('RGB',mask.size);overlay.putdata([(200,200,200) if x and y else (255,30,180) if x else (40,180,255) if y else (20,20,20) for x,y in zip(a,b)]);overlay.save(out/('damage_delta_'+name))
a=json.loads((out/'repeat_reference.json').read_text());b=json.loads((out/'bake_measurements.json').read_text());metrics['independent_process_repeat']=dict(png_identical=a['png_sha256_runs']==b['png_sha256_runs'],glb_identical=a['glb_sha256']==b['glb_sha256'])
(out/'image_metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2))
