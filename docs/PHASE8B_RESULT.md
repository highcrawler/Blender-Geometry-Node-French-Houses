# Phase 8B – Ergebnis: PARTIAL

Branch `experiment/procedural-cottage-thatch-08b` auf Phase 8A `666a567`; Blender 5.2.2 LTS. [Entwurf](PHASE8B_THATCH_DESIGN.md) · [alle Vergleichsbilder und kritische Sichtprüfung](PHASE8B_VISUAL_COMPARISON.md) · [Messdaten](../experiments/cottage_generator_08b/measurements.json) · [Reproduktion](../experiments/cottage_generator_08b/README.md).

| Variante (unveränderte Parameter und Seeds) | Dreiecke gesamt 8A → 8B | Mehrkosten | Dach-Dreiecke 8A → 8B |
|---|---:|---:|---:|
| Small, Seed 11 | 1.934 → 2.166 | +232 (+12,0 %) | 1.572 → 1.804 |
| Long, Seed 23 | 3.494 → 3.966 | +472 (+13,5 %) | 3.132 → 3.604 |
| Steep Roof, Seed 37 | 2.038 → 2.286 | +248 (+12,2 %) | 1.676 → 1.924 |

**Technischer Befund:** Baseline-Geometrie aller drei Varianten stimmt byteformatgenau im Weltkoordinaten-SHA-256 mit Phase 8A überein. 8B-Skript testet identische Parameterwiederholung/Seed, identische Nicht-Dachgeometrie, unveränderte frühere Dachbauteile und Materialfarbwerte. Je zwei neue Dachschalen pro Variante: **0 nicht-manifold Kanten, 0 doppelte Flächen, positives signiertes Volumen und keine degenerierten Flächennormalen**. Bestehender Parametertest passiert für alle fünf Eingaben und ungültige Grenzwerte. Bestehende 8A-Bilder, Testdatei und Messdatei sind nicht verändert. Keine globale Selbstschnitt-/FPS-Garantie; separate Bauteile berühren einander konstruktionsbedingt.

**Bildbefund:** Traufe weniger linear, die Brüche sind im Detail und im materialfreien Dachvergleich sichtbar. Aus der Dreierperspektive aber zu subtil, das Dach bleibt eher glatt bzw. blockig als überzeugend strohgebündelt. Deshalb **PARTIAL**, nicht PASS; der Benutzer muss die künstlerische Qualität separat beurteilen. Keine Add-on-Integration, kein Merge.

**Genau ein nächster kleiner Schritt:** Die *bereits vorhandene* Traufschürze künstlerisch auf weichere, weniger quaderförmige Stirnseiten justieren und erneut aus denselben Kameras vergleichen; erst nach Sichtfreigabe weitere Arbeiten.
