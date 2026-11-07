# ART-WOOD-02 – isolierter Hauptbalken unter hartem Art-Gate

Nur `ART01_MidRail` der MOD-02-B-Fensterwand, Basis `048dee8`. A ist **byteidentischer** nativer MOD-02-B-GLB; B/C entstehen auf isolierter Kopie des Balkens und derselben wegwerfbaren Wand. Keiner der historischen Skripte, `.blend`-Dateien, Module, Generatoren oder Dächer wurde verändert. Drei Zustände, keine zusätzlichen Gebäudemodule.

`make_textures.py` erzeugt deterministisch mit Python/Pillow einen warmen Holz-Atlas und eine aus der Höhenmaske abgeleitete Normalmap (1024×512, keine Fremdbilder); **kein Blender-Bake nötig**, denn die prozedural rasterisierten Bilder sind unmittelbar glTF-kompatibel. `timber_surface.py` wendet Bevel/Displace auf der Objektkopie an, erzeugt UVs entlang lokaler Balken-Z und verknüpft Color (sRGB) und Normal (Non-Color) über einen Normal-Map-Node. Alle drei GLBs über den nativen Blender-Export. Godot 4.7 importiert A/B/C einschließlich Texturen.

Reproduktion: Blender 5.2.2, Godot 4.7, Python3 mit Pillow und ein grafisches Display für Godot-Screenshots.

```bash
cd /home/alexander-both/Dokumente/Generation/ircss-fork
P=experiments/art_wood_02
python "$P/make_textures.py"
blender -b -X -Y -t 4 --python-exit-code 40 experiments/wooden_roof_system_09f/three_owned_cottages.blend -P "$P/spike.py" > "$P/blender.log" 2>&1
godot --headless --editor --path "$P/godot_test" --quit > "$P/godot_import.log" 2>&1
H_REPORT="$PWD/$P/godot_audit.json" godot --headless --path "$P/godot_test" -s res://audit.gd > "$P/godot_audit.log" 2>&1
godot --headless --path "$P/godot_test" --quit-after 5 > "$P/godot_smoke.log" 2>&1
bash "$P/capture.sh"
python "$P/validate.py"
```

[Blender/Godot-Vergleich](screenshots/comparison_board.png) · [GLB-/Blender-Audit](assembly_audit.json) · [Godot-Import](godot_audit.json) · [Textur-Rezept](texture_audit.json) · [unabhängiger PASS der technischen Prüfungen](validation.json). **Dieser technische PASS ist ausdrücklich kein Bestehen des künstlerischen Gates.**
