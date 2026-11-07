# ART-01 – Isolierter Test einer einzigen Fachwerk-Seitenwand

Basis WOOD-01 `a8b9f6c` im **einzigen** Checkout `ircss-fork`; Branch `experiment/art01-medieval-timber-frame`. Nur die gespeicherte Phase-9F-A-Quelle wird eingelesen, **niemals gespeichert oder überschrieben**. `probe.py` misst wirkliche Koordinaten und Materialslots aus der `.blend`, `spike.py` dupliziert A-Root und alle 37 A-Meshdaten, erzeugt A/B auf privaten Collections, rendert reale Blender-Bilder und nutzt **Blenders nativen** `bpy.ops.export_scene.gltf` (GLB, `use_selection`, Y-up, kein `export_apply`) für beide. Baseline A muss SHA-256-identisch zum 9K-GLB sein. B verändert ausschließlich die positive-X-Seitenwand. Kein Generator-, Dach-, Exportcode-, Holztextur- oder Materialeingriff.

Erforderlich: Blender **5.2.2**, Godot **4.7 stable**, Python 3/Pillow, Grafik-`DISPLAY` für Godot-Screenshots. Keine neuen Worktrees, Clones, Benutzerdatei-Restores oder `.blend`-Saves. Nach einer Neuerzeugung von GLBs wird das Godot-Projekt **neu importiert**, dann neu auditiert und aufgenommen:

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/art01_medieval_timber_frame
SRC=experiments/wooden_roof_system_09f/three_owned_cottages.blend
blender -b -X -Y -t 4 --python-exit-code 40 "$SRC" -P "$P/probe.py" > "$P/probe.log" 2>&1
blender -b -X -Y -t 4 --python-exit-code 40 "$SRC" -P "$P/spike.py" > "$P/blender.log" 2>&1
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
for view in side iso detail distance300; do
  for v in A B; do
    if [ "$v" = A ]; then asset=art01_A_baseline.glb; else asset=art01_B_timber_frame.glb; fi
    J_VIEW="$view" H_ASSET="$asset" H_SHOT="$PWD/$P/screenshots/godot_${v}_${view}.png" \
      godot --path "$P/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$P/godot_capture.log" 2>&1
  done
done
python "$P/make_board.py"
python "$P/validate.py"
```

`godot_test/.godot/` ist ignorierter regenerierbarer Importcache. [`baseline_geometry.json`](baseline_geometry.json) bewahrt den lesenden Quellen-Audit, [`geometry_audit.json`](geometry_audit.json) die Kopie-Endpunkte/Änderungskosten, [`godot_audit.json`](godot_audit.json) die **tatsächlich importierten** Mesh-/Surface-/Material-/Weltbounds, [`validation.json`](validation.json) den unabhängigen A/B-GLB- und Anschlusstest. Die Tafel [`screenshots/comparison_board.png`](screenshots/comparison_board.png) wird aus den echten Screenshots neu erzeugt. Keine Änderungen am historischen 9K-GLB oder an gesicherten Benutzerdateien.
