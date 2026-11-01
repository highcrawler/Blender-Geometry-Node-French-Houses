# Phase 2 – Materialaudit von HouseOne

**Umgebung:** Blender 5.2.2 LTS, Ausgangscommit `12cd98fd44fffbe948a457bd6e1de7528af1272a`, Branch `experiment/material-export-02`. Quelle `GeometryNodesFrenchHous.blend`, SHA-256 `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5`; weder Quelle noch Phase-1-`tests/variants/HouseOne.blend` wurden geändert. Messungen: [`tests/materials/measurements.json`](../tests/materials/measurements.json). Der anfängliche Prüfansatz `scripts/phase2_probe.py` las Blender-5.2-Modifikatorwerte fälschlich über IDProperties; tatsächliche Objektwerte stehen unter `modifier.properties.inputs.Socket_* .value` (ohne Leerzeichen vor `.value`). Die alte, unversionierte Prüfdatei blieb unangetastet und ist **keine** Messgrundlage.

## Tatsächliche Materialien und Shader

Das evaluierte HouseOne hat fünf belegte Materialien (zusätzlich zum unbelegten Slot 0 der ursprünglichen Szene). Die Materialnamen im GLB sind identisch. Jeder verwendete Material-Output läuft über eine Blender-Shader-Node-Gruppe und Principled BSDF; die Base-Color-Pfade sind nicht einfache konstante Principled-Farben:

| Material | Triangles BASELINE | Blender-Knoten / Quelle | GLB-Übertragbarkeit |
|---|---:|---|---|
| `Roof` | 7.256 | Noise, Map Range, Mix, `RoofColor`-Attribut, `TileRandom`, Shader-Gruppe | Form und Materialslot ja; prozedurale Dachfarbvariation nein |
| `GroundFloorWalls` | 20 | Zwei Shader-Gruppen, Normale und Farbverarbeitung | Geometrie ja; Gruppen-Shader nein |
| `UpperFloorsPaint` | 2.210 | Noise, Mix, triplanare Ziegel-Untergruppe, `PaintColor`, Normalenverarbeitung | Putz-/Ziegelmuster und Normaleneffekt nein |
| `Beam` | 4.718 | gerichteter Noise, `BeamDirection`, `BeamColor`, Shader-Gruppe | Holzfarb-/Maserungsverlauf nein |
| `Stone` | 36.740 | Noise, Map Range, RGB, Shader-Gruppe | prozedurale Steintonwerte nein |

Die Zählungen beziehen sich auf Dreiecke nach GN-Auswertung, nicht auf eigenständige Objektzahlen. Alle fünf Materials enthalten Noise direkt oder in Untergruppen; **keine der fünf tatsächlich verwendeten Material-Nodetrees einschließlich Untergruppen enthält eine Image Texture Node**. Das Quell-`.blend` enthält drei gepackte FILE-Bilder (`billboardgrass0001.png`, `LeafTexture`, `plantsTextureLowRes.png`) mit ursprünglichen absoluten Windows-Pfaden. Sie sind in dieser HouseOne-Materialkette nicht referenziert. Gepackt in der Datei bedeutet nicht benutzt oder im GLB eingebettet. Material- und Knotenbelege sind maschinenlesbar in `measurements.json`; das vorläufige `tests/materials/source_audit.json` enthält die Knoten-Links und Attribute, aber **nicht** verlässliche Objekt-Overrides (siehe oben).

GN-Mesh-Attribute: `RoofColor`, `PaintColor`, `BeamColor` (FLOAT_COLOR/POINT), `TileRandom` (FLOAT/POINT), `BeamDirection`, `LocalPosition`, `UVMap` u. a. Der HouseOne-Modifikator hat `Seed=29`, `NumberFloor=2`, `RoofCurvature≈1,66`, `RoofColor=(0,4792;0,0553;0,1106;1)`, `PaintColor=(1;1;1;1)`, `BeamCollor=(0,2706;0,2141;0,2204;1)`, `SpawnIVY=true`, `High Polz Plants=true`. **Wichtig:** Gruppendefault `SpawnIVY=false`, aber Objektwert **true**. Der Shader nutzt die Schreibweise `BeamColor`, die Schnittstelle heißt `BeamCollor` (Originalschreibweisen).

## Echte Blender-Ansichten

Cycles CPU, 16 Samples, Denoising, 960×720, ursprüngliche Shader- und GN-Attributwerte, neutrale World/Hauptlicht; keine künstlerisch neuen Gebäudematerialien. Kamera ortho: iso `(12,-15,12)→(0,0,3.7)`, front `(16,0,5.2)→(0,0,3.7)`, Fassade `(11,-5,4.8)→(0,-0.4,4.2)`; vertikale Ortho-Skalen 15/12/6. Eine *separate, nur für Export und Rendering gebackene* Meshkopie liegt nach XY-Zentrierung auf Z=0. Der GN-Generator bleibt gespeichert unverändert.

- [Gesamtansicht](../tests/materials/blender/baseline_iso.png)
- [Frontansicht](../tests/materials/blender/baseline_front.png)
- [Fassadendetail](../tests/materials/blender/baseline_facade.png)

Sichtbar: rot-rosa Ziegeldach, dunkle Balken/Tür, fleckiger weißer Obergeschossputz und unregelmäßiger Steinfuß. Die geometrischen Fenster-/Gaubenformen sind sichtbar; transparente Fensterverglasung lässt sich für dieses Exemplar **nicht** nachweisen, und eine hervortretende Pflanzenmasse ist in diesen Ansichten nicht erkennbar. Das ist keine Aussage über alle Assets des Generators. Frontansicht ist die lokale +X-Richtung, entsprechend dem Phase-1-README.

## Warum `images=0`?

Es fehlen **benutzte Bildtexturen**, nicht aber Blender-Materialslots oder GN-Attributdaten. Beide neu exportierten GLB enthalten fünf Materialeinträge und fünf Primitives, aber `images=0`, `textures=0`; alle glTF-PBR-Einträge enthalten nur `metallicFactor: 0` und weder `baseColorFactor` noch `baseColorTexture`. Die GLBs enthalten `COLOR_0`–`COLOR_3`, doch deren bloße Existenz reproduziert weder die Blender-Shaderverknüpfungen noch Noise/Triplanar/Normalen. Stichprobe `COLOR_0` ist weiß; weitere Farbkanäle tragen u. a. Balkenwerte. Deshalb keine pauschale Gleichsetzung von „ohne Bilder“ und „ohne Materialdaten“: **dieses konkrete GLB verliert jedoch den visuellen Blender-Farbpfad**. Der Phase-1-GLB hat dieselbe PBR-Materialstruktur und 50.944 Dreiecke. Keine Fehlermeldung des Exporters; ein technisch erfolgreicher Export mit vorhersehbarer Shader-Inkompatibilität, nicht ein nachgewiesener Dateifehler.

## Reproduktion

```bash
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/phase2_materials.py
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/phase2_toggle_probe.py
python3 scripts/validate_glb.py tests/materials/exports/BASELINE.glb tests/materials/exports/REDUCED.glb
```

Arbeitsverzeichnis ist zwingend die Repository-Wurzel. `scripts/phase2_materials.py` setzt zwei **Objekt-Modifikatorwerte nur im temporären Blender-Prozess**; die Quelldatei wird weder gespeichert noch überschrieben. Die Bilder/GLB werden beim bewussten erneuten Ausführen an denselben *Phase-2-Ausgabepfaden* aktualisiert; Phase-1-Dateien bleiben unberührt. `tests/materials/blender_run.log` dokumentiert den konkreten Durchlauf.
