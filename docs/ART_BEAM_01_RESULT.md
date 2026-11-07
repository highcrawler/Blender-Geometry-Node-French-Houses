# ART-BEAM-01 – Hand-Hewn Weathered Timber

**TECHNICAL RESULT: PASS. ARTISTIC RESULT: A BEST. INTEGRATION RESULT: REJECT (diese B/C-Ausführungen).**

Basis MOD-02 `048dee8`; Branch `experiment/art-beam-01-aged-timber`. Alle Artefakte ausschließlich [`experiments/art_beam_01/`](../experiments/art_beam_01/), Dokumente ausschließlich `docs/ART_BEAM_01_*.md`. Keine produktive Integration, kein Merge, keine Änderung an ART-01/MOD-01/MOD-02/Generator/Dach/Project Pilgrimm. Die originale `.blend` ist vor/nach SHA-256-identisch `38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae`.

**Technischer Befund:** A ist byteidentischer MOD-02-B-GLB; B/C exportieren tatsächlich angewandte Bevel-/Clouds-Geometrie, nicht nur einen Viewport-Modifier. C hat erfolgreiche Cycles-Color-/Tangent-Normal-Bakes 512²; Godot 4.7 importiert und verwendet beide Texturen/Normal-Map. 15 andere Meshes, gemeinsamer Rahmen *außer der isolierten Zielkopie*, Fenstergeometrie, Modul-Pivots/Materialien und die Originalquelle unverändert. Ziel `ART01_KneeBrace_1`: 8→216 Vertices, 12→428 Δ; 16 Gesamtmeshes und 204→620 Δ, GLBs 21.588→49.624→109.884 B. Risse und Bump wurden korrekt gebacken; **technischer Erfolg ist keine Art-Freigabe.** [Geometrie/Anschlüsse](ART_BEAM_01_GEOMETRY.md) · [Shader und Bake](ART_BEAM_01_SHADER.md) · [Godot](ART_BEAM_01_GODOT_TEST.md) · [Bildurteil](ART_BEAM_01_VISUAL_COMPARISON.md) · [Reproduktion](../experiments/art_beam_01/README.md).

## Künstlerische Entscheidungsfragen

1. **Handbearbeitete Kanten?** Nur bei naher Betrachtung schwach. In Spielentfernung nicht deutlich genug.
2. **Verformung?** Technisch organisch/leicht (`0,0015 m`), mit Endausblendung, aber an 300-px-Wand praktisch unsichtbar.
3. **Holzrisse?** C zeigt lange Linien entlang der Balkenachse, aber zu gleichmäßig/parallel: **künstliche Streifen**, keine überzeugenden individuellen Holzrisse.
4. **Zum Cottage passend?** A warm und stilisiert ja; B neutral; C zwar warm, aber Linien passen stilistisch schlechter.
5. **Normale Distanz?** **Nein:** Godot A/B-Distanzbilder pixelgleich, C nur minimale Bildänderung; kein überzeugender Stilgewinn.
6. **Kosten?** **+416 Δ** nur für einen 9-cm-Balken; zwei zusätzliche 512²-Maps und neues nur auf C liegendes Material; 2,3×/5,1× GLB-Dateigröße gegenüber A.
7. **Nutzen/Aufwand?** **Nein.** B erzeugt kaum sichtbaren Gewinn, C erzeugt unruhige, zu saubere Streifen; keine Massenanwendung.

**Genau ein nächster kleiner Schritt:** An demselben isolierten Knieverband eine **gezielt unterbrochene, seltene Längsriss-Maske** mit identischem 512²-Bake und derselben Godot-Distanzkamera gegen A testen; zunächst **keine** zusätzliche Geometrie oder weitere Balken. Nur bei sichtbarem Stilgewinn wäre ein neuer Kandidat vertretbar.
