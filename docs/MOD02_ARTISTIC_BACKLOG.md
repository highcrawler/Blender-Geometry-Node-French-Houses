# MOD-02 – bewusst nicht implementierte künstlerische Arbeit

Die erste [Fensterwand](../experiments/mod02_window_module/screenshots/comparison_board.png) ist ein funktionsfähiger **technischer Prototyp**, kein freigegebenes Final-Asset. In der ~300-Pixel-Godot-Sicht ist die Öffnung lesbar, aber rechteckige Hölzer und völlig glatte Clay-Fläche wirken handwerklich zu sauber. Der gemeinsame Rahmen, Montage-Pivot und die geprüfte Durchbruchsgeometrie sollen bei späteren **isolierten** Kunsttests stabil bleiben.

1. **Fensterproportionen:** Höhe/Breite relativ zu Riegel, Platte und Gefach nach Augenmaß in der Spielkamera abstimmen; Loch nicht so groß machen, dass das obere Putzband verschwindet.
2. **Rahmenstärke – höchste Priorität als *nächster einzelner* Kunsttest:** Gewicht und Abstufung von seitlichem Holz, oberem Abschluss und Bank gezielt vergleichen. Momentan alle einfache Boxprofile; stärker handwerklich lesbare Rahmensilhouette bei ~300 Pixeln anstreben, aber lichte Öffnung erhalten. **Nicht in MOD-02 umsetzen.**
3. **Holzverbindungen:** Gehrungs-/Zapfen-Andeutung und glaubwürdiger Übergang zu den vier separaten Teilen; die aktuellen rechten Winkel überschneiden sich technisch absichtlich.
4. **Fensterbank:** Neigung/Wasserablauf, feine Überstände, ungleichmäßige Enden; aktuell eine gerade eckige Bank.
5. **Fensterladen:** Evtl. ein einzelner schlichter handmodellierter Laden mit getrenntem Pivot; weder beweglich noch verglast in MOD-02.
6. **Kantenabnutzung:** Sehr sparsame gebrochene Holz-/Clay-Kanten statt vieler dekorativer Polygone.
7. **Leicht unregelmäßiger Putz:** Dezente Flächenvariation ohne Risse am exakt definierten Modulanschluss und ohne neue Seam-Z-Fights.
8. **Verwitterung und Schmutz:** Später gezielt um Fensterbank und unter Holzanschlüssen; MOD-02 verwendet nur die konstanten Materialien aus 9I/9J, keine neue Shader- oder Baking-Pipeline.

Bei jedem zukünftigen Vergleich: zunächst **eine** Änderung, gleiche A/B-Spielkamera, getrennte Godot-Vorschau und neuer Geometrie-/Nahttest. Keine Vermehrung von Fensterformen als Ersatz für Qualität.
