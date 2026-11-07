"""Compose screenshots captured separately in Blender and Godot; never fabricate a view."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parent;shots=P/'screenshots';tile=(640,360);bar=45
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
except OSError:font=ImageFont.load_default()

def compose(rows,path):
 cols=max(len(row) for row in rows)
 result=Image.new('RGB',(cols*tile[0],len(rows)*(tile[1]+bar)),'#21282b');draw=ImageDraw.Draw(result)
 for r,row in enumerate(rows):
  for c,(name,label) in enumerate(row):
   src=shots/(name+'.png');image=Image.open(src).convert('RGB');assert image.size==(1280,720),src
   x=c*tile[0];y=r*(tile[1]+bar);draw.text((x+8,y+9),label,font=font,fill='#f5f5ef');result.paste(image.resize(tile,Image.Resampling.LANCZOS),(x,y+bar))
 result.save(shots/path);print('MOD01_BOARD',shots/path)

compose([[('godot_A_'+view,'Godot 4.7 '+view+' | A – ART-01 B'),('godot_B_'+view,'Godot 4.7 '+view+' | B – modular')]
         for view in ('side','iso','detail','distance300')]+[
         [('A_side','Blender 5.2 | A – ART-01 B'),('B_side','Blender 5.2 | B – modular')],
         [('A_iso','Blender 5.2 | A – ART-01 B'),('B_iso','Blender 5.2 | B – modular')]],
         'comparison_board.png')
compose([[('single_plain','1 · Ein geschlossenes WALL_PLAIN'),('three_separate','2 · Drei getrennte WALL_PLAIN'),('shared_frame','3 · Rahmen ohne Füllung')],
         [('middle_removed','4 · Mittleres Gefach entfernt'),('middle_restored','5 · Gleiches Gefach wieder eingesetzt'),('B_side','6 · Zusammengesetzte Wand')]],
         'module_proof_board.png')
