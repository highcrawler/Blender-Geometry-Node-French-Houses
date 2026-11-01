# Phase 4B – Visuelle Verifikation

Alle Einzelbilder sind echte Blender-Cycles-Ausgaben bzw. Screenshots eines grafischen Godot-Prozesses. Die Tafeln werden ausschließlich aus diesen Bildern zusammengesetzt. Keine Illustrationen oder nachträglich verschobenen Schadensmasken.

## Vergleichsbilder

| Ansicht | Geometrie A/B/C mit Originalshadern | Original-GN / Phase4-Bake / Phase4B-Bake | Godot vorher/nachher |
|---|---|---|---|
| Iso | [Tafel](../tests/baking/phase4b/geometry_iso.png) | [Tafel](../tests/baking/phase4b/comparison_iso.png) | [Tafel](../tests/baking/phase4b/godot_comparison_iso.png) |
| Front | [Tafel](../tests/baking/phase4b/geometry_front.png) | [Tafel](../tests/baking/phase4b/comparison_front.png) | [Tafel](../tests/baking/phase4b/godot_comparison_front.png) |
| Seite | [Tafel](../tests/baking/phase4b/geometry_side.png) | [Tafel](../tests/baking/phase4b/comparison_side.png) | [Tafel](../tests/baking/phase4b/godot_comparison_side.png) |
| Fassade | [Tafel](../tests/baking/phase4b/geometry_facade.png) | [Tafel](../tests/baking/phase4b/comparison_facade.png) | [Tafel](../tests/baking/phase4b/godot_comparison_facade.png) |

Die dritte Spalte der Geometrietafeln verwendet vollständige realisierte Geometrie mit fixiertem Texspace und denselben Originalmaterialien; die Bake-Tafeln zeigen hingegen die vereinfachten PBR-Materialien. Das sind unterschiedliche Fragestellungen.

## Kontrollierte Bedingungen

Blender: 640×480, Orthografie, identische Szene/Welt/Area-Leuchte und Objektpositionen. Alle beleuchteten Shader-/Bake-Vergleiche: Cycles CPU, **16 Samples, Seed 0, Denoising an, Standard View Transform**. Kein nachträgliches Aufhellen des Putzes. Die Welt verwendet den neuen neutralen Blender-World-Default bei Stärke 0,8; Area 1.800 W, Größe 9, Ausgangsposition `(2,-3,12)` im zentrierten Vergleichsrahmen. Transparenter Hintergrund; Tafeln unterlegen diesen nur einheitlich dunkel.

Kameras im zentrierten Vergleichsrahmen, beim Blender-Rendering gemeinsam in originale Weltkoordinaten verschoben:

| Ansicht | Eye | Target | horizontale Ortho-Skala |
|---|---|---|---:|
| Iso | 12, −15, 12 | 0, 0, 3,7 | 15 |
| Front | 16, 0, 5,2 | 0, 0, 3,7 | 12 |
| Seite | 0, −16, 5,2 | 0, 0, 3,7 | 12 |
| Fassade | 11, −5, 4,8 | 0, −0,4, 4,2 | 6 |

Silhouetten/Generated-Diagnosen: Emission, 8 Samples, Denoising aus; keine störenden Material-/Lichtunterschiede. Original und realisiert verwenden je Ansicht identische Kameras und Sample-Einstellungen. Original und Phase4B sind in allen vier Silhouetten **RGBA-identisch**. Die separaten `silhouette_delta_*.png` markieren gegenüber Phase4 fehlende Außenpixel magenta, gemeinsame Pixel grau, zusätzliche Pixel cyan. Innere fehlende Balken sind im reinen Umriss nicht sichtbar; dafür dienen Originalshaderbilder und der vollständige Polygonabgleich.

## Sichtprüfung

- Dachziegel, Dachformen, Gauben, Stein- und Wandgrundgeometrie waren bereits im direkten Mesh vorhanden; keine geometrische Korrektur ihrer Form nötig.
- Zuvor fehlendes diagonales Fachwerk, Fenster-/Gaubenrahmen, Scheiben und Pflanzen sind in Phase4B wieder vollständig vorhanden. Besonders deutlich in Iso und Fassade.
- Keine versehentlich mitexportierten anderen Häuser/Quellobjekte, keine neuen Doppelbauteile; Bijection und Godot-Materialdreieckszahlen bestätigen die Bildprüfung.
- Große vertikale Putzschadensbereiche liegen unverändert über den Stockwerken. Sie werden durch die zurückgekehrten Balken und Fenster teilweise verdeckt, **nicht verschoben**. Gerade diese neue Verdeckung hatte den früheren Vergleich erschwert.
- Schmaler linker Schaden und braune Ziegelbereiche stimmen räumlich überein. Das 1024²-Bake bleibt weicher; fehlendes Bump-Relief verändert Fugenbeleuchtung, nicht die zugrunde liegende Farbmaske.
- Keine auffälligen neuen schwarzen UV-Nähte in den vier Ansichten. Das Atlaslayout ist exakt gleich Phase4; dessen bestehende UV-Analyse bleibt gültig. Keine Garantie für jede Entfernung/Mip-Stufe oder jede verdeckte Fläche.

### Messbare Bildabweichung

[`image_metrics.json`](../tests/baking/phase4b/image_metrics.json) enthält exakte Silhouettenvergleiche und zusätzlich eine **heuristische** warme Ziegelmaske innerhalb der erodierten sichtbaren Putzflächen: `R−B > 7` und `R−G > 1` in 8-Bit-RGB. Die `damage_delta_*.png` zeigen Übereinstimmungen grau, nur Referenz magenta, nur Test cyan.

Gemessene IoU: **0,90766** für Phase4-Bake, **0,91975** für Phase4B-Bake, **0,99354** für die korrigierte Geometrie mit Originalshader gegenüber dem tatsächlichen Original. Dieser beleuchtungsabhängige Schwellenwert ist keine Ground-Truth-Schadenssegmentierung und kein Abnahmekriterium. Bump, indirektes Licht, Materialvereinfachung und Resampling erzeugen Unterschiede. Der stärkere Koordinatennachweis ist deshalb der **Float-Generated-Vergleich mit Fehler 0**, zusätzlich der **vollständig byteidentische Phase4-/Phase4B-Putzatlas**. Es wird kein Pixelgleichstand zwischen beleuchtetem Original und Base-Color-Bake behauptet.

## Godot 4.7: tatsächlich ausgeführt

Grafischer Prozess, **Godot 4.7.stable**, OpenGL 3.3 Compatibility, NVIDIA RTX 3060. Kein Headless-Screenshot-Ersatz. Headless wurde nur der Editorimport ausgeführt; Exit 0. Beide Assets wurden danach im selben grafischen Lauf nacheinander instanziiert und aus allen vier Kameras aufgenommen.

| Kontrolle | Phase4 | Phase4B |
|---|---:|---:|
| MeshInstances | 1 | 1 |
| Surfaces | 5 | 12 |
| Dreiecke | 50.944 | 154.602 |
| Putz-Albedo | 1024² | 1024² |
| texturierte Materialflächen | 1 | 1 |
| AABB-Ausdehnung X/Y/Z in Godot | 3,927816 / 8,150175 / 6,485448 | 3,927816 / 8,150175 / 6,561168 |

[`godot_capture.log`](../tests/baking/phase4b/godot_capture.log), [`godot_import.log`](../tests/baking/phase4b/godot_import.log), [`godot_measurements.json`](../tests/baking/phase4b/godot_measurements.json) protokollieren Materialnamen, Materialdreieckszahlen, Texturgröße und Bounds. Die bekannten Blender→Godot-Achsen sind berücksichtigt. GLB-UVs des Putzes sind innerhalb 0…1, `TEXCOORD_1` vorhanden; das eingebettete PNG ist byteidentisch. Godot erhält UV-Skalierung 1. Keine neuen Geometrie-/UV-/Importfehler beobachtet.

## Bewusst verbleibende Materialgrenzen

Die vier ursprünglichen Nichtputz-PBR-Materialien behalten die Phase-3-Konstanten. Für die sieben neu erhaltenen Materialtypen werden nur die jeweiligen ursprünglichen Principled-Defaults übernommen, keine weiteren Texturen gebacken. **Insbesondere Blüten erscheinen weiß statt prozedural rot/orange**; Glas besitzt hier keine originalgetreue Transmission. Das ist eine explizite Nichtputz-Materialvereinfachung dieses begrenzten Tests, kein Beleg vollständiger Originalmaterialtreue. Sie ist in Blender- und Godot-Bildern sichtbar und wird nicht als erfolgreich übertragener Originalshader ausgegeben.

Der PASS dieser Phase bezieht sich auf vollständige relevante Geometrie, erhaltene Materialzuweisungen und die geprüften Putzkoordinaten/-schäden, **nicht** auf eine fertig texturierte Originalhaus-Replik. Allgemeine Materialübertragung, Normalen- und Roughness-Bakes bleiben außerhalb des Auftrags.
