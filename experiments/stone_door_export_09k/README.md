# Phase 9K – Stone/Door auf isolierter Exportkopie

Einziger aktiver Checkout: `/home/alexander-both/Dokumente/Generation/ircss-fork`; keine Worktrees/Clones. Basis `14ff3f6`. In 9K ist `AGENTS.md` die **byteidentische**, gezielt übernommene Single-Checkout-Policy, nicht ein Merge. Lokale Altdateien aus dem vorherigen schmutzigen Checkout liegen verifiziert unter `/home/alexander-both/MBG-workspace-consolidation-backup-20261107T120434Z/pre-9k-checkout-recovery/`; siehe dort `README.md`, `manifest.json`, `release_result.json`. Nie Dateien aus der Sicherung blind in einen anderen Branch zurückkopieren.

Blender 5.2.2 LTS, Godot 4.7 stable, Python 3/Pillow und grafische Anzeige/`DISPLAY` für Godot-Captures; keine Neuinstallation. Original-9F-Blend **nur** in disposable Blender-Prozess mit `-X -Y` öffnen, niemals speichern. Long CLEAN A allein, 37 Meshes/14.054 Dreiecke. Die 9J-GLB-Referenz ist byteidentisch als `godot_test/assets/oak_reference_A.glb` kopiert. Nur Stone/Door sind neue Exportmaterialien.

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/stone_door_export_09k
blender -b -X -Y -t 4 --python-exit-code 40 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$P/spike.py" > "$P/blender.log" 2>&1
python "$P/compare.py"  # lesender GLB-Payload-Vergleich; KEIN eigener GLB-Writer
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
python "$P/validate.py"
for view in normal distance300 detail; do
  for variant in reference candidate; do
    if [ "$variant" = reference ]; then asset=oak_reference_A.glb; else asset=stone_door_constant_A.glb; fi
    J_VIEW="$view" H_ASSET="$asset" H_SHOT="$PWD/$P/screenshots/${variant}_${view}.png" \
      godot --path "$P/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$P/godot_capture.log" 2>&1
done; done
python "$P/make_board.py"
```

`godot_test/.godot/` ist regenerierbarer Cache und ignoriert. `validate.py` vergleicht Stone-/Door-Albedo sRGB-korrekt, Quellen-Hash und byteidentische 9J-GLB-Referenz sowie die importierten Materialwerte; `compare.py` vergleicht GLB-Positions-/Indexdaten und Surface-IDs. Die historischen 9F–9J-Szenen und Materialien bleiben unberührt. Die vier Dokumente `docs/PHASE9K_*.md` enthalten Interpretation und Grenzen.
