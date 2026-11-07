# WOOD-01: Medieval Weathered Beam Material Test

**Isolierter Vergleich**, kein neues Materialsystem. Ausgangsbasis `a4a59f3`; nur der einzelne Checkout `ircss-fork`. Die 9F-Quelldatei wird als Blender-Background-Input geladen, nie gespeichert. Alle Änderungen passieren auf einzeln kopierten A-Meshes und Wegwerfmaterialien; keine Generator-/Dach-/Exportdateien geändert.

A: byteidentisches Phase-9K-A-GLB, Weathered Oak konstant; B: Poly Haven [Rough Wood](https://polyhaven.com/a/rough_wood), 1K Diffuse JPEG, Normal (GL) PNG und Rough JPEG (CC0, Rob Tuytel); C: einfacher Blender-Wave→Ramp→Emission-*Bake* auf 512²-PNG, dann per nativer glTF-Schnittstelle exportiert. B/C ändern nur 16 echte Fachwerkbalken (192 Dreiecke); die sechs Türteile bleiben konstante Oak, Clay/Stone/Door und das CLEAN-Dach bleiben unverändert. Die Quell-BMP-/PNG-/JPEG-Dateien stehen unter `textures/`, inklusive [API-Antwort](textures/polyhaven_files_api.json), [Asset-Info](textures/polyhaven_asset_info.json). Alle B/C-Texturen sind in GLB eingebettet. C ist ein **Farb-Bake**, kein Normal/Roughness-Bake.

Blender 5.2.2, Godot 4.7 stable, Python 3/Pillow sowie `DISPLAY` für Godot-Aufnahmen:

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/wood_beam_material_01
blender -b -X -Y -t 4 --python-exit-code 40 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$P/spike.py" > "$P/blender.log" 2>&1
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
for view in detail distance300; do
  for v in A B C; do
    case "$v" in A) asset=beam_A_baseline.glb;; B) asset=beam_B_roughwood.glb;; C) asset=beam_C_procedural.glb;; esac
    J_VIEW="$view" H_ASSET="$asset" H_SHOT="$PWD/$P/screenshots/godot_${v}_${view}.png" \
      godot --path "$P/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$P/godot_capture.log" 2>&1
  done
done
python "$P/validate.py"
python "$P/make_board.py"
```

`validate.py` liest die echten GLB-Triangle-Daten unabhängig vom Godot-Import, lässt durch UV-Nähte hinzugefügte Vertexduplikate zu und prüft Positionen, Dreieckzuordnung, Materialzuordnung und Welttransforms gegenüber A, plus Godots importierte Textur- und Materialparameter. Der Test-Screenshot ist unter [screenshots/comparison_board.png](screenshots/comparison_board.png). Keine Änderung am Baseline-GLB; originale gesicherte Benutzerdateien nicht restauriert.
