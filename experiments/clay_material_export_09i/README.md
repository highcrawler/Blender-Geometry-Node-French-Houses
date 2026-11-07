# Phase 9I – one-material spike

Run from repo root with locally installed Blender 5.2.2, Godot 4.7, Python 3/Pillow and a graphical display (`DISPLAY` for Godot screenshots). No dependencies are installed. Source 9F three-owned-cottages blend is opened **read-only in a disposable Blender process**; script never saves it. All outputs stay here.

```bash
EXP=experiments/clay_material_export_09i
blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$EXP/spike.py" > "$EXP/blender.log" 2>&1
python "$EXP/compare.py"
godot --headless --editor --path "$EXP/godot_test" --quit > "$EXP/godot_import.log" 2>&1
H_REPORT="$PWD/$EXP/godot_audit.json" godot --headless --path "$EXP/godot_test" -s res://audit.gd > "$EXP/godot_audit.log" 2>&1
python "$EXP/validate.py"
for pair in 'baseline_A.glb baseline_godot.png' 'clay_constant_A.glb constant_godot.png'; do
  set -- $pair
  H_ASSET="$1" H_SHOT="$PWD/$EXP/screenshots/$2" godot --path "$EXP/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$EXP/godot_capture.log" 2>&1
done
python - <<'PY'
from PIL import Image,ImageDraw
from pathlib import Path
p=Path('experiments/clay_material_export_09i/screenshots'); names=['blender_original.png','baseline_godot.png','constant_godot.png','blender_clay_detail.png']
board=Image.new('RGB',(1280,1600),(28,30,34)); d=ImageDraw.Draw(board)
for i,n in enumerate(names):
 im=Image.open(p/n).convert('RGB'); im.thumbnail((710,375)); board.paste(im,(290,i*400+20)); d.text((16,i*400+20),n,fill='white')
board.save(p/'comparison_board.png')
PY
```

`baseline_A.glb` is a byte-identical copy of 9H `cottage_A.glb`, SHA-256 `fb6dbfa3f3fd053f59c1e36520335ba40c0365c5a32b42556b5258540ac1104b`. `spike.py` is purpose-built for Clay A, not a conversion pipeline. `compare.py` reads native GLB payloads for **audit only**, not serialization. `.godot/` import cache and local logs can be regenerated. The four Markdown reports in `docs/` contain interpretation and limits.
