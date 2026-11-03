# Medieval Building Generator – MVP-Architektur

## Grundlage und Abgrenzung

Blender **5.2.2 LTS**, offizielle Extension (`blender_manifest.toml`), MIT wie das Repository. Keine Python-Zusatzpakete. Kein Export, Baking, Shader-Umbau oder Ersatzgenerator. Basisbranch: `experiment/geometry-coordinate-fidelity-04b`, Commit `eee6dac`.

`GenerateHouse` und seine Untergruppen bleiben unverändert. Phase 4B zeigte, dass direktes Evaluated-Mesh allein nicht das gesamte Haus enthält: Fachwerk, Fenster und Pflanzen können GN-Instanzen sein. Deshalb **kein** Mesh-Export/Realize-Wrapper im Add-on: der originale Modifier bleibt live. Positionsabhängige Seeds sind originales Verhalten; Verschieben kann das Erscheinungsbild ändern.

## Module

Unter `addon/medieval_building_generator/`:

- `__init__.py`: Registrierung/Abmeldung, Object-PointerProperty; wiederholte Aufrufe sind abgesichert.
- `assets.py`: Quellprüfung, gezieltes Library-Appending, Interface-Validierung, Vorlagen-Cache, Hauskopie.
- `properties.py`: Dateipfad in AddonPreferences; PropertyGroup als **zustandslose UI-Brücke** zu Modifier-RNA.
- `operators.py`: Undo-fähiges Erstellen, verständliche Fehlermeldungen.
- `ui.py`: 3D-Viewport-Sidebar, Kategorie `Medieval Buildings`; kein Node-Editor erforderlich.
- Manifest und Lizenz: ZIP-Installation über Blenders Extension-System.

## Datenfluss und Isolation

1. Quelle muss eine vorhandene `.blend` mit `GenerateHouse` und `HouseOne` sein. Arbeiten direkt in dieser Quelldatei wird abgewiesen, um versehentliches Speichern über das Original zu vermeiden.
2. `bpy.data.libraries.load(path, link=False)` fordert ausschließlich `objects = ['HouseOne']` an. Blender löst die tatsächlich referenzierten IDs rekursiv auf. Keine Szene, kein Demo-Stadt-Collection-Import.
3. Die unverbundene HouseOne-Vorlage erhält einen Pfad-Marker und Fake User. Sie wird nicht in die aktive Szene gelinkt. Auch die Asset-Collections bleiben außerhalb der Szene; ihre Referenzen funktionieren dennoch für Geometry Nodes.
4. Pro Haus: `Object.copy()`, **`Mesh.copy()`**, eigener Modifier-Zustand. `Object`-Socket wird zwingend vom Vorlagenobjekt auf das neue Haus umgebunden. Gruppen und Originalmaterialien dürfen unverändert gemeinsam genutzt werden; Eingabefarben sind pro Haus gespeicherte Modifier-Werte, keine Änderungen an gemeinsamen Shadern.
5. Nur das neue Haus wird in die aktuelle Collection gelinkt, am 3D-Cursor platziert und aktiv ausgewählt. Rotation/Skalierung der funktionierenden Vorlage bleiben erhalten (hier Identität); keine Transform-Anwendung.
6. Bei fehlgeschlagenem Appending entfernt die Fehlerbehandlung ausschließlich neu hinzugekommene IDs. Bestehende Nutzer-Daten bleiben erhalten.

Cache: pro absolutem Quellpfad innerhalb der `.blend`. Eine zwischenzeitlich extern ersetzte Quelldatei wird nicht automatisch neu eingelesen; neue Szene oder anderer Quellpfad für einen Asset-Wechsel verwenden. Kein vollständiges Neuladen bei jedem Reglerzug.

## Blender-5.2-RNA und Live-Update

Namen und Typen werden über `modifier.node_group.interface.items_tree` ermittelt (`item_type == 'SOCKET'`, `in_out == 'INPUT'`). Der dort gelesene Identifier adressiert:

```python
item = ...  # exakter Name und validierter Typ
input_rna = getattr(modifier.properties.inputs, item.identifier)
input_rna.value = value
obj.update_tag(refresh={'OBJECT', 'DATA'})
```

**Keine** alten IDProperty-Zuweisungen wie `modifier['Input_2']`. Ein erster Integrationstest zeigte: bloße RNA-Zuweisung invalidiert hier die GN-Auswertung nicht zuverlässig. Deshalb schreiben die PropertyGroup-Setter den echten Eingang und taggen das betroffene Objekt. Der normale Blender-UI-Zyklus wertet es neu aus. Keine Handler-Schleife und kein globales Szenen-Rebuild.

Getter lesen jedes Mal den echten Modifier. Es gibt keine zweite, potenziell abweichende Parameterkopie. Nach Speichern/Laden oder Änderungen im nativen Modifier-Panel zeigt die Add-on-UI den tatsächlichen Zustand. Gespeichert werden die nativen Modifier-Eingaben und der Haus-Marker, nicht redundante UI-Werte.

| UI | Originalsocket | In dieser Quelle nachgewiesener Identifier |
|---|---|---|
| Seed | Seed | Socket_3 |
| Stockwerke | NumberFloor | Socket_4 |
| Dachkrümmung | RoofCurvature | Socket_5 |
| Dachfarbe | RoofColor | Socket_6 |
| Putzfarbe | PaintColor | Socket_7 |
| Balkenfarbe | **BeamCollor** | Socket_8 |
| Efeu | SpawnIVY | Socket_12 |
| High-Poly-Pflanzen | **High Polz Plants** | Socket_14 |
| intern: eigenes Objekt | Object | Socket_2 |

Die Tabelle ist Evidenz, **keine hart codierte Identifier-Zuordnung**. Stockwerke sind bewusst auf 1–8, Krümmung auf 0–3 begrenzt; das ist keine Freigabe beliebiger komplexer Grundrisse.

## Asset-Abhängigkeiten

Snapshot: `tests/addon/phase5/integration.json`. Nach dem ersten Erstellen befindet sich **genau ein** Objekt in der Szene. Die Datenbank enthält zusätzlich die unverbundene Vorlage und referenzierte Assets, darunter `Manager`, Steinobjekte, `GreenLeaves.037`, `HamisheBahar.125`, `Cube`, `Cube.001`, `Plane.009` sowie Collections `Set`, `Plants`, `Plants Low Poly`. Diese sind keine zusätzlich sichtbaren Häuser.

Die vorhandenen Gruppen umfassen u.a. `GenerateHouse`, `CreateDiagonalBeams`, `Generate Windows`, `WindowBeams`, `GetPositionBasedSeed`, `Switch On Roof Type` und Shader-Untergruppen. Originalmaterialien umfassen Dach, Stein, Putz, Balken, Glas und Pflanzen. `plantsTextureLowRes.png` liegt gepackt in der Zieldatei vor; neu geladene FILE-Bilder werden nötigenfalls gepackt.

Nach dem Speichern bleiben alle lokal angehängten Gruppen, Materialien, referenzierten Objekte/Collections und das Bild in der Ziel-`.blend`. Bestehende Häuser benötigen die Quelldatei beim Wiederöffnen nicht. **Zum Erstellen neuer Häuser wird der konfigurierte Quellpfad weiterhin validiert.** Der unabhängige Reload-Test prüft vorhandene Häuser mit absichtlich ungültiger Quellkonfiguration.

## Grundriss / Abmessungen – bewusst zurückgestellt

Die vermessene HouseOne-Eingabe besteht aus einem Quad mit vier individuellen Eckpunkten, X etwa −1,28…1,80, Y −2,97…2,88 und Z −0,03088…0. Sie ist weder exakt rechteckig noch eben oder exakt symmetrisch. Die bisherige technische Untersuchung bestätigt +X als Vorderseite und die originalen Symmetrie-/Transformationsannahmen.

Ein neues Rechteck und zwei Vertex-Abstandsregler sind prinzipiell möglich, aber die sichere Umsetzung inklusive First, Tür-/Fensterverteilung, Überhang und Detailabständen über verschiedene Größen wurde hier **nicht nachgewiesen**. Daher keine irreführenden Breite-/Tiefe-Regler und keine globale Objektskalierung als Ersatz. Die funktionierende Originaleingabe wird unabhängig kopiert. Manuelle Edit-Mode-Änderungen bleiben möglich, sind aber nicht Teil der MVP-Freigabe. Keine neue Grundriss-Engine.

## Testgrenzen

Integration prüft ausgewertetes direktes Mesh, Farbattribute sowie Instanzanzahl/-Transformationen. Das ist kein erneuter vollständiger Polygonbijektions-Audit wie Phase 4B. Die GUI-Materialvorschau ergänzt den Nachweis für das sichtbare Gesamthaus. Pflanzenschalter behalten ihre **originale, situationsabhängige** Bedeutung: High-Poly kann bei bestimmten Seeds/Positionen keinen sichtbaren Unterschied erzeugen; keine erfundene globale Pflanzen-Umschaltung.
