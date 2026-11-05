# Phase 8A – Ergebnis: PARTIAL

**Branch:** `experiment/procedural-cottage-08a` auf `main` `66d90c8`; **Blender:** 5.2.2 LTS. Kein Merge, keine Änderungen an der Phase-7-Arbeitskopie. Experiment: [`experiments/cottage_generator_08a/`](../experiments/cottage_generator_08a/). Technische Architektur: eigenständiger Blender-Python-Meshgenerator; keine `GenerateHouse`-Abhängigkeit. Drei Varianten aus `variants.json`, identischer Generator und feste Seeds. [Vergleichsrender](../experiments/cottage_generator_08a/screenshots/three_together.png), [Dach-Detail](../experiments/cottage_generator_08a/screenshots/thatch_closeup.png); alle Einzelbilder in [Visual Review](PHASE8A_VISUAL_REVIEW.md).

| Metrik | Small | Long | Steep Roof |
|---|---:|---:|---:|
| Breite m | 4.2 | 5.1 | 4.6 |
| Tiefe m | 3.4 | 7.3 | 3.7 |
| Höhe gesamt m | 4.505 | 4.570 | 6.161 |
| Dachneigung ° | 46 | 40 | 58 |
| Dreiecke gesamt | 1,934 | 3,494 | 2,038 |
| Dreiecke Dach inkl. Traufe/First | 1,572 | 3,132 | 1,676 |
| Materialien pro Haus | 5 | 5 | 5 |
| Seed | 11 | 23 | 37 |

Quelle: [`measurements.json`](../experiments/cottage_generator_08a/measurements.json); Dreiecke aus Mesh-Polygonen, nach Quad-Triangulationsäquivalent. Scriptlauf: fünf Parameteränderungen ergeben abweichende Weltgeometrie, gleicher Seed und dieselben Parameter identische Geometrie beim Replay; fünf ungültige Konfigurationen abgewiesen. Beide Dachschalen jeder Variante jeweils 0 nicht-manifold Kanten (BMesh). Sichtkontrolle der Bilder: keine offensichtlich offenen Dachflächen, schwebenden Balken oder doppelten Bauteile; Normalen werden pro Einzelmesh neu berechnet. Die Wände/Giebel sind teilweise offene Einzelmeshes; keine globale Manifold- oder Intersections-Garantie. Kein FPS-Test und keine Engine-Ausfuhr. Details: [Regeln](PHASE8A_GENERATION_RULES.md) und [Sichtprüfung](PHASE8A_VISUAL_REVIEW.md).

**1. Technisch eigenständig?** Ja: kein Library-Appending, keine IRCSS-Gruppen, eigenes prozedurales Mesh und Material.

**2. Unterschiedliche Hütten aus gemeinsamen Regeln?** Ja; Länge, Höhe, Neigung und Saat verändern unabhängige berechnete Teile; drei echte Blender-Renderpaare und Gruppendarstellung belegen dies.

**3. Grundlage für zweiten Add-on-Gebäudetyp?** Technisch ja, **noch nicht visuell freigegeben**: die Strohwirkung ist aus der Distanz zu glatt, die steile Variante wirkt hoch. Deshalb PARTIAL statt PASS.

**Genau ein nächster kleiner Schritt:** eine gezielte Überarbeitung der Strohdach-Silhouette (gestaffelte, leicht gebrochene Traufkante) anhand derselben drei Kameras künstlerisch abnehmen lassen, **bevor** eine Add-on-Integration beginnt.
