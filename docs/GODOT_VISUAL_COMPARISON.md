# Phase 2 – Blender/Godot-Sichtvergleich

**Befund: FAIL (Materialtreue).** Godot **4.7.stable.official.5b4e0cb0f** importiert HouseOne in einem unabhängigen Projekt erfolgreich (ein Mesh, fünf Surfaces, 50.944 Triangles), aber die **tatsächlichen** OpenGL-3-Renderings zeigen ein fast einfarbig weißes Gebäude. Das ist ein visueller Test, nicht nur ein `--headless --import`-Test. Siehe [Materialaudit](MATERIAL_AUDIT.md).

| Eigenschaft | Blender, originale Cycles-Materialien | Godot, importiertes GLB |
|---|---|---|
| Dachmaterial | rosa/rot, sichtbare Kachel- und Farbvariation | weiß, nur Ziegelsilhouette |
| Holzbalken | dunkelbraun, fein variiert | weiß |
| Wandmaterial | weißgrau, fleckiger Putz und Ziegel darunter | weiß ohne Putzmuster |
| Fenster/Gauben | Gauben-/Öffnungsgeometrie sichtbar, Verglasung nicht nachgewiesen | gleiche Silhouette, kein differenzierter Fensterfarbton |
| Steinflächen | grau-beige, wechselnde Steine | weiß, Steingeometrie erhalten |
| Pflanzen | trotz `SpawnIVY=true` keine deutlich hervorstehende Pflanze in diesen Perspektiven | keine deutlich erkennbar; aus Bild nicht beurteilbar |
| Gesamteindruck | als stilisiertes Haus erkennbar, Materialvariation ausgeprägt | geometrisch intakt, Materialidentität unbrauchbar |

### Direkte Bildbelege

| Ansicht | Einzelbilder | Seite an Seite |
|---|---|---|
| Iso | [Blender](../tests/materials/blender/baseline_iso.png) · [Godot](../tests/materials/godot/baseline_iso.png) | [Vergleich](../tests/materials/blender_vs_godot_iso.png) |
| Front | [Blender](../tests/materials/blender/baseline_front.png) · [Godot](../tests/materials/godot/baseline_front.png) | [Vergleich](../tests/materials/blender_vs_godot_front.png) |
| Fassade | [Blender](../tests/materials/blender/baseline_facade.png) · [Godot](../tests/materials/godot/baseline_facade.png) | [Vergleich](../tests/materials/blender_vs_godot_facade.png) |

Die Screenshots sind 960×720 und stammen aus dem echten Godot-Viewport; kein Workbench- oder Headless-Dummy-Bild. Die Szene [`godot-test/scenes/material_comparison.tscn`](../godot-test/scenes/material_comparison.tscn) hält GLB, `Camera3D`, `DirectionalLight3D` und `WorldEnvironment`; [`godot-test/scripts/material_capture.gd`](../godot-test/scripts/material_capture.gd) setzt Kamera und speichert Bilder nach mehreren Frames und `RenderingServer.frame_post_draw`. Der GLB-Hausknoten bleibt bei Identitätstransformation und Originalmaßstab (Bauhöhe 8,150 m). Beim zweiten Durchlauf wird ausschließlich das GLB unter gleicher Szene/Kamera ausgetauscht. Blender-Kamerakoordinaten werden achsenrichtig konvertiert: `(x,y,z) → (x,z,-y)`; Ausrichtung und Ortho-Skalen 15/12/6 entsprechen der Blender-Szene. Für Beleuchtung wurde ein möglichst neutraler Godot-DirectionalLight plus Umgebungslicht statt der Blender-Area-Light/World-Kombination gewählt. Blender verwendet AgX und Cycles, Godot GL Compatibility andere Tonemapping-/Lichtmodelle; **geringe** Farbabweichungen wären darum erwartbar, ein überall weißes Haus ist damit nicht erklärbar.

### Reproduktion (Repository-Wurzel; vorhandene Dateien erhalten)

```bash
# Nach Blender-Export: separate Dateien, Phase-1-HouseOne.glb bleibt unverändert.
cp tests/materials/exports/BASELINE.glb godot-test/assets/HouseOne_Phase2_BASELINE.glb
cp tests/materials/exports/REDUCED.glb godot-test/assets/HouseOne_Phase2_REDUCED.glb
godot --headless --path godot-test --editor --import --quit
godot --headless --path godot-test --script res://scripts/validate_import.gd
# Bildschirmserver nötig: hier DISPLAY=:0, WAYLAND_DISPLAY=wayland-0; OpenGL-3-Renderer.
# NICHT --headless: headless Import beweist keine visuelle Wiedergabe.
godot --path godot-test --rendering-driver opengl3 --script res://scripts/material_capture.gd -- --output "$PWD/tests/materials/godot"
python3 scripts/phase2_compare.py  # benötigt Pillow (auf der Testmaschine installiert)
```

`scripts/material_capture.gd` beendet mit Exit 0 und meldete für **beide** Varianten `meshes=1 surfaces=5`, Dreiecke 50.944/50.764 sowie sechs gespeicherte Screenshots. Die tatsächlichen Protokolle stehen in `tests/materials/godot_import.log`, `tests/materials/godot_validation.log`, `tests/materials/godot_capture.log`. Godot-`.import`-Metadaten wurden im Testprojekt erzeugt; Importcache `.godot/` bleibt ignoriert. Ohne grafischen Bildschirmserver müsste die Methode mit externem X-Server/Offscreen-OpenGL erneut erprobt werden; auf **dieser** Maschine war ein echter GUI-Render möglich.
