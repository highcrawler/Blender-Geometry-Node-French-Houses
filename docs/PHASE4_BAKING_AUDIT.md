# Phase 4 – Audit des originalen Putzshaders

Basis: Phase-3-Abschlusscommit `4b59dc5`, Branch `experiment/texture-baking-04`. Blender 5.2.2 LTS / Godot 4.7. Repository bei Start sauber bis auf die bereits vorhandenen, weiterhin unberührten `scripts/phase2_probe.py` und `scripts/phase2_api_probe.py`. Alle bisherigen Phase-3-Dokumente und `export_houseone_materials.py` wurden gelesen; keine Änderungen daran. Quelle SHA-256: `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5` vor/nach den Versuchen unverändert. Kein Speichern der Originaldatei, keine Änderungen an `GenerateHouse`.

## Konkrete Farbstruktur

Vollständige Nodes, Socket-Defaults, Links, Untergruppen und Mesh-Attribute: [source_audit.json](../tests/baking/phase4/source_audit.json), reproduziert mit [phase4_audit.py](../scripts/phase4_audit.py).

- `Texture Coordinate.Generated → Noise Texture` (Scale 1,6, Detail 6,4, Roughness 0,936) → `Map Range` (0,1…0,4 auf 0,1…1). Ergebnis wird in `Mix.002` mit dem GN-Attribut `PaintColor` multipliziert. HouseOne hat hier konstant Weiß. Die verbundene `Color Ramp` hat keinen weiterführenden Farbpfad und bestimmt die sichtbare Farbe nicht.
- Derselbe Generated-Eingang → `Noise Texture.001` (Scale 0,5, Detail 6,4, Roughness 0,528) → `Map Range.001` (0,395…0,4 auf 1…0) → Faktor von `Mix`. Dieser mischt Putz mit dem Ergebnis von `BricksTriplanar.001`. Das ist die **originale Schadensmaske**, keine neue Maske.
- `Mix → Vector Math SCALE 0,25 → Principled BSDF.Base Color`. Dieser oft übersehene Faktor erklärt, warum ein Bake deutlich dunkler als der unverbundene Principled-Default aus Phase 3 sein darf. Keine manuelle Aufhellung oder Materialkorrektur vorgenommen.
- `BricksTriplanarBricks → TriplanarMap`: `LocalPosition` liefert XY/XZ/YZ-Projektionen; `LocalNormal` bestimmt die normalisierten Projektionsgewichte. Positionsabhängiges Noise verzerrt die Projektionen. Drei `WalltextureMonoDirection.Brick`-Instanzen liefern die gewichteten Ziegelfarben. Die Brick-Textur hat Scale 6,7, Originalfarbwerte ungefähr `(0,8002;0,5632;0,2911)` und `(0,5454;0,4095;0,3084)` in linearer Darstellung. Noise beeinflusst Mörtel und Sättigung; weitere Voronoi-/Mix-Zweige sind im Knotengraph enthalten, nicht jeder davon erreicht den Farbausgang.

## Farbe versus Oberflächenform

`Noise Texture.001 → Math LESS_THAN 0,4` steuert separat `Mix.001`: geometrische Normale versus Bump-Normale aus der Ziegelgruppe. Dieser Pfad geht ausschließlich an `Principled.Normal`. Ziegelfugen, Relief und deren beleuchtungsabhängige Kanten können deshalb nicht vollständig in einem reinen Color-Bake erscheinen. `BackFaceCheckerShader` umschließt den BSDF; sein Value-Faktor ist 0, sodass der reguläre Shader ausgegeben wird. Kein Beleuchtungs-, Normal-, Roughness- oder Metallic-Bake.

## Koordinaten und Reichweite des Nachweises

Die Farbstruktur ist **nicht UV-abhängig**. Putzvariation und Schadensmaske hängen an objektbezogenen Generated-Koordinaten; das Mauerwerk hängt an den erhaltenen GN-Attributen `LocalPosition` (POINT) und `LocalNormal` (CORNER). `PaintColor` ist POINT/FLOAT_COLOR. Ein neues Ziel-UV verändert diese Shaderlogik nicht. Die lokale Exportgeometrie wird beim Baking nicht verschoben; die Zentrierung geschieht über den Objekttransform. Das vollständige ausgewertete Mesh bleibt erhalten, damit dessen Generated-Bezugsraum nicht durch das Herauslösen nur der Putzflächen geändert wird.

**Einschränkung:** `new_from_object` übernimmt den Mesh-Anteil des GN-Ergebnisses, nicht alle separat ausgegebenen Instanzen. Das ist bereits der Phase-3-Stand mit 50.944 Dreiecken. Eine zusätzliche echte GN-Kontrolle (`blender_gn_control_*.png`) zeigt mehr Fachwerk, Fenster-/Pflanzendetails und abweichend erscheinende Schadensverteilung. Sie ist ausdrücklich nicht der Vergleich auf identischer Geometrie. Original-Mesh-Texspace und ausgewertete Mesh-Texspace unterscheiden sich; siehe `audit.log`. Gleiche Generated-Eingaben zwischen vollständigem GN-Original und Exportkopie sind damit **nicht nachgewiesen**. Der zuverlässige Nachweis dieser Phase gilt für den Originalshader auf derselben Phase-3-Meshkopie. Kein stillschweigender Anspruch auf vollständige Original-GN-Treue.

## Bake und Export

[bake_houseone_plaster.py](../scripts/bake_houseone_plaster.py) lädt ausschließlich die originale Datei und unterstützt ausschließlich HouseOne. Die Originalmaterialien werden für die aktiven Bake-Image-Nodes kopiert. Andere Materialslots bekommen einen nur im RAM existierenden 1×1-Sink; allein Putz schreibt in die Ergebnistextur. Ein leerer ungenutzter Materialslot erzeugt eine harmlose Blender-Info. Cycles CPU, DIFFUSE, nur `COLOR`, Direct/Indirect aus, Seed 0, 1024², PNG, sRGB, 8 Pixel EXTEND. AgX wird nur für Vergleichsrenderings verwendet, nicht als Bildtransformation in die gespeicherte Base Color eingebrannt.

Danach: einfache Principled-Materialien mit exakt den Phase-3-Konstanten; ausschließlich der Putz bekommt `UV Map PlasterBake → Image Texture → Base Color`. Original-UVMap bleibt zusätzlich erhalten. Export nur Auswahl **und aktive isolierte Szene**. Frühe Arbeitsläufe erkannten eine wirkungslose UV-Auswahl und ein fremdes ausgewähltes Beispielobjekt; beide Fehler wurden vor der finalen Ausgabe behoben und durch Assertions abgesichert. Keine fehlgeschlagenen GLBs als Ergebnis archiviert.
