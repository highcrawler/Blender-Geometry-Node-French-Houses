# MOD-02 – ein austauschbares `WALL_WINDOW` im mittleren ART-01-Gefach

Basis `5311696`, Branch `experiment/mod02-window-module`. Alle Eingaben sind unverändert: Phase-9F-Quelldatei, MOD-01, ART-01, Hausgenerator, Dach und Project Pilgrimm. Der Assembler/die Module sind lokale **Kopien** von MOD-01 und eine kleine Fenstererweiterung; keine produktive Integration. `wall_window.py` definiert Blender-unabhängig Geometrie, Parameter, separate Holzteil-Spezifikationen und denselben Montagevertrag wie `wall_plain.py`. `assemble.py` erzeugt je Instanz einen eigenen Pivot und separate Meshobjekte für Clay, zwei Pfosten, oberes Holz und Fensterbank. Neun Hölzer gehören ausschließlich `MOD02_SharedFrame`.

**A:** Byteidentische Kopie des nativen, bereits exportierten MOD-01-GLB mit drei `WALL_PLAIN`-Instanzen; die A-Bilder wurden in Blender mit demselben Rahmen und denselben drei Definitionen erneut gerendert. **B:** identischer gemeinsamer Rahmen, `WALL_WINDOW` statt mittlerem `WALL_PLAIN`; nativ aus Blender exportiert. **C:** separates, mit *beiden* Endkappen geschlossenes `WALL_WINDOW` samt lokalem Pivot und allen vier eigenen Holzobjekten; ebenfalls nativer Blender-GLB. Alle GLBs importiert Godot 4.7. `spike.py` prüft Austausch Fenster → geschlossene Füllung und ein Blender-Bild davon; es verändert nie die Quelldatei. Bestandsmaterialien `09I_A_clay_constant` und `09J_A_weathered_oak_constant`; keine Texturen, kein Glas.

**Reproduktion (Blender 5.2.2, Godot 4.7, Python 3/Pillow, grafische Anzeige für Godot-Bilder):**

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/mod02_window_module
python "$P/topology.py"
blender -b -X -Y -t 4 --python-exit-code 40 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$P/spike.py" > "$P/blender.log" 2>&1
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
godot --headless --path "$P/godot_test" --quit-after 5 > "$P/godot_smoke.log" 2>&1
bash "$P/capture.sh"
python "$P/validate.py"
```

`godot_test/.godot/` ist nur ignorierter Cache. Die Putzvolumenprüfung `topology.json` zeigt 48 Dreiecke und 72 je doppelt belegte Kanten des *gedanklich vereinten* Wandvolumens; `validation.json` enthält GLB-Payload-Vergleich, Godot-Import, Pixelvergleich und Material-/Meshkosten. Das hintere Fenster ist sichtbar offen: `godot_audit.json` misst an echten importierten Mesh-Dreiecken **2→0→0** Wandflächentreffer entlang der Fenstermittelachse für A/B/C und **2** Treffer außerhalb der Öffnung in allen Zuständen. Die einzelnen Module sind tatsächliche getrennte Meshdatablocks (nicht miteinander verschweißt). [Vergleichstafel](screenshots/comparison_board.png) · [Einzelteile und Rückwechsel](screenshots/module_proof_board.png).
