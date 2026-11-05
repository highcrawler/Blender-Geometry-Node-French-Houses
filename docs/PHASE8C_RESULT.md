# Phase 8C – Ergebnis

**TECHNICAL RESULT: PASS** · **VISUAL RESULT: A** (nur relativ, noch **keine** künstlerische Freigabe und **keine** Entscheidung über eine endgültige Dachtechnik).

Ausgang `f268615`; Branch `experiment/procedural-cottage-thatch-08c`; Blender **5.2.2 LTS**. Genau ein unverändertes Long Cottage mit drei Dachzuständen. [Dacharchitektur](PHASE8C_ROOF_ARCHITECTURE.md) · [alle 15 Einzelbilder und visuelle Beurteilung](PHASE8C_VARIANT_COMPARISON.md) · [Vergleichstafel](../experiments/cottage_generator_08c/screenshots/all_three.png) · [messender Reproduktionslauf](../experiments/cottage_generator_08c/README.md).

| Messwert | BASELINE | A | B |
|---|---:|---:|---:|
| Dach-Dreiecke | 3.604 | 7.236 | 1.572 |
| Gesamt-Dreiecke | 3.966 | 7.598 | 1.934 |
| Materialien | 5 | 5 | 5 |
| Erzeugungsdauer im **einen gemessenen** Blender-Lauf | 20,88 ms | 35,84 ms | 36,04 ms |
| Rohpayload-Untergrenze Mesh gesamt (Position XYZ + Dreiecksindex) | 73.632 B | 138.048 B | 37.104 B |
| Tatsächliche Größe einzeln gespeicherter `.blend`-Collection | 928.805 B | 853.421 B | 705.191 B |
| Wirkung nah | glatt | weiche Schichten, zu breite Bänder | gerichtete Feinlinien, holzartig |
| Wirkung mittel | glatt | Schichtung sichtbar | überwiegend glatte Fläche |
| Silhouette | zahnig | weiche Schichtstufen | nahezu eben |

Die gespeicherten Datei-Bytes enthalten Blender-/Material-Overhead und sind **kein** Heap-RAM-Messwert; die Rohpayload-Zahlen sind **nur** eine aus tatsächlichen Vertices und triangulierten Flächen berechnete Untergrenze, kein behaupteter Blender-Speicherbedarf. Erzeugungsdauer umfasst Python-Mesh-/Materialaufbau, **nicht** Rendern, Shader-Kompilierung oder FPS. Einzelwerte sind kein Performance-Benchmark; [Maschinenlesbare Daten](../experiments/cottage_generator_08c/measurements.json).

Tests: BASELINE mit eigenständigem schreibgeschützten Laden des gespeicherten Phase-8B-Blend verglichen (93 Objektmeshes als Multimenge identischer 6-stelliger Welt-/Basis-Vertexwerte). Jede der drei Varianten zweimal mit gleichem Seed aufgebaut; Geometrie identisch. Nicht-Dachgeometrie und gesamte Gebäudehöhe identisch. Alle sechs tragenden Schalen: jeweils 0 nicht-manifold Kanten, 0 doppelte Faces, normales positives Volumen und gültige Flächennormalen. A: zusätzlich 19 geschlossene Dachdetail-Meshes. B: 24 bewusst **offene**, in die Schale eingelassene dünne Oberflächenstreifen, First geschlossen; keine global einheitliche Manifold-Behauptung. Materialzuweisungen und B-Shader-Node-Verbindung überprüft. Keine globale UV-/Selbstschnitt-/Godot-Export-/FPS-Prüfung.

**Schwächen:** A kostet 3.632 zusätzliche Dach-Dreiecke (+101 %) gegenüber 8B und wiederholt breite Wülste; Vordergiebel-Anschlusslinien und Firstschatten bleiben sichtbar. B spart 2.032 Dach-Dreiecke (−56 %), verliert aber ohne Blender-Shader-Bake oder Shader-Nachbau die entscheidenden Fasern im GLB; aus mittlerer Entfernung wirkt B zu plankartig. Es wurde keine Baking- oder Exportpipeline implementiert.

**Genau ein nächster Schritt:** Die drei identisch beleuchteten ISO- und Dach-Nahaufnahmen dem Benutzer zur **künstlerischen Auswahl bzw. Ablehnung beider Ansätze** vorlegen, bevor ein Dachansatz als Generatorstandard weiterentwickelt wird.
