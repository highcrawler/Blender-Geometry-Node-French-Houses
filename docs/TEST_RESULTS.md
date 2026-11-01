# Testresultate – Entwicklungsphase 1

## Status: **PARTIAL** (technischer Kern PASS, Darstellung noch nicht freigegeben)

- **PASS** Fork `highcrawler/Blender-Geometry-Node-French-Houses` vom IRCSS-Upstream, Quelle `b49b3c1dca15a57f3696e23c6f3ba8badf1fa6a3`; Branch `experiment/building-generator-audit`. Original-Lizenz/Urheberhinweise unangetastet.
- **PASS** Blender **5.2.2 LTS** lädt die Quelle, wertet drei `GenerateHouse`-Objekte aus, speichert drei editierbare Dateien, rendert drei PNG und exportiert drei GLB. Godot **4.7.stable.official** importiert HouseOne und instanziiert ein Mesh mit fünf Surfaces und 50.944 Dreiecken.
- **PARTIAL** Qualität: Workbench-Bilder belegen Formen, Fenster, Fachwerk und Dächer, **nicht** die tatsächliche Textur-/Shaderwiedergabe im Spiel. Die GLB enthält null Bilder/Texturen; keine Godot-GUI-Sichtprüfung und kein Kollisions-/LOD-Test. Gewählte Varianten nutzen bereits im Original vorhandene unterschiedliche Grundrisse/Proportionen statt neue Features zu implementieren.

## Drei Varianten (unveränderte vorhandene `GenerateHouse`-Objekte)

| Objekt | Grundrisspunkte | ungefähre Blender-Abmessungen (m) | Faces | Triangles | GLB | Bild |
|---|---:|---|---:|---:|---:|---|
| HouseOne | 4 | 3,928 × 6,485 × 8,150 | 20.003 | 50.944 | [HouseOne.glb](../tests/variants/HouseOne.glb) | [HouseOne.png](../tests/variants/HouseOne.png) |
| HouseTWo | 4 | 4,860 × 5,397 × 7,539 | 18.253 | 45.926 | [HouseTWo.glb](../tests/variants/HouseTWo.glb) | [HouseTWo.png](../tests/variants/HouseTWo.png) |
| HouseThree | 10 | 6,403 × 9,649 × 7,183 | 38.223 | 93.818 | [HouseThree.glb](../tests/variants/HouseThree.glb) | [HouseThree.png](../tests/variants/HouseThree.png) |

Die editierbaren `.blend` und JSON-Messdaten stehen unter `tests/variants/`. Bilder wurden nach direkter Betrachtung als erkennbare Fachwerkhäuser mit Gauben beurteilt; HouseThree ist deutlich größer, aber nicht extrem gestreckt (Grundriss-Seitenverhältnis etwa 1,51). Der gewollte Obergeschossüberhang und Schmuck/Pflanzen sind sichtbar; eine vollständige geometrische Durchdringungsprüfung existiert nicht. Es wurden keine neuen Dach-Topologien erzwungen.

### Leistung und Größen

Depsgraph-Auswertung nach Laden der Datei im selben Prozess: 0,005–0,011 s je Haus (Warmlaufzeit; **nicht** vollständige Initialisierungs-/Render-/GPU-Zeit). GLB: 3.797.324 / 4.277.728 / 8.141.508 Bytes für HouseTWo / HouseOne / HouseThree. Mesh ist für ein einzelnes Gebäude detailreich; Performance auf Spielzielhardware nicht gemessen. Drei Testszenen enthalten weiterhin Quelldaten und sind keine schlanken Lieferdateien.

### Wiederholen

```bash
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/inspect_blend.py
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/build_variants.py -- HouseOne
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/build_variants.py -- HouseTWo
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/build_variants.py -- HouseThree
cp tests/variants/HouseOne.glb godot-test/assets/HouseOne.glb
godot --headless --path godot-test --editor --import --quit
godot --headless --path godot-test --script res://scripts/validate_import.gd
```

Godot-Ausgabe: `GODOT_IMPORT meshes=1 surfaces=5 triangles=50944` (Exit 0). Zu den Grenzen des GLB-Exports siehe [EXPORT_PIPELINE.md](EXPORT_PIPELINE.md). Die Quelle ist unangetastet; `*.blend1` und `godot-test/.godot/` werden nicht versioniert.
