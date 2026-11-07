# MOD-01 – Drei `WALL_PLAIN`-Module + gemeinsames ART-01-Fachwerk

Basis `6731e4c`, ausschließlich ein Checkout `ircss-fork`. `wall_plain.py` ist die kleine **Blender-unabhängige** Moduldefinition; `assemble.py` erzeugt eigene lokale Pivots/Clay-Meshes und einmalig die ART-01-Rahmenobjekte. `spike.py` liest Phase-9F-A-`.blend` nur als Blender-Background-Input, misst/prüft gegen ART-01-Audit und baut A (ART-01-B-Wand isoliert) sowie B (derselbe Rahmen plus 3 separat platzierbare Infill-Module), rendert und exportiert **nativ** mit `bpy.ops.export_scene.gltf(... export_format='GLB', use_selection=True, export_yup=True, export_apply=False)`. Keine neue Exportfunktion oder Generatorintegration. Vor/nach Blender-Quellhash muss identisch sein.

**Zustände:** `screenshots/single_plain.png` (geschlossenes Einzelmodul), `three_separate.png` (3 um 0/0,25/0,50 m gesprengte/geschlossene Instanzen), `shared_frame.png` (9 nur dem Rahmen gehörende Hölzer), `middle_removed.png`/`middle_restored.png` (zweite Instanz vorübergehend entfernt/wiederhergestellt, Rahmen-Fingerprint+Objekt-IDs gleich), `A_*.png`/`B_*.png` (montierte reale Blender-A/B-Ansichten); `godot_A_*.png`/`godot_B_*.png` (Godot 4.7). Die montierten internen Modul-Endkappen werden konfigurationsbedingt ausgelassen, sodass an Kontaktflächen keine doppelten koplanaren Putzfaces liegen. Ein Einzelmodul hat beide Endkappen. Einzelne montierte Module sind damit *an offenen Kontaktseiten* nicht vollständig geschlossen – siehe `docs/MOD01_MODULE_INTERFACE.md`.

Blender 5.2.2, Godot 4.7 stable, Python3/Pillow, grafische Anzeige (`DISPLAY`) für echte Godot-Captures:

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/mod01_modular_wall_poc
blender -b -X -Y -t 4 --python-exit-code 40 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$P/spike.py" > "$P/blender.log" 2>&1
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
for view in side iso detail distance300; do
  for v in A B; do
    if [ "$v" = A ]; then asset=mod01_A_art01_wall.glb; else asset=mod01_B_three_modules.glb; fi
    J_VIEW="$view" H_ASSET="$asset" H_SHOT="$PWD/$P/screenshots/godot_${v}_${view}.png" \
      godot --path "$P/godot_test" --rendering-driver opengl3 --resolution 1280x720 -s res://capture.gd >> "$P/godot_capture.log" 2>&1
  done
done
python "$P/make_board.py"
python "$P/surface_union.py"
python "$P/validate.py"
```

`godot_test/.godot/` enthält nur ignorierten regenerierbaren Cache. `assembly_audit.json` protokolliert 3 Pivot-/Anschluss-Verträge und unveränderten SharedFrame; `godot_audit.json` importierte Meshes, Materialslots, Weltbounds und 3 tatsächliche Godot-Pivots; `validation.json` vergleicht 9 Rahmenmeshes + das A-Putzmesh *unabhängig gegen das historische ART-01-B-GLB*, misst 8 echte A/B-Bilddifferenzen und prüft Kosten/Material. `surface_union.json` prüft die 28 Putz-Dreiecke auf doppelte Flächen sowie auf fehlende Kanten **nach gedanklichem Verschweißen gleichliegender Meshgrenzen**; die drei Meshdatablocks bleiben tatsächlich getrennt. [Vergleichstafel](screenshots/comparison_board.png) · [Baukastenbeweis](screenshots/module_proof_board.png). Kein Project-Pilgrimm-Projekt wurde berührt.
