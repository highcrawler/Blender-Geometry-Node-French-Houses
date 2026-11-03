# Phase 5 – Medieval Building Generator Add-on MVP

**RESULT: PASS** – für den dokumentierten HouseOne-basierten Bedienworkflow mit Blender **5.2.2 LTS**. Keine Freigabe beliebiger Grundrisse oder zusätzlicher Exportfunktionen.

Branch: `feature/blender-addon-mvp-05`, Basis `eee6dac` (abgeschlossene Phase 4B). Kein Merge nach `main`. Push-Ziel ausschließlich `origin` = `highcrawler/Blender-Geometry-Node-French-Houses`, nicht `upstream` = IRCSS.

## Vorbereitung und Bestandsschutz

Beim Start war `experiment/house-two-validation-05` ausgecheckt, ebenfalls auf `eee6dac`, ohne neuere Commits. Vorhanden waren eine lokale `.gitignore`-Änderung sowie unversionierte HouseTWo-/Phase-5-Exportdokumente, Skripte, GLB/PNG, Godot-Dateien und `tests/pipeline/`. Außerdem ältere unversionierte Phase-2-Probes. Alles blieb unverändert und außerhalb dieses Commits. Der neue Branch basiert somit direkt auf Phase 4B, nicht auf unvollständigen Exportarbeiten.

Die bestehenden Export-/Baking-Skripte und Tests wurden nicht geändert. Erkenntnisse aus Phase 4B werden berücksichtigt: vollständige GN-Instanzen bleiben erhalten, keine voreilige Realisierung, positionsabhängige Seeds nicht als Fehler kaschiert.

Originaldatei vor/nach allen Tests:

```text
GeometryNodesFrenchHous.blend
SHA-256 f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5
```

Die Quelldatei wurde nur gelesen, auch im Schutztest nie gespeichert. Keine originalen Nodes, Shader oder Eingabegeometrien verändert.

## Lieferung

- Installierbare Extension: [`medieval_building_generator-0.1.0.zip`](../tests/addon/phase5/medieval_building_generator-0.1.0.zip), 6.158 Bytes.
- ZIP SHA-256: `95d46ce1ba43b6c92a4d3c8b665cca6e5c3f8e3e8e71b68c0c9865ecbf2872ca`.
- Quellcode: [`addon/medieval_building_generator/`](../addon/medieval_building_generator/).
- [Installation / Bedienung / Reproduktion](ADDON_INSTALLATION.md).
- [Architektur / RNA / Abhängigkeiten / Grundrissgrenze](ADDON_ARCHITECTURE.md).

Die originale IRCSS-`.blend` ist bewusst **nicht im ZIP** enthalten. Einmalig Quelle in den Add-on-Preferences oder im Panel auswählen.

## Abnahmekriterien

| Test | Ergebnis / Nachweis |
|---|---|
| A – ZIP installieren und aktivieren | PASS. Offizieller Extension-Build und ZIP-Validator; Installation mit `extension install-file -r mbg_test -e` in isoliertes Blender-Profil. Panel in echter GUI sichtbar. |
| B – Leere Szene → neues Haus | PASS. Im Integrationstest genau **ein** Szenenobjekt; in der GUI per Panel-Button erstellt, automatisch aktiv. 31.736 direkte Meshvertices plus 3.056 zugehörige Instanzen am Ursprung. |
| C – Alle acht Eingänge | PASS. Echte UI-Interaktionen plus ausgewertete Mesh-/Farb-/Instanzdaten, siehe Tabellen unten. |
| D – Drei unabhängige Häuser | PASS. Separate Meshes/Modifierwerte; nur Haus 2 Seed/Farbe ändern, Haus 1 und 3 identische Auswertung. Zusätzlich echter GUI-Seedvergleich 17→99 nur an Haus 2. Vorlage unverändert. |
| E – Speichern / anderer Prozess / Wiederöffnen | PASS. Drei Häuser, Parameter und Auswertung nach Laden identisch. Ungültiger konfigurierter Quellpfad stört vorhandene Häuser nicht. Re-Registrierung und anschließende Live-Änderung funktionieren. |
| F – Fehler / Registrierung | PASS. Fehlende Konfiguration/Datei, falscher Dateityp, falsche `.blend` ohne Gruppe, beschädigte Datei, offene Originalbibliothek: verständliche Fehler, keine neuen Objekte. Keine/fremde Auswahl in echter GUI. Mehrfaches register/unregister sowie echtes Disable/Enable geprüft. |
| GUI-Abnahme | PASS. Echte Blender-Fensterscreenshots, Material Preview, tatsächliche GUI-Events; kein Headless-Render als GUI-Ersatz. |
| Originalgenerator | PASS. SHA unverändert, lokal angehängte Gruppen nicht umgebaut. |

### Headless-Messungen der tatsächlichen Änderungen

Ein Eingang nach dem anderen, jeweils Ausgangszustand wiederhergestellt. Ursprung, Seed 29, sofern nicht anders angegeben.

| Eingang | Änderung | Direkte Geometrie / Instanzen |
|---|---|---|
| Seed | 29→83 | Vertices 31.736→29.477; Instanzen 3.056→1.517 |
| NumberFloor | 2→3 | Vertices 31.736→32.088; Instanzen 3.056→3.297 |
| RoofCurvature | 1,66→0,5 | Vertices 31.736→30.872, zusätzlich Positionshash geändert |
| RoofColor | Rot→Blau | Ausgewertetes `RoofColor`-Attribut geändert; keine Geometrieänderung erforderlich |
| PaintColor | Weiß→Braun | Ausgewertetes `PaintColor`-Attribut geändert |
| BeamCollor | Original→Dunkelgrün | Ausgewertetes `BeamColor`-Attribut geändert |
| SpawnIVY | true→false | Instanzen 3.056→525; direktes Mesh gleich |
| High Polz Plants | true→false | **Originalposition von HouseOne**, Seed 29: Vertices 27.919→27.827, Faces 20.003→19.927 |

**Wichtige ehrliche Grenze:** High-Poly zeigte am Ursprung bei diesem Seed keine Änderung. Der Kontrolltest an der Originalposition weist die originale bedingte Wirkung nach. Auch in der GUI verschwindet damit nicht pauschal jeder Blumenkasten. Keine eigene Pflanzenlogik entwickelt und keine behauptete allgemeine Polygonersparnis.

Die Farbattribute wurden nicht lediglich als Modifier-Eingabewerte geprüft; sie stammen aus der ausgewerteten Geometrie. Die Originalshader zeigen die zugehörigen Farben in den GUI-Bildern sichtbar an. Der Integrationstest ist kein neuer vollständiger Phase-4B-Polygonbijektionsnachweis.

## Echte GUI-Abnahme und Testprotokoll

Echte grafische Blender-5.2.2-Sitzung auf dem vorhandenen Desktop, Fenster 2560×1440. Testprofil vollständig innerhalb des Repositorys. Quelle/Materialvorschau/Ansicht wurden durch `addon_gui_session.py` vorbereitet. Die eigentlichen Bedienelemente wurden mittels **`Window.event_simulate`** angeklickt bzw. per Tastatur editiert, einschließlich Farbwähler-Hexfeldern. Screenshots stammen von `bpy.ops.screen.screenshot`, nicht von gerenderten oder montierten UI-Nachbildungen.

Replay: [`scripts/addon_gui_acceptance.py`](../scripts/addon_gui_acceptance.py). Aufzeichnung: [`gui_actions.json`](../tests/addon/phase5/gui_actions.json), Abschlussassertionen: [`gui_result.json`](../tests/addon/phase5/gui_result.json). Der Replay ist fenstergrößenabhängig, keine allgemeine GUI-Testbibliothek.

| Tatsächlich betätigtes Steuerelement | Sichtbares Ergebnis / Bild |
|---|---|
| Kategorie `Medieval Buildings`, leere Szene | [Panel ohne Haus](../tests/addon/phase5/gui_empty.png) |
| `+ Neues Haus erstellen` | [Haus mit aktiven Einstellungen, Seed 29](../tests/addon/phase5/gui_house_seed29.png) |
| Seed-Feld 29→83 | [Dasselbe Haus: andere Gauben, Schornstein, Fachwerk, Blumenkästen](../tests/addon/phase5/gui_house_seed83.png) |
| Stockwerke 2→3 | [Zusätzliches Geschoss / veränderte Höhe](../tests/addon/phase5/gui_floors3.png) |
| Dachkrümmung 1,66→0,5 | [Veränderte Dachsilhouette](../tests/addon/phase5/gui_curvature05.png) |
| Dachfarbe, Farbwähler-Hex `2468BE` | [Blaues Dach](../tests/addon/phase5/gui_roof_blue.png) |
| Putzfarbe, Hex `C99A52` | [Ockerfarbener Putz](../tests/addon/phase5/gui_paint_ochre.png) |
| Balkenfarbe, Hex `283A24` | [Dunkelgrünes Fachwerk](../tests/addon/phase5/gui_beams_green.png) |
| Efeu-Checkbox aus | [Ranken am Sockel entfernt](../tests/addon/phase5/gui_ivy_off.png) |
| High-Poly-Checkbox aus | [Schalterzustand; kein behaupteter deutlicher Effekt in diesem GUI-Zustand](../tests/addon/phase5/gui_plants_off.png) |
| Zwei weitere Klicks auf Neues Haus, Seeds 17 und 56 | [Drei getrennte Häuser](../tests/addon/phase5/gui_three_houses.png); Cursorpositionen vorher per Testsetup auf X=11/22 gesetzt |
| Haus 2 im Outliner auswählen, Seed 17→99 | [Nur mittleres Haus verändert](../tests/addon/phase5/gui_house2_changed.png) |
| Disable/Enable des installierten Add-ons per Blender-API | [Panel und alle Hauswerte wieder vorhanden](../tests/addon/phase5/gui_reenabled.png) |
| Button bei leerer Quelle | [Kontrollierter Fehlerfall](../tests/addon/phase5/gui_missing_source.png), keine weitere Hauserstellung |
| Fremdes Objekt / keine Auswahl | [Fremdes Objekt](../tests/addon/phase5/gui_foreign_selection.png), [keine Auswahl](../tests/addon/phase5/gui_no_selection.png): Hinweis statt fehlerhafter Hausregler |

Nach Disable/Enable ist die Quelle in Blender-AddonPreferences zurückgesetzt; für weitere neue Häuser erneut auswählen. Die Parameter bleiben in den Modifiers gespeichert und funktionieren sofort weiter. Das ist dokumentiert, nicht als verlorener Hauszustand bewertet.

## Testdateien

Unter [`tests/addon/phase5/`](../tests/addon/phase5/):

- `probe.json`, `probe.log`: read-only Originalobjekt, Transform, vier Grundrisspunkte, Socket-RNA-Werte.
- `build.log`, `validate.log`, `install.log`: offizielles Extension-Artefakt und Installation.
- `integration.json`, `integration.log`: echte Auswertungen, Varianten, Isolation, Vorlage, Asset-Inventar, Fehler und Registrierungszyklen.
- `reload.json`, `reload.log`: unabhängiger Prozess mit identischer gespeicherter Auswertung und neuer funktionierender Änderung.
- `errors.json`, `errors.log`: echte Operatorfehler inklusive Originaldatei-Schutz.
- `gui_actions.json`, `gui_result.json`, `gui_*.png`, `gui.log`: grafische Sitzung und protokollierte Eingaben. `gui.log` enthält auch einen frühen, anschließend behobenen Event-Testharness-Fehler (fehlendes `value`-Argument), keinen Add-on-Fehler; der finale Replay verwendet vollständig spezifizierte Events und Abschlussassertionen.
- `runtime/`: ignorierte Testpreferences, installierte ZIP-Kopie, gespeicherte Test-`.blend` und Inbox. Werden bei Reproduktion erzeugt, nicht mitcommittet.

## Nicht umgesetzt / verbleibende Grenzen

- Breite/Tiefe: zurückgestellt. HouseOne ist ein leicht unregelmäßiges, nicht ebenes Quad. Eine zuverlässig getestete rechteckige Umparametrisierung mit korrekter X-Symmetrie, +X-Front und Dach-/Fassadendetails fehlt; keine globale Skalierung als Täuschung.
- Keine Stil-Presets, GLB-/Godot-Buttons, Baking, neuen Shader, LOD, Optimierungen, Dachgeneratoren oder Dorf-/Stadtgenerierung.
- Keine Kompatibilitätsbehauptung für andere Blender-Versionen oder beliebige geänderte Assetbibliotheken.
- Ein gemeinsamer Asset-Cache pro Quellpfad; externe Änderungen derselben Datei werden innerhalb der geöffneten Szene nicht automatisch nachgeladen.
- Viele Häuser und sehr große Parameterwerte können teuer werden. Kein Performance-/FPS-Versprechen.

**Praktisches Ergebnis:** Quelle einmal konfigurieren → Neues Haus → wenige verständliche Live-Regler → weiteres, unabhängiges Haus. Die bestehende IRCSS-Engine bleibt die technische Grundlage.
