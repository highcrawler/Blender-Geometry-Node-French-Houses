# Phase 8D – Ergebnis

**TECHNICAL RESULT: PASS** · **VISUAL RESULT: UNCONVINCING** (keine künstlerische Freigabe durch den Benutzer).

Branch `experiment/procedural-cottage-thatch-08d`, Ausgang `3749fa4`; Blender 5.2.2 LTS. Neue Dateien ausschließlich unter [`experiments/cottage_generator_08d/`](../experiments/cottage_generator_08d/) und `docs/PHASE8D_*.md`. Vier Dachzustände am **gleichen Long Cottage**. [Referenz](PHASE8D_THATCH_REFERENCE.md) · [Baukonstruktion](PHASE8D_HYBRID_DESIGN.md) · [Bildpaare und kritische Beurteilung](PHASE8D_VISUAL_COMPARISON.md) · [Vierfachtafel](../experiments/cottage_generator_08d/screenshots/all_four.png) · [Vierfachtafel bei ~300 px](../experiments/cottage_generator_08d/screenshots/all_four_300.png).

| Messwert | 8B BASELINE | 8C A | 8C B | 8D H |
|---|---:|---:|---:|---:|
| Dachkörper-Dreiecke (H) | — | — | — | 1.280 |
| Bündel-Dreiecke (H) | — | — | — | 4.380 |
| First-Dreiecke (H) | — | — | — | 212 |
| **Dach-Dreiecke** | **3.604** | **7.236** | **1.572** | **5.872** |
| Gesamt-Dreiecke | 3.966 | 7.598 | 1.934 | 6.234 |
| Materialien | 5 | 5 | 5 | 5 |
| Traufmodule / Teilstreifen | — | — | — | **82 / 219** |
| Erzeugung im *einen gemessenen* Blender-Lauf | 20,24 ms | 35,07 ms | 37,21 ms | **42,16 ms** |
| Rohpayload-Untergrenze aller Meshes (XYZ+Index) | 73.632 B | 138.048 B | 37.104 B | 118.320 B |
| Gespeicherte Collection auf Platte | 928.805 B | 853.421 B | 705.191 B | 747.957 B |

[Maschinenlesbare Einzelmessungen](../experiments/cottage_generator_08d/measurements.json). Ein einzelner Lauf ist **kein** FPS- oder Erzeugungsdauer-Benchmark. Dateigrößen sind **kein** Blender-Heap-RAM; Rohpayload ist ausdrücklich nur eine aus gezählten Vertices und Dreieckindizes errechnete Untergrenze.

**Technischer Nachweis:** Die 8B-Baseline stimmt als Multimenge der Objekt-Meshes mit dem unabhängig gespeicherten 8B-Blend überein, ebenso A/B mit den archivierten 8C-Collections. Alle vier Zustände sind bei gleichem Seed geometrisch reproduzierbar; Nicht-Dach-Geometrie und Gesamt-Gebäudehöhe identisch. H-Tragschalen: je 0 nicht-manifold Kanten, 0 doppelte Faces, gültige Normalen und positives signiertes Volumen. Beide kombinierten Bündel-Meshes und First sind geschlossen; Bündel berühren/überdecken die Schale absichtlich. Breitere/tiefere **temporäre Testkonfiguration** (5,6 × 8,3 m) erhöht die Modulzahl von 82 auf 92 und passt die Stützdachbreite an, ohne ein neues Hausartefakt zu erzeugen. Die Materialslots und verknüpften Farbraum-/Roughness-/Normal-Knoten sind geprüft; kein Volltest aller möglichen Selbstüberschneidungen, UVs oder GLB-Exporte.

**Vier Antworten:**
1. **Aus mittlerer Entfernung besser als A?** Nicht eindeutig: H verbessert die Traufkante, A hat weiterhin die auffälligere gesamte Dachstruktur. [~300-px-Vergleich](../experiments/cottage_generator_08d/screenshots/all_four_300.png).
2. **Erkennbar gebündeltes Stroh?** Im [Traufdetail](../experiments/cottage_generator_08d/screenshots/variant_h_eave.png) teilweise; als Gesamtgebäude bei ~300 px noch **nicht zuverlässig**. Bündel wirken gelegentlich wie schmale Plättchen, Fasern wie Holz.
3. **Polygonaufwand gerechtfertigt?** +2.268 Dach-Dreiecke vs. Baseline und +4.300 vs. B sind technisch begrenzt, aber **künstlerisch noch nicht gerechtfertigt** ohne Lesbarkeit aus Distanz; A hat 1.364 Dach-Dreiecke mehr als H.
4. **Grundsätzlich GLB-geeignet?** Ja für die Meshes nach späterer UV-/Überlappungsprüfung. Nein für **identischen visuellen Eindruck ohne weitere Arbeit**: gerichtete Shader-Noise, Ramp, Roughness und Bump benötigen später Baking oder Engine-Shader. Kein Export in dieser Phase.

**Genau ein nächster Schritt:** Die große und die ~300-px-Vierfachtafel dem Benutzer zur gezielten künstlerischen Entscheidung über die Dachwirkung vorlegen; **bis dahin kein weiteres automatisches Dach-Refinement und keine Integration**. Kein Merge nach `main`.
