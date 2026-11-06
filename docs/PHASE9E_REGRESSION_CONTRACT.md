# Phase 9E – verbindlicher Regressionstest-Vertrag (für die spätere Extraktion)

**Referenz: Blender 5.2.2 LTS, Commit `9e1c042`, [`09D/measurements.json`](../experiments/wooden_roof_system_09d/measurements.json).** Genau die acht unten genannten Testpunkte sind nachgewiesen; gültige Cottage-Eingabeintervalle (`width 3–8`, `depth 2.8–9`, `wall_height 2–3`, `pitch 35–60`, Seed 0..2³¹−1) sind **keine** Freigabe ihres gesamten kartesischen Produkts. Werte in Metern/Grad. Gleiche Parameter und Generatorversion erzeugen identische lokale Meshes auch nach anderen Häusern; CLEAN/AGED haben je Gebäude denselben Dach- **und** Nicht-Dach-Geometriehash. AGED-Mooszahl muss unverändert bleiben.

| Fall | Width × depth | Wall; pitch; seed | Reihen je Seite | Schindeln | Dach-/Gesamttris | AGED Moos-Schindeln |
|---|---:|---|---:|---:|---:|---:|
| Long | 5.1 × 7.3 | 2.3; 40°; 23 | 20 | 1,137 | 13,692 / 14,054 | 36 |
| Compact | 4.0 × 3.5 | 2.3; 48°; 11 | 18 | 534 | 6,456 / 6,818 | 21 |
| T01 | 3.0 × 4.3 | 2.0; 42°; 31 | 13 | 464 | 5,616 / 5,978 | 30 |
| T02 | 8.0 × 5.2 | 3.0; 42°; 37 | 31 | 1,302 | 15,672 / 16,034 | 25 |
| T03 | 5.2 × 2.8 | 2.4; 44°; 41 | **21** | 524 | 6,336 / 6,698 | 15 |
| T04 | 5.0 × 9.0 | 2.5; 44°; 43 | 21 | 1,446 | 17,400 / 17,762 | 49 |
| T05 | 5.0 × 5.0 | 2.2; 35°; 47 | **18** | 737 | 8,892 / 9,254 | 31 |
| T06 | 5.0 × 5.0 | 2.8; 60°; 53 | 29 | 1,179 | 14,196 / 14,558 | 26 |

## SHA-256-Referenzen (für CLEAN **und** AGED identisch)

| Fall | Dach (64 hex) | übriges Cottage (64 hex) |
|---|---|---|
| Long | `d9808450846c8d9476e09c21c0192475e36b58e18a7ef568423747484fadf1c3` | `0000359066faa8ad131f7de176d7b36010e590ad3bbc64c20d4c7b274551f7a2` |
| Compact | `c45e8a6a73ff66e977fb2ec1bb69c8f7a6cabc89e68d41149c5130173bd65c5f` | `81c3c3fca92756fc6099a470307e021afea2cf822ce7534ca3f35d9d4a671227` |
| T01 | `70bb98906f359ecdd2cc891441d0f5eda0681b29a9db50173b29ef9de082a9e1` | `a579f4fcc0682c335ca1fa950be54274167de74edf76158d2c467ea85827d332` |
| T02 | `edb9b970610d4b509adbfaafc42a8689c13a6cdeca5bcc8dc3a5278c7ff0f2d7` | `27e9d83e57b1f722694b1ad9ef33774e6bc72dec7d958d9ad983c8badfc1ac70` |
| T03 | `fbc620c23515b0c19c0a588279c503cfe8f7e7177791610d09d4f681f1af8b35` | `b5ae396b9c5ad5ce640a666d58659523cf536a71666d69190728205fca3a90b7` |
| T04 | `f2f625151f014b82ce06701518274c86b75e691b41d0f2fcf5c6aea095b73c2f` | `bc6f9c7d090fba6a7c135d7e5b8fef129c98574d29abc9db087421fb8aaffa59` |
| T05 | `46a49d27cd1901c00def1099b70fb67e355200a072ae209b02f2af7889650b13` | `bdb809a5911295b5c324ecc0c27db98382c762b1b4cf6e77739fe82ce9c21a1f` |
| T06 | `78a0b6d0771cb35a9b148c5d92742af217aefad3623d1522d65c1538a703d0ff` | `b6af10d7ce20c14190f1020af2ecd354f7d86c8aab0618f3222f6c2a9354d497` |

Hashmethode: [`hash_objects` aus 09B](../experiments/wooden_roof_system_09b/audit.py) bildet für **jedes** Mesh einen SHA-256 über `repr(tuple(round(float(x),6) for x in object.matrix_basis @ vertex.co))` für die Vertices in Indexfolge und `repr(tuple(polygon.vertices))` für die Polygone in Indexfolge. Die einzelnen Mesh-Digests werden sortiert und als Hex-Strings konkateniert erneut SHA-256-gehasht. **Materialien und Objektname sind absichtlich nicht im Geometriehash**; sie erhalten separate Prüfungen. Der Basisvergleich erfolgt im unveränderten Hauslokalrahmen (Root=Identität), *vor* einer optionalen Gebäudeplatzierung. Unveränderte lokale Float32-Meshvertices und Polygonwinding/-indizes sowie Material-Slot-Face-Indizes und Shader-Werte sind zusätzlich gegen die gespeicherte [09C `.blend`](../experiments/wooden_roof_system_09c/wooden_roof_validation_09c.blend) zu prüfen. Bei gewollter Reorganisation der Parent-Hierarchie wird die lokale Geometrie/Root-Transform gesondert verglichen; sie ist **kein** Vorwand für einen anderen Meshhash. Präfixe und bloße Dreieckszahlen genügen nicht.

## Pflichtprüfungen / Freigabegates

1. Exakt dieselben acht Konfigurationen/Seeds × CLEAN/AGED erzeugen; `RoofResult.courses_per_side` gegen **aus Mesh-Reihen unabhängig abgeleitete** Werte prüfen (insbesondere T03=21, T05=18), ebenso Schindelanzahl, Dreiecke, Rollen-/Eigentümerobjekte und vier Dachmaterialslots. Keine Änderung des internen AGED-`n_courses`-Moosprädikats zur kosmetischen Erfüllung der Zählung.
2. Geometriehashes gegen obige **vollständige** SHA-Werte; CLEAN/AGED je Fall gleich, voneinander isolierte Gebäude auch bei anderer Erzeugungsreihenfolge. Volumen/geschlossene Meshes jeder Schindel, beider Decks und Firstplanken, valide Normalen, positive Flächen, keine identischen Doppel-Schindeln, letzte Reihe bis unter Firstcap. **Giebel-Randreserve <0.09 m, interne Schindellücke <0.04 m, kürzeste Schindel >0.10 m**; es sind technische Testgrenzen, keine historischen Baustandards. T06=0.10728 m ist der bekannte enge Fall; Grenzwerte nicht erhöhen, um ein FAIL zu verbergen. Absichtliche Schindelüberdeckung ist kein Fehler.
3. Materialface-Indizes und CLEAN-/AGED-Shaderwerte/Palette gegen 09D-Inventar; Mooszahlen wie Tabelle, keine externen Texturen; je Cottage acht an Mesh-Slots **referenzierte** Materialdatenblöcke (CLEAN: vierter Roof-Slot nicht auf Flächen benutzt; sieben tatsächlich polygonverwendete Materialien, AGED bei den acht geprüften Fällen acht). Blender-Version/Hashverfahren dokumentieren. Gleiches Seed/gleiche Parameter zweimal und nach anderen Aufrufen reproduzieren; Position `(0,0,0)` vs `(35,12,0)` und Z-Yaw nach Einführung des Roots prüfen, indem **Root-lokale** Geometriehashes identisch bleiben und die Weltgeometrie dem erwarteten Starrtransform folgt. Die Transformprüfung ist ein **zukünftiges Gate**, noch kein belegter 9D-Test.
4. Cottage-Adapter erhält Nicht-Dach-Geometrie und Original-Experimente; Long/Compact gegen gespeicherte 09A/09B-Referenzmeshes vergleichen. Vier Kontrollfälle Long/Compact/T03/T05 × CLEAN/AGED mit unveränderten 09C-Kamera-/Lichtdaten rendern: [09D-Testbilder und RGB-Vergleich](PHASE9D_REGRESSION.md). Pixelgleichheit wurde 09D in der getesteten Umgebung erreicht; bei anderer Renderumgebung zunächst Bildunterschiede getrennt von Mesh-Failures prüfen. **Kein** automatisches Update der Golden-Hashes/Bilder beim Testfehler.
5. Nur nach diesen Gates und expliziter Freigabe weitere rechteckige Gebäudetypen anschließen. Bestehende Phase-6-Exporttests bleiben unabhängig; ein Cottage-GLB-Exporter ist noch nicht vorhanden und verlangt eigene Integrations-/Pivot-/Besitztests.

Ein Unterschied an Geometrie, Material oder Row Count ist **FAIL**, nicht stillschweigend eine neue Referenz. Unausweichliche Geometrieänderung nur als separater, begründeter Change mit neuer technischer und künstlerischer Abnahme.
