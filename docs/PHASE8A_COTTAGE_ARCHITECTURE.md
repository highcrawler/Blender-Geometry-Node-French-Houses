# Phase 8A – Cottage Prototype 01: Architektur

**Isolation:** Experiment-Branch `experiment/procedural-cottage-08a`, Basis `main` `66d90c8` (Add-on 0.2.0), getrenntes Worktree. Der schmutzige Phase-7-Arbeitsbaum und Branch `0aaa910` bleiben unberührt. Blender 5.2.2 LTS.

## Prüfung der IRCSS-Bauteile

Lesender Audit: `blender -b GeometryNodesFrenchHous.blend -P experiments/cottage_generator_08a/audit_source.py`. `GenerateHouse` enthält **1023 Nodes** und hängt u. a. von `CreateDiagonalBeams` (26 Nodes), `WindowBeams` (63 Nodes, wiederum `Curve Info`), `Generate Windows`, `GetPositionBasedSeed` und `Switch On Roof Type` ab. `WindowWalls` hat 141 Nodes und vier Untergruppen; `CurvedDoorFromEdges` 198 Nodes. `Curve Info` hat 19 Nodes und hängt von `Curve Root`/`Curve Tip` ab. Das beliebige Anhängen selbst der einfachen IRCSS-Balkenoperationen würde für eine kleine Hütte komplizierte Edge- und Positionssemantik einschleppen. **Keine IRCSS-Gruppe, kein Originalmaterial und kein Originalobjekt wird importiert oder verändert.** Übernommen ist nur das allgemeine Konstruktionsprinzip: entlang zweier Endpunkte orientierte Balken und wiederholte Geometrie; der Code ist neu.

## Entscheidung: Blender-Python statt Geometry Nodes

`cottage.py` berechnet Rechteckwände, ausgesparte Tür, Giebel, Tragwerk und Dach explizit anhand typisierter Parameter. Python ist für die ungleichmäßigen geschlossenen Dachflächen und verifizierbare Seed-Regeln überschaubarer als eine weitere große Node-Gruppe. Spätere Live-Bedienung könnte den Generator beim Ändern eines UI-Parameters erneut ausführen; **der Prototyp ist noch nicht live und nicht ins Add-on integriert**. Ein separates kleines GN-System wäre alternativ sinnvoll für interaktive Streuung von Strohdetails, ist hier nicht erforderlich. Keine allgemeine Gebäude-Engine.

Module: `cottage.py` (Parameter/Material/Geometrie), `variants.json` (Konfigurationen), `build_examples.py` (Messung, Kameras, Blender-Render, Testdatei), `test_parameters.py` (Regressionsprobe), `audit_source.py` (nur lesend). Keine externen Assets. Blender-Testdatei und Screenshots liegen ausschließlich in `experiments/cottage_generator_08a/`.
