# ART-WOOD-02 – Natural Timber Breakthrough / harter Art-Gate

**TECHNICAL RESULT: PASS. ARTISTIC RESULT: NONE ACCEPTABLE. INTEGRATION RESULT: REJECT.**

Die geforderte visuelle Abnahme wurde **nicht** erreicht. Daher **kein neues Modul**, keine Integration, keine Gleichsetzung von importierten Texturen mit gutem mittelalterlichem Holz. Branch `experiment/art-wood-02-natural-timber` auf Basis MOD-02 `048dee8`; nur `experiments/art_wood_02/` und `docs/ART_WOOD_02_*.md`. Ein Checkout, kein Worktree, Clone oder Merge. Die Module, Quelle, Generator, Dach, Project Pilgrimm und historischen Experimente bleiben unverändert. [Geometrie](ART_WOOD_02_GEOMETRY.md) · [prozedurale Holzmaps](ART_WOOD_02_SHADER.md) · [Godot-Test](ART_WOOD_02_GODOT_TEST.md) · [Bildkritik](ART_WOOD_02_VISUAL_COMPARISON.md) · [Reproduktion](../experiments/art_wood_02/README.md).

**Test:** einzelner 7,30-m-`ART01_MidRail` mit 12-cm-Querschnitt, nicht wieder ein dünner 9-cm-Knieverband. A identisches MOD-02-B-GLB; B nur modifier-applizierte leichte Clouds-/Bevel-Geometrie; C dieselbe Geometrie mit warmem eigenem prozeduralem Längsseiten-Atlas, diskontinuierlichen Trocknungschecks, zwei importierten Texturen und kleiner Normalwirkung. Godot 4.7 importiert 204/660/660 Wand-Dreiecke, 16 Meshes und 0 fehlende Materialslots; lediglich dieses eine Mesh verändert sich. Die normalen Modul-Pivots, Fensteröffnung und übrigen 15 Meshes sind gleich. `validation.json` meldet technische Reproduzierbarkeit, nicht Art-Freigabe. Original `.blend` unverändert SHA-256 `38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae`.

## Antworten auf die acht Fragen

1. **B besser als A?** In der Makroansicht minimal andere Lichtkante, **nicht** bei normaler Spielkamera; nicht überzeugender.
2. **C besser als A/B?** Im Makro strukturierter und wärmer, **nicht** klar überzeugender auf ~300-px-Wanddistanz; nicht freigeben.
3. **Risse natürlich?** Keine Voronoi-Zebrastreifen mehr, wenige unterbrochene Checks; dennoch in Godot vielfach wie **gezeichnete Striche** statt geöffnete Faser.
4. **Mehr als helle Braunfläche?** Ja auf Nahaufnahme; im Spielkontext dominiert nach wie vor ein langer regelmäßiger Balken.
5. **Normale Distanz?** B und A unterscheiden sich in Godot nach den drei Behauungsfacetten **minimal**, C etwas stärker; kein deutlich lesbarer Handwerkseffekt.
6. **Stil Cottage?** Farbtemperatur passt, nicht jedoch die nahezu perfekte lange Box und der aufgesetzte Eindruck der Risse.
7. **Kosten?** 12→468 Dreiecke (**+456**) und B 21.588→54.020 B; C 218.448 B, zwei eingebettete 1024×512-Maps und ein dritter nur dem Ziel zugeordneter Materialtyp. Für fehlende Bildwirkung **nicht vertretbar**.
8. **Kandidat für alle Balken?** **Nein.** Eine Anwendung auf viele Bauteile würde Kosten und Gleichförmigkeit verbreiten.

**Genau ein nächster kleiner Schritt, ohne neue Module:** Ein **handmodelliertes, am Ende/Anschluss kontrolliert auslaufendes Behauungsprofil** für denselben isolierten Hauptbalken als Gegenprobe zu B erstellen; gleiche Godot-300-px-Spielkamera, keine weiteren Texturen oder Änderungen am Fachwerk. Sollte der Effekt auch dort unsichtbar bleiben, Art-Gate weiterhin geschlossen halten.
