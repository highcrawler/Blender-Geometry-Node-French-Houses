# ART-BEAM-01 – ein isolierter Knieverband

**Ausgangsbasis `048dee8` (MOD-02).** Hier werden ausschließlich Kopien des linken `ART01_KneeBrace_1` und der isolierten MOD-02-Seitenwand betrachtet. Kein Eingriff in `.blend`, ART-01, MOD-02, Generator, Dach oder Exportbibliothek. A ist eine byteidentische Kopie des historischen MOD-02-B-GLB. B/C entstehen aus Wegwerfkopien derselben Geometrie; nur das Ziel-Mesh ändert sich. C verwendet nach einem lokalen Cycles-Bake zwei 512²-PNGs. Das Godot-Testprojekt enthält allein dieses Experiment.

Reproduktion mit Blender 5.2.2, Godot 4.7, Python/Pillow und laufender grafischer Anzeige für Screenshots:

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/art_beam_01
blender -b -X -Y -t 4 --python-exit-code 40 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$P/spike.py" > "$P/blender.log" 2>&1
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
godot --headless --path "$P/godot_test" --quit-after 5 > "$P/godot_smoke.log" 2>&1
bash "$P/capture.sh"
python "$P/validate.py"
```

[Vergleichstafel](screenshots/comparison_board.png) · [Blender-Audit](assembly_audit.json) · [Godot-Audit](godot_audit.json) · [unabhängige Prüfung](validation.json). `godot_test/.godot` ist ignorierter Importcache. Keine Gebäudebibliothek/Shader-Pipeline wurde gebaut.
