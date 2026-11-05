# Phase 8C – visueller Vergleich (ein Long Cottage)

**Gleiche** 5,1 × 7,3 m, Wandhöhe 2,3 m, 40°, Seed 23; 800×600, Cycles CPU, 16 Samples, gleiche zwei Flächenlichter, gleiche Welt, Objektposition und Kamera **pro Ansicht**. Nur die Dachsilhouette rendert Blender Workbench materialfrei in Einheitsgrau. Die [Vergleichstafel](../experiments/cottage_generator_08c/screenshots/all_three.png) wurde ohne Farb-/Belichtungskorrektur aus drei **echten identisch beleuchteten Blender-ISO-Renderings** nebeneinander gesetzt; die zusammengesetzte Tafel selbst ist kein separater Blender-Render. Sie bevorzugt keinen Kandidaten durch unterschiedlich gelegene Lichtquellen.

| Ansicht | BASELINE | VARIANT_A | VARIANT_B |
|---|---|---|---|
| ISO, mittlere Entfernung | [Bild](../experiments/cottage_generator_08c/screenshots/baseline_iso.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_a_iso.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_b_iso.png) |
| Front | [Bild](../experiments/cottage_generator_08c/screenshots/baseline_front.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_a_front.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_b_front.png) |
| Seite | [Bild](../experiments/cottage_generator_08c/screenshots/baseline_side.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_a_side.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_b_side.png) |
| Nahaufnahme | [Bild](../experiments/cottage_generator_08c/screenshots/baseline_detail.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_a_detail.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_b_detail.png) |
| Nur Dach, materialfrei | [Bild](../experiments/cottage_generator_08c/screenshots/baseline_silhouette.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_a_silhouette.png) | [Bild](../experiments/cottage_generator_08c/screenshots/variant_b_silhouette.png) |

## Kritische Bewertung

| Kriterium | BASELINE | A – Geometrie | B – Shader |
|---|---|---|---|
| Nahwirkung | glatte, schindelartige Fläche, zahnige Traufe | weiche überlappende Wülste, aber breite wellige **Bänder** statt klarer einzelner Strohbündel | sehr feine gerichtete Fasern, aber monoton, teils wie Holzmaserung |
| Mittlere Entfernung | Fläche glatt | Schichtung schon sichtbar, natürlicher als Baseline, jedoch repetitive horizontale Streifen; eher gewobene Matte als lockeres Stroh | geringste Abweichung zur glatten Dachplatte; Faseroptik verschwindet aus Distanz |
| Dachsilhouette | harte Schürze | leichte, abgerundete Schichtstufen sichtbar | fast glatt; dünne Linien kaum wirksam |
| Wiederholungsmuster | gleichförmige Traufzähne | wiederkehrende neun Bänder pro Dachseite | regelmäßige feine Richtungsstreifen und gelegentliche dünne Längslinien |
| Game-Asset-Perspektive | bisherige Kosten; noch keine Exportprüfung | geometrisch mit GLB transportierbar, aber rund doppelte Dach-Dreiecke | deutlich kleineres Mesh, entscheidender Blender-Shader-Effekt ohne spätere Bake/Shader-Nachbau **nicht** in Godot erhalten |
| Skalierung auf andere Dachgrößen | alte grid-basierte Regeln | feste neun Schichten und 19 Tiefenintervalle können bei anderen Dimensionen zu sichtbar anderem Abstand führen | Objektkoordinaten-Shader bleibt räumlich orientiert; 12 Einlagerungen/Seite sind noch nicht adaptiv |

**VISUAL RESULT: A (relativer Vergleichssieger, keine künstlerische Freigabe).** A wirkt aus der mittleren Entfernung erstmals deutlich weniger wie eine glatte Platte. Auch A liest sich noch nicht eindeutig wie lose gebündeltes Stroh: die Wellen sind zu regelmäßig und an den Giebelseiten sind dunkle Anschlusslinien sichtbar. B gewinnt bei Geometriekosten und feiner Nahstruktur, verliert aber gerade beim wichtigeren mittleren Abstand und beim Export ohne Shadertransfer. Eine endgültige Dachtechnik ist damit **nicht** entschieden.
