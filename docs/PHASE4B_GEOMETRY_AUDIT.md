# Phase 4B – Geometrie-Audit

Basis: `03a3e9e` (Phase 4, PARTIAL), eigener Branch `experiment/geometry-coordinate-fidelity-04b`. Startbranch war `experiment/texture-baking-04`. Einzige vorhandene unversionierte Dateien: `scripts/phase2_probe.py`, `scripts/phase2_api_probe.py`; nicht bearbeitet oder aufgenommen. Phase-4-Dokumentation, Bake-/Exportskripte und bestehende Testergebnisse wurden geprüft. Kein Merge, keine Änderung an `main` oder früheren Ergebnissen.

Blender **5.2.2 LTS**, Source SHA-256 vor/nach: `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5`. Die originale `.blend` wird ausschließlich geöffnet, niemals gespeichert. `GenerateHouse` und seine Untergruppen werden nicht verändert.

## A / B / C

- **A ORIGINAL:** tatsächliches `HouseOne` in seiner originalen Welttransformation; direkter Mesh-Anteil plus alle sichtbaren Mesh-Blätter von `depsgraph.object_instances`, ausschließlich `is_instance && parent.original == HouseOne && show_self`.
- **B PHASE4:** `meshes.new_from_object(HouseOne.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)`, exakt die bisherige Methode. Keine Instanzblätter darin.
- **C REALIZED TEST:** Kopie von Objekt **und Eingabemesh**, an unveränderter ursprünglicher Weltposition. Frischer, nachgeschalteter GN-Wrapper `Input Geometry → Realize Instances (Realize All=True) → Output Geometry`. Nur an dieser Kopie. `GenerateHouse` bleibt referenziert/unverändert. Danach ausgewertetes Mesh entnehmen, Testobjekt entfernen. Kein Realisieren anderer Szenenobjekte.

| Messwert | A Original inkl. Blätter | B Phase4 | C Realized |
|---|---:|---:|---:|
| Mesh-Vertices, expandiert | 110.320 | 27.919 | 110.320 |
| Polygone | 97.060 | 20.003 | 97.060 |
| Dreiecke | 154.602 | 50.944 | 154.602 |
| tatsächlich verwendete Materialien | 12 | 5 | 12 |
| Hauptobjekte | 1 | 1 | 1 |
| zusätzliche DG-Instanzblätter | 2.595 | 0 | 0, realisiert |
| resultierende Exportmeshes | – | 1 | 1 |

Mesh-/Objektzahlen sind keine austauschbaren Größen: Original sind ein direkter Mesh-Anteil und 2.595 Mesh-Vorkommen, nicht 2.596 unabhängige Blender-Objekte. Geteilte Blatt-Datablocks werden für den Audit gecacht: **30 verschiedene Blatt-Mesh-Datablocks plus ein direktes Mesh**; siehe `geometry.json`. Godot teilt das eine Exportmesh in zwölf Surfaces nach Material.

### Tatsächlich fehlende Instanzen in B

| Blatt-Typ / Materialslots | Vorkommen | Dreiecke je Vorkommen | zusätzliche Dreiecke |
|---|---:|---:|---:|
| Beam, 14 Vertices | 26 | 24 | 624 |
| Beam, 8 Vertices | 203 | 12 | 2.436 |
| WindowGlass | 19 | 2 | 38 |
| GreenSta.001 / Material.005 | 139 | 52 | 7.228 |
| Greenery | 2.096 | 16 | 33.536 |
| Material.002 | 52 | 48 | 2.496 |
| Material.001 / Material.003 | 60 | 955 | 57.300 |
| **Summe** | **2.595** | | **103.658** |

Das betrifft zusätzliches Fachwerk, Fenster-/Gaubendetails und Pflanzen inklusive der hochpolygonalen Pflanzenteile. Dächer und Steindetails waren nicht pauschal verloren: Roof bleibt **7.256**, Stone **36.740**, Putz **2.210**, GroundFloorWalls **20** Dreiecke. Beam steigt von **4.718 auf 7.778**. Alle zwölf Material-Dreieckszahlen stehen in `geometry.json` und wurden nach GLB-Dekodierung und in Godot erneut verglichen.

## Eigentümerschaft, Quellen, Verschachtelung

[`probe.json`](../tests/baking/phase4b/probe.json) enthält Node-Referenzen samt Socket-Links, Attribute, Transformationen, Collection-Mitglieder und den positionsbasierten Seed-Graphen. Explizite Collection-Quellen: **Plants** in `Generate Windows`, **Set** in `GenerateHouse`. Object-Info-Nodes verwenden überwiegend `Self Object`; unverbundene `Object=None`-Socketdefaults sind daher **kein** Beleg fehlender Objektbezüge. Die Modifier-Interface-Defaults im Report sind als solche bezeichnet, keine behaupteten vollständig ausgelesenen Laufzeitparameter.

GN-Blätter heißen in dieser Blender-Version im DG häufig selbst `HouseOne`: Filtern nach Blattnamen oder `instance_object.name` wäre unzuverlässig. Entscheidend sind DG-Parent, Sichtbarkeit, echte Blatt-`object.data` und `matrix_world`. Alle 2.595 persistenten Pfade sind eindeutig und haben zwei belegte ID-Komponenten; der DG liefert finale Blätter einschließlich verschachtelter Erzeugung. Containerinstanzen werden nicht nochmals addiert. Der vollständige Wrapper-Abgleich prüft unabhängig, dass kein relevanter verschachtelter Rest fehlt.

Bewusst ausgeschlossen: andere Häuser, Beispiel-/Quellobjekte und Collections als eigenständige Szenenobjekte, Licht/Kamera und Hilfsobjekte. Deren tatsächlich von HouseOne referenzierte, sichtbare Instanzgeometrie ist dagegen eingeschlossen. Keine globale Auswahl oder Szenenrealisierung.

**Wichtige API-Grenze:** Für DG-Instanzblätter wird `inst.object.data.copy()` verwendet, nicht erneut `new_from_object(inst.object)`: Letzteres erwies sich im Vorversuch als ungeeignete Re-Evaluierung mit starkem Speicherbedarf; der Versuch wurde beendet. Keine daraus abgeleiteten Zähler oder Artefakte werden als Ergebnis verwendet. `new_from_object` bleibt nur für die echten ausgewerteten Hauptobjekte korrekt.

## Mehr als ein Dreieckszähler

- Bijection aller **97.060 materialbeschrifteten Polygone** A↔C: jeweils gleiche Eckpunktzahl, räumlich übereinstimmende Ecken, jeder Partner genau einmal verwendet. **0 unmatched** auf beiden Seiten, maximaler Eckpunktfehler **1,1681e-6 BU**, Toleranz **1e-4 BU**.
- Ein naiver auf 1e-5 gerundeter Polygonhash liefert 16.626 symmetrische Unterschiede durch Rundungszellgrenzen. Das ist **kein Geometrieverlust**; der zusätzliche tolerante bijektive Test löst diese Mehrdeutigkeit. Beide Werte bleiben im Report sichtbar.
- Original- und C-Silhouetten: RGBA-Pixel in **allen vier Ansichten exakt identisch**.
- Nach GLB-Dekodierung materialweise beidseitiger Vertexpositionsvergleich, Achsenkonversion und Objekttranslation berücksichtigt: maximal **4,771e-7 BU**. Dreieckszahlen je Material ebenfalls exakt. UV-/Normalensplits können die GLB-Vertexzahl erhöhen, ohne Geometrie hinzuzufügen.
- Keine zusätzlich erzeugten Duplikate: bijektiver Polygonvergleich erhält auch die Original-Multiplizität, Export und Godot enthalten genau ein Mesh und die erwarteten zwölf Materialflächen.

### Bounding Boxes (originale Weltkoordinaten, BU)

| Achse | A und C | B |
|---|---|---|
| X | 1,4598937 … 5,3877096 | gleich |
| Y | −15,2952175 … −8,7340488 | −15,2589779 … −8,7735300 |
| Z | −0,4025301 … 7,7476454 | gleich |

Ausdehnung A/C: **3,927816 × 6,561169 × 8,150176 BU**. Zusätzliche Pflanzen erklären die geringe Y-Erweiterung. Keine Maßstabsänderung. Zentrierung/Bodenausrichtung des GLB erfolgt erst am eingefrorenen Exportobjekt, ohne seine lokalen Vertices zu verändern.

Reproduktion und Artefaktindex: [Ergebnis](PHASE4B_RESULT.md). Bildprüfung: [Visuelle Verifikation](PHASE4B_VISUAL_VERIFICATION.md).
