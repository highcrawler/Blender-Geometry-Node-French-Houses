# Phase 7 – Godot-Validierung

Godot **4.7 stable**, OpenGL-Compatibility-Renderer. Blender 5.2.2 erzeugte mit der installierten Extension 0.3.0 drei eigenständige GLBs über den Phase-6-Exporter. Die unveränderten exportierten Dateien `compact.glb`, `narrow.glb`, `wide.glb` werden in `godot-test/assets/MBG_Phase7_*.glb` eingebunden. Die Godot-Quelle ist ein lokaler Prüfbereich, kein externes Projekt.

Reproduktion: Godot-Editorimport im Projekt `godot-test`, danach die Szene [`addon_variety07.tscn`](../godot-test/scenes/addon_variety07.tscn) öffnen. Das ausführbare Mess- und Bildskript [`addon_variety07_capture.gd`](../godot-test/scripts/addon_variety07_capture.gd) lädt die Szene und wertet importierte Meshes, Dreiecke, Materialflächen, Fußbodenvertices und Weltpositionen aus. Prüfwerte: [`godot_measurements.json`](../tests/addon/phase7/godot_measurements.json), Blender-Referenz [`integration.json`](../tests/addon/phase7/integration.json). Laufprotokoll: [`godot_capture.log`](../tests/addon/phase7/godot_capture.log).

| Instanz | Bodenbreite Z | Bodentiefe X | Höhe über Boden | Dreiecke | Materialien |
|---|---:|---:|---:|---:|---:|
| Compact | 4,0 m | 3,2 m | 8,054 m | 86.975 | 12 |
| Narrow | 3,2 m | 5,0 m | 8,377 m | 90.875 | 12 |
| Wide | 7,0 m | 4,0 m | 7,889 m | 181.248 | 12 |

Blender-Y wird nach glTF/Godot-Z, Blender-X nach Godot-X, Z-Höhe nach Godot-Y abgebildet. Die vier **Bodenvertices** des `GroundFloorWalls`-Materials liegen je bei Y=0; ihre X/Z-Mitte ist `(0,0)` mit Abweichung unter 0,0001. Die AABB aller Wände ist als Fußabdruck ungeeignet, denn obere Mauerdetails und Überhänge sind mit enthalten – daher überprüft das Skript ausdrücklich die Bodenvertices. Je Haus exakt ein importiertes Mesh mit zwölf Materialflächen; alle Flächen haben eine PBR-Materialzuordnung und keine externe Albedo-Texturabhängigkeit. Die Dreieckszahlen entsprechen den unabhängigen Blender-GLB-Prüfungen. Die drei Meshwurzeln beginnen mit Scale `(1,1,1)`, ohne internen Transformationsoffset; ihre Positionen sind `(0,0,0)`, `(0,0,11)`, `(0,0,24)`.

Die Szene zeigt separate Häuser auf derselben Testfläche: [Dreieransicht](../tests/addon/phase7/godot_three_presets.png) und [Frontansicht](../tests/addon/phase7/godot_three_fronts.png). In einem dritten echten Frame wird nur die Narrow-Instanz nach `(3,0,10)` bewegt; Compact und Wide behalten ihre Wurzelpositionen: [Narrow unabhängig versetzt](../tests/addon/phase7/godot_narrow_moved.png). Die importierten PBR-Farben von Dach, Putz, Balken, Stein, Fenster und Grün sind im Screenshot sichtbar. Ein sichtbarer Boden und orange Kreuzmarkierungen zeigen den Nullpunkt der Grundflächen; diese Markierungen und Label gehören **nur zur Testszene**, nicht zu den GLBs.

**Ergebnis: PASS für die drei konkreten, getesteten GLBs** (Sichtprüfung, Proportionen, Boden-Pivot, Materialvollständigkeit und Einzelpositionierung). Keine Freigabe für beliebige Formen, Performancegrenzen oder alternative Renderer; die geerbten Nullflächen des Originalgenerators werden separat im [Audit](PHASE7_FOOTPRINT_AUDIT.md) offengelegt.
