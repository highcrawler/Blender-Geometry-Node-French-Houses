# Phase 2 – kontrollierte Detailreduktion

**Nur zwei exportierte Vergleichsvarianten:** `BASELINE` (unveränderte HouseOne-Objektwerte) und `REDUCED` (gleicher Grundriss, Seed, Stockwerke, Dach und Farben; bestehende `SpawnIVY`- und `High Polz Plants`-Modifikatoreingänge auf `false`). Beide Meshes aus demselben Blender-Ladevorgang; keine Änderungen an `GenerateHouse`, keine Speicherung der geänderten Quelldatei. Details und exakte Parameter: [`tests/materials/measurements.json`](../tests/materials/measurements.json), [`scripts/phase2_materials.py`](../scripts/phase2_materials.py). Blender 5.2.2 LTS, Godot 4.7.

| Metrik | BASELINE | REDUCED | Differenz |
|---|---:|---:|---:|
| Vertices (evaluiertes Blender-Mesh) | 27.919 | 27.827 | −92 (−0,330 %) |
| Faces | 20.003 | 19.927 | −76 (−0,380 %) |
| Triangles | 50.944 | 50.764 | **−180 (−0,3533 %)** |
| belegte Materialien | 5 | 5 | 0 |
| GLB-Größe (Bytes) | 4.277.724 | 4.263.356 | **−14.368 (−0,3359 %)** |
| Blender-Exportdauer, ein Warmdurchlauf | 0,389 s | 0,233 s | nicht als Benchmark vergleichbar |
| Godot-Import/Instanzierung | PASS: 1 Mesh / 5 Surfaces / 50.944 Triangles | PASS: 1 Mesh / 5 Surfaces / 50.764 Triangles | visuelle Materialien beider FAIL |

Phase-1-HouseOne: 27.919 Vertices, 20.003 Faces, 50.944 Triangles, 4.277.728 Bytes, 1 Mesh/5 Surfaces/0 Bilder. Der neu generierte BASELINE-GLB ist **4 Bytes kürzer**, weil der Exportobjektname `HouseOne_BASELINE` statt `HouseOne_GameReady` lautet; **nicht** eine behauptete Geometrieeinsparung. Bounds bei beiden: 3,928×6,485×8,150 m, lokal zentriert und auf Bodenhöhe; Exportkopie mit Identitätstransformation. Jede GLB wurde mit `scripts/validate_glb.py` geprüft. GLB-Dateien liegen unter `tests/materials/exports/`, die separat importierten Kopien unter `godot-test/assets/` (Phase-1-Dateien unangetastet).

## Wirkung der vorhandenen Pflanzen-Eingänge

Der **Objektwert**, nicht der Gruppendefault, beträgt `SpawnIVY=true`, `High Polz Plants=true`. Nur im Blender-Arbeitsspeicher ausgeführte Kontrollauswertung ohne Speichern mit [`scripts/phase2_toggle_probe.py`](../scripts/phase2_toggle_probe.py), keine weiteren Varianten exportiert:

| SpawnIVY | High Polz Plants | Vertices | Faces | Triangles |
|---|---|---:|---:|---:|
| true | true | 27.919 | 20.003 | 50.944 |
| true | false | 27.827 | 19.927 | 50.764 |
| false | true | 27.919 | 20.003 | 50.944 |
| false | false | 27.827 | 19.927 | 50.764 |

`SpawnIVY` hat in **diesem konkreten HouseOne-Zustand** keine messbare Geometriewirkung; `High Polz Plants=false` spart 180 Triangles, alle unter Materialslot `Stone`. Aus Materialslot-Zählungen allein lässt sich die geometrische Herkunft dieser 180 Dreiecke **nicht sicher einer Pflanze** zuordnen. Beispielsweise könnte ein Pflanzen-/Steindetail denselben Slot verwenden. Keine allgemeine Prozentbehauptung für alle Seeds/Häuser. `Roof` bleibt 7.256 und `Stone` sinkt von 36.740 auf 36.560 Triangles; große Dachziegel-/Steingeometrie wird durch die beiden Pflanzenregler nicht adressiert.

## Sichtbare Qualität und Grenzen

| Ansicht | Blender-Vergleich | Godot-Vergleich |
|---|---|---|
| Iso | [BASELINE/REDUCED](../tests/materials/baseline_vs_reduced_blender_iso.png) | [BASELINE/REDUCED](../tests/materials/baseline_vs_reduced_godot_iso.png) |
| Front | [BASELINE/REDUCED](../tests/materials/baseline_vs_reduced_blender_front.png) | [BASELINE/REDUCED](../tests/materials/baseline_vs_reduced_godot_front.png) |
| Fassade | [BASELINE/REDUCED](../tests/materials/baseline_vs_reduced_blender_facade.png) | [BASELINE/REDUCED](../tests/materials/baseline_vs_reduced_godot_facade.png) |

Für alle drei festen Blender-Kameras sind die PNGs der beiden Varianten **pixelidentisch** (`Pillow ImageChops.difference(...).getbbox() is None`); auch die Godot-Vergleichsbilder sind pixelidentisch. Das stützt „keine sichtbare Änderung in diesen Ansichten“, **nicht** „überall unsichtbar“. Die Materialwiedergabe in Godot bleibt für beide Varianten weiß und ist deshalb ungeeignet, feine farbige Unterschiede auszuschließen. Weder FPS noch GPU-Zeit/Memory gemessen. Die zwei Exportzeiten enthalten unterschiedliche Warmup-/Cache-Zustände und sind **keine** Leistungsbehauptung.

## Weitere vorhandene Regler / Vorschläge (nicht ausgeführt)

`NumberFloor`, `RoofCurvature`, `RoofGeometryType`, Dachüberhang-Eingänge und Seed beeinflussen teils Silhouette/Stockwerke; für diese kontrollierte Messung **nicht** verändert. Es gibt in der geprüften `GenerateHouse`-Schnittstelle keinen sicheren separaten Regler zum Entfernen einzelner Dachziegel, Fensterdetails oder rein dekorativer Steinbauteile bei gleicher Dachform. Ein Eingriff in den Original-GN-Graphen wurde bewusst nicht vorgenommen. Für Phase 3: Dachziegel- und Steindetails getrennt parametrieren, erst danach mehrere Seeds/Grundrisse und visuelle QA; ggf. LOD-Stufen auf Zielhardware testen. Daten zeigen hier **nur 0,35 %**, keinen überzeugenden generellen Detailhebel.

## Reproduktion

```bash
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/phase2_materials.py
blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/phase2_toggle_probe.py
python3 scripts/validate_glb.py tests/materials/exports/BASELINE.glb tests/materials/exports/REDUCED.glb
# Für Godot-Import und Screenshots siehe docs/GODOT_VISUAL_COMPARISON.md.
```

Die Werte in `tests/materials/toggle_probe.log` und `measurements.json` sind Messdaten **dieses** Laufs. Ein erneuter Blender-/Godot-Lauf soll die Zahlen und Ansichten bestätigen; Exportzeiten dürfen abweichen.
