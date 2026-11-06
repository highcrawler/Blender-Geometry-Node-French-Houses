"""Pair genuine Blender renders; identical pixel scaling in comparison A/B."""
from pathlib import Path
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent
views=('iso','front','side','roof_detail','gable_ridge','eave_end')
for state in ('clean','aged'):
    board=Image.new('RGB',(1020,2330),(38,39,40)); draw=ImageDraw.Draw(board)
    for row,view in enumerate(views):
        for col,name in enumerate(('long','compact')):
            image=Image.open(root/'screenshots'/f'{name}_{state}_{view}.png').convert('RGB')
            image=image.resize((480,360),Image.Resampling.LANCZOS)
            x=15+col*505;y=25+row*385
            board.paste(image,(x,y))
            draw.text((x,y-17),f'{name.upper()} / {state.upper()} / {view}',fill=(240,235,215))
    board.save(root/f'comparison_{state}_long_vs_compact.jpg',quality=93)
board=Image.new('RGB',(1020,790),(38,39,40));draw=ImageDraw.Draw(board)
for row,name in enumerate(('long','compact')):
    for col,state in enumerate(('clean','aged')):
        image=Image.open(root/'screenshots'/f'{name}_{state}_iso_300.png').convert('RGB')
        assert image.size==(480,360)
        x=15+col*505;y=25+row*390
        board.paste(image,(x,y))
        scale=11.5 if name=='long' else 8.25
        draw.text((x,y-17),f'{name.upper()} / {state.upper()} / ortho={scale} / native 480x360',fill=(240,235,215))
board.save(root/'comparison_all_four_300.jpg',quality=93)
