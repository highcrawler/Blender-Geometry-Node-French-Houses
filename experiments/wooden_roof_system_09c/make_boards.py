"""Contact sheets of existing Cycles renders; all isos share one ortho camera."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent
cases=list(json.loads((root/'config.json').read_text()))

def board(name,keys,view,columns,states=None):
    states=states or ['clean']*len(keys)
    rows=(len(keys)+columns-1)//columns
    result=Image.new('RGB',(columns*410+10,rows*325+15),(38,39,40))
    draw=ImageDraw.Draw(result)
    for i,(key,state) in enumerate(zip(keys,states)):
        im=Image.open(root/'screenshots'/f'{key}_{state}_{view}.png').convert('RGB')
        im=im.resize((400,300),Image.Resampling.LANCZOS)
        x=10+(i%columns)*410;y=22+(i//columns)*325
        result.paste(im,(x,y));draw.text((x,y-17),f'{key} / {state.upper()} / {view}',fill=(245,240,225))
    result.save(root/name,quality=93)

board('overview_six_iso.jpg',cases,'iso',3)
board('overview_six_front.jpg',cases,'front',3)
board('comparison_with_references.jpg',['long','compact',*cases],'iso',4)
# Failure-region detail board, native original crops scaled identically.
result=Image.new('RGB',(1020,650),(38,39,40));draw=ImageDraw.Draw(result)
for row,key in enumerate(('T03_short','T05_shallow')):
    for col,view in enumerate(('gable_ridge','eave_end')):
        im=Image.open(root/'screenshots'/f'{key}_clean_{view}.png').convert('RGB')
        im=im.resize((480,300),Image.Resampling.LANCZOS)
        x=15+col*505;y=22+row*320
        result.paste(im,(x,y));draw.text((x,y-16),f'{key} / CLEAN / {view}',fill=(245,240,225))
result.save(root/'failure_details.jpg',quality=93)
