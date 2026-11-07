# Phase 9J – reproduzierbarer Einzelmaterialtest

Ab Repository-Wurzel; lokal vorhandene Programme: Blender 5.2.2, Godot 4.7, Python 3 mit Pillow; eine laufende grafische Sitzung/`DISPLAY` für die realen Godot-Screenshots. Nichts installieren. `spike.py` öffnet nur die 9F-Dreihäuser-Referenz und **speichert nie die Quelle**. 9I-GLB liegt als notwendiger A/B-Importfall **byteidentisch** unter `godot_test/assets/clay_reference_A.glb` (nur eine Datei, keine Kopie des historischen Projekts). Alle anderen Dateien hier sind Testartefakte.

```bash
EXP=experiments/weathered_oak_export_09j
blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$EXP/spike.py" > "$EXP/blender.log" 2>&1
python "$EXP/compare.py"  # nur lesender GLB-Geometrie-/Materialvergleich, kein GLB-Writer
godot --headless --editor --path "$EXP/godot_test" --quit > "$EXP/godot_import.log" 2>&1
H_REPORT="$PWD/$EXP/godot_audit.json" godot --headless --path "$EXP/godot_test" -s res://audit.gd > "$EXP/godot_audit.log" 2>&1
python "$EXP/validate.py"
for view in normal distance300 detail; do
  for variant in reference candidate; do
    if [ "$variant" = reference ]; then asset=clay_reference_A.glb; else asset=oak_constant_A.glb; fi
    J_VIEW="$view" H_ASSET="$asset" H_SHOT="$PWD/$EXP/screenshots/${variant}_${view}.png" \
      godot --path "$EXP/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$EXP/godot_capture.log" 2>&1
done; done
python "$EXP/make_board.py"
```

Der **9I-GLB-Hash** muss `bec98bcb935eda5ff720061679326d5678eb291c802fbae08b46c44dfabba622` sein; historischer 9F-Blend-Hash `38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae`. `validate.py` prüft beide bei jedem Lauf. `.godot/`-Cache ist regenerierbar und nicht versioniert. Die vier `docs/PHASE9J_*.md` erläutern Messwerte und visuelle Grenzen; nur Clay und Weathered Oak sind im Kandidaten exportkompatibel, Stone und Door bleiben absichtlich unverändert.
