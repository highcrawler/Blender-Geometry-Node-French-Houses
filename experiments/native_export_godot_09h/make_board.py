"""Arrange only real Godot captures; no Blender rendering or color manipulation."""
from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).resolve().parent/'screenshots'
board=Image.new('RGB',(1280,768),'#20252a')
draw=ImageDraw.Draw(board)
for i,(name,label) in enumerate((('long_clean_glb','Long CLEAN • native GLB'),
                                  ('long_clean_blend','Long CLEAN • direct .blend'),
                                  ('compact_aged_glb','Compact AGED • native GLB'),
                                  ('compact_aged_blend','Compact AGED • direct .blend'))):
    x=(i%2)*640;y=(i//2)*384
    image=Image.open(p/(name+'.png')).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
    board.paste(image,(x,y+24));draw.text((x+12,y+6),label,fill='white')
board.save(p/'comparison_board.png')
