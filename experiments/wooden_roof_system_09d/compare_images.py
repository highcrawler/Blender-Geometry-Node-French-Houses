"""Compare 9D Cycles control PNGs to unchanged 9C archives at RGB pixel level."""
import json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
root=Path(__file__).resolve().parent
old=root.parent/'wooden_roof_system_09c'/'screenshots'
new=root/'screenshots'
cases=('long','compact','T03_short','T05_shallow')
results={}
for state in ('clean','aged'):
    board=Image.new('RGB',(1020,1560),(38,39,40));draw=ImageDraw.Draw(board)
    for row,key in enumerate(cases):
        filename=f'{key}_{state}_iso.png'
        before=Image.open(old/filename).convert('RGB')
        after=Image.open(new/filename).convert('RGB')
        assert before.size==after.size==(800,600)
        diff=ImageChops.difference(before,after)
        stats=ImageStat.Stat(diff)
        mae=sum(stats.mean)/3
        max_delta=max(bound[1] for bound in stats.extrema)
        identical=diff.getbbox() is None
        results[key+'_'+state]=dict(rgb_pixels_equal=identical,mean_absolute_rgb_error=mae,
                                   max_channel_difference=max_delta,pixels=800*600)
        for col,(label,image) in enumerate((('9C archive',before),('9D corrected',after))):
            x=15+col*505;y=25+row*385
            board.paste(image.resize((480,360),Image.Resampling.LANCZOS),(x,y))
            draw.text((x,y-17),f'{key} {state.upper()} / {label}',fill=(245,240,225))
    board.save(root/f'comparison_{state}.jpg',quality=93)
(root/'image_comparison.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(x['rgb_pixels_equal'] for x in results.values()),results
print('9D_IMAGE_COMPARISON',len(results),'pixel-identical RGB render pairs')
