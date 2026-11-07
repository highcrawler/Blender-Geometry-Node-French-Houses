# ART-BEAM-01 – kontrollierte Bildbewertung

[**Blender/Godot A/B/C-Vergleichstafel**](../experiments/art_beam_01/screenshots/comparison_board.png). Das isolierte Ziel ist der linke, diagonale Knieverband **links vom Fenster** (nicht die gemeinsame Dachplatte und nicht das Fenstermodul). Die Kameras, Auflösung, Farbe aller anderen Bauteile und Licht sind je Engine/Ansicht gleich; die Godot-Distanzansicht aus MOD-02 ist bewusst beibehalten.

- **A (Original):** klare, einfache stilisierte Silhouette; warmes Oak, keine künstlichen Maserungsstreifen. Enden überlappen wie im unveränderten ART-01-Boxrahmen.
- **B (Hand-hewn-Geometrie):** Bei Detailblick lassen sich Bevel-Lichtkanten und eine extrem subtile Abweichung erkennen. Von der normalen Spielkamera **kein sichtbarer Gewinn gegenüber A**. Der Preis von 12 auf 428 Δ für diesen Balken ist zu hoch.
- **C (Geometrie + gebackene Weathered/Riss-Maske):** Im Nahbild längsgerichtet und technisch importiert, aber die dunklen Linien sind **zu gerade und zu regelmäßig**, eher künstliche Streifen als vereinzelte tiefe Holzrisse. Bleibt warm statt fotorealistisch grau; trotzdem schlechterer Stil als A. Aus 300-px-Wandansicht verschwindet der Unterschied fast vollständig.

**Vorläufige künstlerische Rangfolge: A BEST; B nahe A, jedoch kein Aufwand-/Nutzengewinn; C unter A/B.** Das ist keine Behauptung, dass Kantenalterung allgemein untauglich ist: nur dieser konkrete Bevel-/Clouds-/Voronoi-PoC auf **einem** 9-cm-Knieverband mit unveränderter Umgebung wurde getestet. Mehr Noise/mehr Polygone oder mehr Balken anzufassen ist ohne sichtbare Demonstration ausdrücklich nicht gerechtfertigt.
