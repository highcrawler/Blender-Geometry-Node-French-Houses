# Phase 6 – Selected House GLB Export

**RESULT: PASS** – für den geprüften Selected-House-Workflow mit Blender **5.2.2 LTS**, Godot **4.7**, Linux.

- Branch: `feature/blender-addon-export-06`.
- Tatsächliche Basis: Phase-5-Commit **`a20ce4a`**; kein neuerer Entwicklungscommit vorhanden.
- Add-on-Version: **0.2.0**.
- Abschlusscommit: Commit dieses Berichts und der Implementierung auf dem Feature-Branch; konkrete ID im Git-Verlauf und Abschlussprotokoll.
- Push ausschließlich nach `origin` / `highcrawler/Blender-Geometry-Node-French-Houses`. Kein Merge nach `main`, kein Push zu IRCSS/upstream.

## Installierbares ZIP und Bedienung

[`tests/addon/phase6/medieval_building_generator-0.2.0.zip`](../tests/addon/phase6/medieval_building_generator-0.2.0.zip), **12.405 Bytes**.

SHA-256: `ccd0f56e911b836fdfdb84f1e30af644d6648217a755f667b2febbf8df5143ec`.

Blender → Preferences → Get Extensions → Install from Disk → ZIP installieren/aktivieren. Ein Add-on-Haus aktiv auswählen → N-Panel **Medieval Buildings → Export → Export Selected House (.glb)** → Standard-Dateidialog → Speicherort bestätigen. Existierende Datei verlangt zusätzlich **GLB überschreiben?**. Abbrechen verändert nichts.

Die Quellbibliothek muss zum Export gespeicherter Häuser nicht erneut geladen werden. Dateinamenvorschlag wird aus dem aktuellen Objektnamen bereinigt: `Renamed / Castle : 03` → `Renamed_Castle_03.glb`.

## Vorbereitung und Sicherheit

Zu Beginn: Branch `feature/blender-addon-mvp-05`, HEAD `a20ce4a`, Phase 5 visuell freigegeben. Weiterhin vorhanden waren die ältere lokale Root-`.gitignore`-Änderung und unversionierte Phase-2-/HouseTWo-/Phase-5-Exportexperimente, Godot-Dateien und `tests/pipeline/`. Diese bleiben unverändert und außerhalb dieses Commits.

Gelesen wurden Phase-5-Ergebnis/Architektur, Phase-4B-Ergebnis/Geometrie-/Koordinatenanalyse sowie vorhandene Phase-3-Konvertierung und Phase-4B-Realisierungs-/Baking-Skripte. Die neue Funktion verwendet deren Erkenntnisse, aber **keine fest codierten HouseOne-Dreieckszahlen oder globalen Demo-Objektsammlungen**.

Originaldatei vor/nach den Tests:

```text
GeometryNodesFrenchHous.blend
SHA-256 f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5
```

Keine Original-Nodes, Shader oder bestehenden Export-/Bakingtests geändert. Die neue Realize-Gruppe existiert ausschließlich temporär. Keine Änderungen an externen Spielprojekten oder `main`.

## Abnahme

| Kriterium | Tatsächlicher Nachweis | Ergebnis |
|---|---|---|
| Installierbare Extension | offizieller Build/ZIP-Validator, Installation in isoliertes Testprofil; ZIP-Inhalt bytegleich zum Add-on-Quellcode | PASS |
| Exportbutton / Dateidialog | echte Blender-GUI, Panel-Klick, Standard-Dateibrowser, bereinigter Vorschlag, tatsächlicher Export | PASS |
| Ausschließlich aktives Haus | fünf unterschiedliche Häuser plus Würfel alle markiert, nur Haus 3 aktiv; danach Haus 1 und 5 separat exportiert | PASS |
| Vollständige Geometrie | gefilterte Eigentümerinstanzen + direkte Geometrie; bijektiver Polygonvergleich und unabhängiger GLB-Binärpositionsvergleich | PASS |
| Boden-Pivot / kein Weltversatz | Eingabegrundriss, danach eingefrorenes Mesh verschoben; GLB-Meshnode Identität; Godot-Körperunterkante Y=0 | PASS |
| Originalszene unverändert | vor/nach Erfolg und Fehlern: Objekte, Matrizen, Meshes, Modifierwerte, Auswahl, Assets, Gruppenreferenzen, Shader, Datenblockinventar identisch | PASS |
| Speicherung / Umbenennen | eigener Blender-Prozess, gespeicherte Bibliothek geladen, umbenanntes Haus exportiert, GLB hashidentisch; Quellkonfiguration absichtlich ungültig | PASS |
| Fehler / Abbruch | fehlender Zielordner, ungültiges/kein Objekt, Edit Mode, falsche Object-Selbstreferenz, Konflikt, Teilfehler beim Gruppenaufbau, Geometrie-/Schreibfehler, Dialogabbruch | PASS |
| Explizites Überschreiben | Sentinel-Datei bleibt vor Bestätigung und nach Cancel erhalten; erst Return auf Bestätigung ersetzt sie mit gültiger GLB | PASS |
| Godot | zwei Varianten normal importiert, echte grafische Sitzung, zwei Screenshots, getrennte Platzierung und Pivot-/Geometrieassertionen | PASS |

Die gesonderte Prüfung einer frisch geladenen Datei meldet auch `bpy.data.is_dirty: false → false` über den Export. Der gespeicherte `.blend`-Dateihash bleibt in GUI und separatem Prozess unverändert.

### Exportzahlen

| Testvariante | Eigene sichtbare Instanzblätter | Dreiecke | GLB-Bytes |
|---|---:|---:|---:|
| A – einzelnes Haus, Seed 83 / 3 Stockwerke / geänderte Farbe | 1.761 | 335.775 | 14.311.676 |
| B – Haus 3, Seed 17, Weltposition (40,15,0) | 1.480 | 106.735 | 5.137.440 |
| B – Haus 1, Seed 29, Weltposition (0,0,0) | 3.056 | 187.021 | 8.851.672 |
| B – Haus 5, Seed 102, Weltposition (15,−25,0) | 2.284 | 378.786 | 16.230.960 |
| Transformkontrolle Haus 2, Yaw / nichtuniform / gespiegelt | 3.067 | 338.825 | 15.175.728 |
| Wiederholung Haus 3 / nach Reload | jeweils 1.480 | jeweils 106.735 | jeweils 5.137.440 |

Je GLB ein Mesh und zwölf verwendete Material-Primitives. Haus-3-/Haus-5-Referenzen werden unter `tests/addon/phase6/` mitversioniert; weitere Kontroll-GLBs erzeugen die Tests reproduzierbar, bleiben aber zur Vermeidung doppelter großer Artefakte ignoriert.

**Warum nicht stets 154.602 Dreiecke wie Phase 4B?** Jener Wert galt für das originale HouseOne an dessen gespeicherter Position. Neu erzeugte Häuser besitzen andere Seeds, Positionen und Geschosse. IRCSS verwendet positionsabhängige Zufallslogik. Deshalb erfolgt ein dynamischer Soll-/Ist-Vergleich pro Haus statt der falschen Annahme einer universellen Hausgeometrie.

### Auswahl- und Geometrie-Beweis

Die Zugehörigkeit wird durch **`parent.original == active_house`** nachgewiesen, nicht durch Mesh-/Assetnamen. Das neue Haus trägt den Phase-5-Marker; `Object` muss auf dieses Haus selbst zeigen. Die zugehörigen Persistent-IDs stehen in `*_ownership.json`.

Haus 3: **61.309 Polygone**, Haus 1: **121.459**, Haus 5: **305.660** bijektiv mit ihren jeweiligen Originaloberflächen abgeglichen, **0 fehlend/zusätzlich**. Maximale Eckfehler unter **4e−6 BU**. Zusätzlich werden alle GLB-Positionen beidseitig und Materialdreieckszahlen unabhängig geprüft. Das schließt die bloße Behauptung „Exporter fertig, also vollständig“ aus.

### Pivot-Beweis

Primärer lokaler Pivot: **(0,2602572; −0,0453312; −0,03087646)** aus dem tatsächlichen Eingabequad. Zuerst Auswertung an Originalposition, dann Transformation des gefrorenen Meshes um diesen Weltpivot. Keine komplette Gebäude-Bounding-Box mit Dach/Efeu.

Godot Haus 3 bei (0,0,0), Haus 5 bei (12,0,−2), beide ohne interne Translation und mit Skalierung (1,1,1). Tragende Wände beginnen exakt bei **Y=0**. Details, Transformationen, Rückfallregel und Grenzfälle: [Auswahl/Pivot](PHASE6_SELECTION_AND_PIVOT.md).

## Grafisches Testprotokoll

Echte Blender-GUI 2560×1440; Buttons und Bestätigungen über `Window.event_simulate`. Nur die Zielverzeichnis-Auswahl im Browser wird vom Testfixture über die Filebrowser-API gesetzt. Das ist ein reales Dateidialogfenster, kein Mockup.

1. [Panel mit neuem Exportbereich, aktives umbenanntes Haus, weitere Objekte markiert](../tests/addon/phase6/blender_export_panel.png).
2. [Standard-Dateidialog mit automatisch bereinigtem Namen](../tests/addon/phase6/blender_file_dialog.png).
3. Cancel betätigt: keine Datei und keine Szenenänderung.
4. [Ziel gewählt](../tests/addon/phase6/blender_file_destination.png), Export betätigt: GLB hashgleich mit dem unabhängig geprüften Haus 3; [Viewport nach Export](../tests/addon/phase6/blender_after_export.png).
5. [Explizites Überschreibfenster](../tests/addon/phase6/blender_overwrite_confirmation.png): vor Bestätigung bleibt Sentinel erhalten. Escape lässt ihn unverändert. Erneuter Dialog, Return auf **Überschreiben**: gültige GLB.
6. [Alle fünf ursprünglichen Häuser weiterhin in der Szene](../tests/addon/phase6/blender_five_houses_unchanged.png). Zustandsvergleich bestätigt unveränderte Platzierung/Parameter/Auswahl.
7. [Zwei eigenständige Häuser in Godot](../tests/addon/phase6/godot_two_houses.png), [nur Haus 5 verschoben](../tests/addon/phase6/godot_house5_moved.png).

Während der Entwicklung zeigte sich, dass `ExportHelper.check_existing` allein keine explizite Zustimmung garantiert. Das wurde **vor der finalen Abnahme** durch den eigenen Bestätigungsdialog korrigiert. Im finalen Replay werden Cancel, unveränderter Sentinel und bestätigtes Ersetzen tatsächlich assertiert.

## Materialstatus und Grenzen

**Erfüllt:** Dach, Balken, Putz, Stein und zusätzliche Instanzflächen besitzen sinnvolle unterscheidbare PBR-Farben. Die drei Hausfarben entsprechen den wirklichen Modifier-Eingängen und wurden gegen GLB-Faktoren geprüft. Bekannte Pflanzenmaterialien sind nicht versehentlich weiße Principled-Defaults. Keine externen Texturabhängigkeiten und keine benutzten unbekannten Materialslots in den Referenzvarianten.

**Nicht behauptet:** vollständige prozedurale Shader-Treue, Putz-Baking, Relief/Normalmaps, echtes Glas oder originalgetreue Blütenfarben. Glas ist deckend, Pflanzenfarben eine bewusste Palette. Unbekannte benutzte Materialien erzeugen eine dokumentierte braune Annäherung und Warnung.

Weitere Grenzen:

- Fünf Häuser sind **kein Lasttest für 50**; keine FPS-/Speicher-/Laufzeitgarantie.
- Aufrechte Originalhäuser bleiben aufrecht; absichtliche Neigung wird nicht automatisch entfernt.
- Der unterstützende Pivot-Fallback ist mit dem bekannten IRCSS-Körper kontrollgeprüft, nicht für beliebige neue Grundriss-/Node-Engines freigegeben. Unklarer Pivot oder abweichende Instanzrealisierung wird sicher abgebrochen.
- Export erwartet einen sichtbaren gültigen Hauskandidaten im Object Mode und ein bestehendes beschreibbares Zielverzeichnis. Atomarer No-Clobber-Commit ist auf dem getesteten lokalen Linux-Dateisystem nachgewiesen, nicht auf jedem Netzlaufwerk.
- Beim normalen Blender-Speichern/Laden verschwinden echte Zero-User-Datenblöcke. `reload.json` dokumentiert die erwartete Bereinigung unbenutzter `Manager`-/`Cube`-/`Dots Stroke`-Daten. Keine vom Exporter verursachte Löschung; alle lebenden Haus-/Asset-/Shaderzustände bleiben gleich.
- Keine neuen Batch-Export-, LOD-, Collision-, Baking-, Optimierungs- oder Preset-Funktionen.

## Antwort auf die Bibliotheksfrage

**JA.** Eine Blender-Datei kann 50 verwaltete Häuser enthalten; der Export verwendet ausschließlich das aktive markierte Haus, dessen eigene GN-Auswertung und zugehörige Instanzvorkommen, danach ein isoliertes Ein-Objekt-Export-Scene. Es existiert keine feste Begrenzung auf fünf und keine Auswahl aller markierten Gebäude. Die Quellweltposition wird nur aus dem eingefrorenen Exportmesh entfernt; der Bestand bleibt stehen.

**Nachgewiesen ist die Auswahl-/Geometrie-/Pivot-Korrektheit mit fünf Häusern, nicht die Lasttauglichkeit einer konkret mit 50 komplexen Häusern bestückten Datei.** Wie viele solcher Häuser flüssig auswertbar sind, hängt von Instanzzahlen, Parametern und Hardware ab.

## Reproduktion und Artefakte

Alle neuen Blender-Testartefakte: [`tests/addon/phase6/`](../tests/addon/phase6/), Runtime-Dateien und doppelte Kontroll-GLBs ignoriert. `integration.json` enthält den vollständigen Zustandsvergleich, Materialpolicy und geometrische Messwerte; `reload.json`, `guards.json`, `gui_result.json`, `godot_measurements.json` die unabhängigen Folgeprüfungen. Die `.log`-Dateien protokollieren tatsächliche Prozesse.

```bash
B=/snap/blender/current/blender
export BLENDER_USER_CONFIG="$PWD/tests/addon/phase6/runtime/config"
mkdir -p "$BLENDER_USER_CONFIG" tests/addon/phase6/runtime/extensions
"$B" --factory-startup --command extension build \
  --source-dir addon/medieval_building_generator --output-dir tests/addon/phase6
"$B" --factory-startup --command extension validate \
  tests/addon/phase6/medieval_building_generator-0.2.0.zip
# Einmalig für das isolierte Testprofil:
"$B" --factory-startup --command extension repo-add mbg_export_test --name 'Export MVP Test' \
  --directory "$PWD/tests/addon/phase6/runtime/extensions"
"$B" --command extension install-file -r mbg_export_test -e \
  "$PWD/tests/addon/phase6/medieval_building_generator-0.2.0.zip"
"$B" -b -t 4 -P scripts/test_addon_export06.py
"$B" -b -t 4 -P scripts/test_addon_export06_reload.py
"$B" -b -t 4 -P scripts/test_addon_export06_guards.py
"$B" tests/addon/phase6/runtime/library.blend --enable-event-simulate -t 4 -W \
  -P scripts/addon_export06_gui.py
```

In der GUI-Sitzung `tests/addon/phase6/runtime/gui_command.py` mit folgendem Testinhalt schreiben:

```python
exec(compile((ROOT/'scripts/addon_export06_gui_replay.py').read_text(), 'gui_replay', 'exec'), globals())
```

Replay benötigt die dokumentierte Fenstergröße/Aufteilung und noch nicht vorhandene `Renamed_Castle_03.glb` in Ausgabe- und Runtime-Verzeichnis; vorhandene eigene Dateien **nicht** unkontrolliert löschen, stattdessen separates Testverzeichnis oder manuelle Schritte verwenden. Diese Code-Inbox ist ausschließlich Testinfrastruktur, kein Bestandteil des installierten Add-ons.

Godot-Kommandos und Import-Testszene: [Godot-Verifikation](PHASE6_GODOT_VALIDATION.md). Implementierungsdetails: [Exportarchitektur](PHASE6_EXPORT_ARCHITECTURE.md).
