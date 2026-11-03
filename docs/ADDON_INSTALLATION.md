# Installation und Bedienung

## Voraussetzungen

- Getestet mit **Blender 5.2.2 LTS**. Manifest-Mindestversion 5.2.0; ältere Modifier-APIs werden nicht unterstützt.
- Originale IRCSS-Datei `GeometryNodesFrenchHous.blend` aus diesem Repository. Sie wird **nicht** im ZIP mitverteilt und nie vom Add-on gespeichert.
- Keine zusätzlichen Python-Pakete.

## ZIP installieren

Artefakt: [`tests/addon/phase5/medieval_building_generator-0.1.0.zip`](../tests/addon/phase5/medieval_building_generator-0.1.0.zip).

1. Blender → **Edit / Preferences → Get Extensions → Menü oben rechts → Install from Disk**.
2. ZIP auswählen, Installation und Aktivierung bestätigen. Nicht vorher entpacken.
3. Unter **Add-ons → Medieval Building Generator** den Eintrag aufklappen.
4. **IRCSS-Quelldatei** auf die originale `GeometryNodesFrenchHous.blend` setzen. Alternativ dasselbe Feld direkt im Gebäude-Panel verwenden. Für Neustarts Preferences speichern bzw. Auto-Save Preferences aktiviert lassen.
5. Eine **neue** Szene verwenden, nicht die Originalbibliothek selbst bearbeiten.

Bei Blender-Extensions mit Dateizugriffs-Rückfrage den Zugriff auf die ausgewählte lokale Asset-Bibliothek erlauben. Keine Internetverbindung oder externe Repository-Installation nötig.

## Praktischer Workflow

1. Im 3D-Viewport **N** drücken, Register **Medieval Buildings** öffnen.
2. Im **Object Mode** auf **+ Neues Haus erstellen** klicken.
3. Das Haus erscheint am **3D-Cursor**, wird aktiv und erhält einen eindeutigen Namen (`Medieval House`, `.001`, …).
4. Für Originalfarben **Material Preview** aktivieren; Solid View zeigt nicht alle prozeduralen Materialien. Bei Bedarf mit Numpad `.` auf das ausgewählte Haus fokussieren und das N-Panel am linken Rand breiter ziehen.
5. Seed, Stockwerke, Dachkrümmung, Dach-/Putz-/Balkenfarbe und beide Detail-Schalter bearbeiten. Änderungen wirken ohne Generate-Button live.
6. Weitere Häuser an einer anderen Cursorposition erstellen oder anschließend verschieben. **Verschieben darf wegen der originalen positionsabhängigen Seeds das Haus verändern.** Nicht denselben Seed an unterschiedlichen Orten als Identitätsgarantie verstehen.
7. Die eigene Szene unter einem **neuen** `.blend`-Namen speichern.

Objekte und Grundrissmeshes sind unabhängig; Gruppen und Shader werden unverändert geteilt. Nicht direkt gemeinsame Node-Gruppen oder Materialien verändern, wenn ausschließlich ein Haus geändert werden soll.

### Besonderheiten

- Nur aktive Add-on-Häuser zeigen Einstellungen. Ohne Auswahl oder bei anderen Objekten erscheint ein Hinweis.
- Der erste Klick lädt die Asset-Abhängigkeiten und kann länger dauern. Danach wird die lokale Vorlage wiederverwendet.
- Beide Pflanzenregler steuern die Originaleingänge. High-Poly ist kein garantierter sichtbarer Unterschied bei jedem Seed; im Kontrollzustand an der Originalposition wurde eine Geometrieänderung nachgewiesen.
- Keine Breite/Tiefe im MVP: begründete Einschränkung in [Architektur](ADDON_ARCHITECTURE.md).
- Nach **Deaktivieren und erneutem Aktivieren** bleiben Häuser und alle Modifier-Werte erhalten. Blender entfernt dabei die Add-on-Preferences; den Quellpfad für neue Häuser gegebenenfalls erneut auswählen. Bestehende Häuser lassen sich weiterhin bearbeiten.
- Ohne Quelldatei funktionieren gespeicherte Häuser weiter. Ein neues Haus verlangt eine gültige Quelle.
- Fehlende Datei, falsches Format, fehlende `GenerateHouse`-/`HouseOne`-Daten oder inkompatible Sockettypen werden verständlich gemeldet.

## Reproduzierbare technische Tests

Aus Repository-Wurzel; die folgenden Einstellungen bleiben ausschließlich unter `tests/addon/phase5/runtime/` (ignoriert). Vorhandene persönliche Blender-Preferences werden nicht verändert.

```bash
B=/snap/blender/current/blender
export BLENDER_USER_CONFIG="$PWD/tests/addon/phase5/runtime/config"
mkdir -p "$BLENDER_USER_CONFIG" tests/addon/phase5/runtime/extensions
"$B" --factory-startup --command extension build \
  --source-dir addon/medieval_building_generator --output-dir tests/addon/phase5
"$B" --factory-startup --command extension validate \
  tests/addon/phase5/medieval_building_generator-0.1.0.zip
# Einmalig für das isolierte Testprofil:
"$B" --factory-startup --command extension repo-add mbg_test --name 'MVP Test' \
  --directory "$PWD/tests/addon/phase5/runtime/extensions"
"$B" --command extension install-file -r mbg_test -e \
  "$PWD/tests/addon/phase5/medieval_building_generator-0.1.0.zip"
"$B" -b -t 4 -P scripts/test_addon_mvp.py
"$B" -b -t 4 -P scripts/test_addon_reload.py
"$B" -b -t 4 -P scripts/test_addon_errors.py
```

GUI-Testprofil starten:

```bash
"$B" --enable-event-simulate -t 4 -W -P scripts/addon_gui_session.py
```

Die Sitzung öffnet eine echte Blender-Oberfläche mit Materialvorschau, leerer Szene und konfigurierter Quelle. Splash schließen, N-Panel-Kategorie **Medieval Buildings** öffnen. Manuell testen oder den auf **2560×1440** und die dokumentierte Standardaufteilung abgestimmten Replay starten: Datei `tests/addon/phase5/runtime/gui_command.py` mit folgendem Inhalt erstellen (wird vom **Testskript**, nicht vom Add-on, abgearbeitet und gelöscht):

```python
exec(compile((ROOT/'scripts/addon_gui_acceptance.py').read_text(),
             'scripts/addon_gui_acceptance.py', 'exec'), {})
```

Der Replay betätigt echte GUI-Felder per Blenders Event-Simulation, speichert echte Fenster-Screenshots und `gui_actions.json`. Er ersetzt keine plattformübergreifende UI-Automation; bei anderer Fenstergröße die Schritte aus [Ergebnis/Testprotokoll](PHASE5_RESULT.md) manuell ausführen. Die vorbereitete Inbox führt bewusst Testcode aus und gehört **nicht** zum installierten Add-on.

Runtime-`.blend`-Dateien werden nicht versioniert; Tests erzeugen sie neu. Der Importtest und der Reload-Test müssen nacheinander laufen. Bestehende Export-/Bakingtests bleiben unverändert.
