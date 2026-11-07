# ART-01 – Isolierter Tragwerks-/Geometrietest

Blender-Skript [`spike.py`](../experiments/art01_medieval_timber_frame/spike.py) öffnet die Phase-9F-Quelle **lesend** als Background-Prozess, dupliziert A-Root und alle 37 A-Meshdaten privat und arbeitet nur in einer wieder entfernten Collection. A wird mit dem nativen 9K-GLB-Verfahren **neu** exportiert; SHA-256 des neu erzeugten A-GLB ist **byteidentisch** zur Phase-9K-Referenz (`98330454442deb60dac54e2e19b02e5571b090fb27989e12e86d882b30ce5f05`). Kein eigener GLB-Writer, keine `.blend`-Speicherung, keine Änderung von Cottage-, Dach- oder bisherigem Exportcode. [Messwerte und geplante Endpunkte](../experiments/art01_medieval_timber_frame/geometry_audit.json) · [unabhängige GLB-/Godot-Assertions](../experiments/art01_medieval_timber_frame/validation.json).

| Bauteil auf **X-positiver** Wand | Lage aus Quellgeometrie abgeleitet | Funktion | Änderung |
|---|---|---|---:|
| Vorhandene SideWallPlate `.001` | Zentrum X **2,55 → 2,615**, Y ±3,65, Z 2,30; 0,13 m | sichtbar gewordene obere Lastverteilung zum Dach/Eckpfosten | verschoben, 0 Dreiecke |
| Zwei alte lange Endstreben `.002/.003` | Y nahe ±3,15, Z ~0,8…2,2 | kreuzen durchgehenden Mittelriegel und stehen ohne Zwischenpfosten | **entfernt −24 Dreiecke** |
| `ART01_SideSill` | X 2,615, Y −3,65…3,65, Z 0,315; **0,15 m** | untere Schwelle/Sockelkontakt, Lastweg nach unten | +12 |
| `ART01_MidRail` | X **2,607** (8 mm hinter Pfostenvorderkante), Y −3,65…3,65, Z **1,1725**; **0,12 m** | verbindender Mittelriegel/Unterteilung der Putzfelder | +12 |
| Zwei `ART01_IntermediatePost` | X 2,615, Y **−1,2167 / +1,2167**, Z 0,315…2,30; **0,12 m** | Lastweg obere Platte→Schwelle, drei Gefache | +24 |
| Zwei `ART01_KneeBrace` | an neuen Pfosten ab Z 1,3725 zu oberer Platte bei Z 2,275, Y bis ca. **±2,0927**; **0,09 m** | obere Aussteifung zweier äußerer Felder, Mittelgefache offen | +24 |

**Anschlüsse:** neue Schwelle beginnt bei Z **0,24** (gemessene Steinoberkante); Pfosten überlappen die Schwelle und die vorhandene obere Platte; Mittelriegel kreuzt/bindet die Pfosten. Je kurzer Knieverband überlappt seinen Pfosten sowie die obere Platte, beginnt aber >8 cm oberhalb des Mittelriegels: **keine Kreuzung mit Riegel**. Der Riegel sitzt um 8 mm hinter der Pfostenfront, damit am sichtbaren Kreuzungspunkt keine koplanaren Frontflächen/Z-Fighting entstehen. Neue Holzrückseiten gehen für den vereinfachten Anschluss **in die bestehende massive Putzbox hinein**, durchstoßen aber nicht deren Innenfläche; **kein konstruktives Boolean-/Zapfenmodell**. Die sechs neuen Quader mit je 12 Dreiecken lassen verdeckte Kontaktflächen stehen; dies ist bewusst redundante Geometrie und vor einer Produktionsintegration zu überprüfen. Die Eckanschlüsse der über die ganze Seitenlänge laufenden Schwelle/Platte werden nur als Quaderüberdeckung simuliert, nicht verzapft. Die ursprünglichen Eckpfosten/Giebel-/Türteile werden nicht verschoben.

| Messgröße | A | B | Änderung |
|---|---:|---:|---:|
| Meshobjekte | 37 | **41** | +4 netto (−2, +6) |
| Dach-Dreiecke | 13.692 | **13.692** | 0 |
| Körper-Dreiecke | 362 | **410** | +48 |
| Gesamtdreiecke | **14.054** | **14.102** | **+48 (0,342 %)** |
| Godot-Surfaces / eindeutige importierte Materialien | 39 / 7 | **43 / 7** | +4 / 0 |
| Godot-GLB-Datei | 783.288 Bytes | **788.320 Bytes** | +5.032 Bytes |

**Regressionsbeleg:** 34 unveränderte GLB-Meshes behalten **exakt gleiche POSITION-/INDEX-Payloads, Materialzuordnung und praktisch gleiche Transforms** (Serializer-Float-Toleranz 2×10⁻⁵); von den weiteren drei alten Meshen werden genau zwei positive Seitenstreben entfernt und eine positive Platte um 0,065 m versetzt, ohne ihr Mesh zu ändern. Alle Dach-, Tür-, negative-X-Wand-, Giebel- und Mauerflächen bleiben gleich. A/B-Bounds identisch (Godot X `±2,89`, Höhe `0…4,528018`, Z `±3,935`), Boden-Pivot `(0,0,0)`. 7 identische glTF-Materialdefinitionen; Godot: Clay, Stone, Door und Dach pro Surface/Wert gleich, Oak-Mehrkosten ausschließlich 48 neue Dreiecke. Nach Blender-Prozess Quelle SHA-256 weiterhin `38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae`. Keine generelle Mesh-Fusion/Optimierung.
