"""Compare unchanged 9D reference RGB pixels against 9F Blender controls."""
import json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
root=Path(__file__).resolve().parent
old=root.parent/'wooden_roof_system_09d'/'screenshots'
results={}
for state in ('clean','aged'):
    board=Image.new('RGB',(1020,1560),(38,39,40));draw=ImageDraw.Draw(board)
    for row,key in enumerate(('long','compact','T03_short','T05_shallow')):
        filename=f'{key}_{state}_iso.png'
        before=Image.open(old/filename).convert('RGB')
        after=Image.open(root/'screenshots'/filename).convert('RGB')
        assert before.size==after.size==(800,600)
        diff=ImageChops.difference(before,after);stats=ImageStat.Stat(diff)
        results[key+'_'+state]=dict(rgb_pixels_equal=diff.getbbox() is None,
            mean_absolute_rgb_error=sum(stats.mean)/3,
            max_channel_difference=max(x[1] for x in stats.extrema),pixels=800*600)
        for col,(label,im) in enumerate((('9D',before),('9F',after))):
            x=15+505*col;y=25+385*row
            board.paste(im.resize((480,360),Image.Resampling.LANCZOS),(x,y))
            draw.text((x,y-17),f'{key} {state.upper()} / {label}',fill=(245,240,225))
    board.save(root/f'comparison_{state}.jpg',quality=93)
(root/'image_comparison.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(v['rgb_pixels_equal'] for v in results.values()),results
print('09F_IMAGES',len(results),'exact RGB matches')
