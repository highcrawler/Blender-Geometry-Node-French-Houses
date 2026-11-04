# Phase 7 – Presets und Bedienung

## Entscheidungsrahmen

Nur ein begrenztes, zentriertes Vierpunkt-Rechteck wird als neuer Grundriss unterstützt. Die Fassade liegt entlang lokal Y, die Tiefe entlang lokal X, die Tür zeigt nach lokal +X; siehe [Grundriss-Audit](PHASE7_FOOTPRINT_AUDIT.md). **Objektskalierung wird nicht zum Einstellen der Maße verwendet.** Das unveränderte IRCSS-`GenerateHouse` baut aus dem lokalen Eingabequad die eigentliche Geometrie.

| Preset | lokale Breite Y | lokale Tiefe X | Verhältnis B/T | Wirkung |
|---|---:|---:|---:|---|
| Compact | 4,0 m | 3,2 m | 1,25 | kleines, gedrungenes Haus |
| Narrow | 3,2 m | 5,0 m | 0,64 | schmale Straßenfront und tiefer Baukörper |
| Wide | 7,0 m | 4,0 m | 1,75 | breite Front mit weiteren Fenster-/Fachwerkplätzen |
| Custom | 3,2–7,0 m | 3,0–5,0 m | variabel | einzeln begrenzte, unabhängige Eingabemaße |

Alle Werte entsprechen Blender-Lokaleinheiten; bei Scale `(1,1,1)` entspricht 1 BU einem Meter. Die Zahlen sind Maße der **Eingabegrundfläche**, nicht des Daches mit Überstand. Andere Werte können per manueller Meshänderung erzeugt werden, sind aber nicht für die Regler freigegeben. Geänderte Maße setzen den Presetstatus auf **Custom**; erst die bewusste Presetauswahl setzt die beiden Maße zurück. Der bestehende Seed, Stockwerke, Dachkrümmung, Farben und Detailflags bleiben dabei unabhängig.

## Installieren und bedienen

ZIP: [`tests/addon/phase7/medieval_building_generator-0.3.0.zip`](../tests/addon/phase7/medieval_building_generator-0.3.0.zip). Unter Blender 5.2: *Edit → Preferences → Get Extensions → Install from Disk*, ZIP wählen und Extension aktivieren. In den Extension-Einstellungen den Pfad auf die **unveränderte** `GeometryNodesFrenchHous.blend` setzen. Nicht deren Inhalt bearbeiten. Im 3D-Viewport mit `N` → **Medieval Buildings** → „Neues Haus erstellen“, dann im ausgewählten Haus die Box „Building Shape“ verwenden. Dort Preset auswählen oder „Hausbreite (m)“ und „Haustiefe (m)“ separat ändern. Ein neu erzeugtes Haus startet mit Compact. Der GLB-Export bleibt in der gleichen Seitenleiste und benötigt ein gültiges ausgewähltes Haus.

Bestehende 0.2-Häuser bleiben **ohne Schema** und mit unveränderten Eingabevertices auch nach Laden und Add-on-Registrierung erhalten; die neuen Maße sind für sie deaktiviert. „Rechteck-Grundriss aktivieren“ öffnet einen Bestätigungsdialog und legt **nur nach ausdrücklicher Bestätigung** ein neues, eigenes Quad-Mesh für dieses Haus an. Das alte Mesh bleibt erhalten; andere Nutzer dieses Meshes und andere Häuser bleiben unverändert. Abbrechen ändert nichts. Die Konvertierung ersetzt einen eventuell schiefen individuellen Altgrundriss durch ein zentriertes Rechteck – deshalb niemals stillschweigend. Der bisherige GLB-Export alter Häuser funktioniert ohne Konvertierung.

Bei Shift-D und Alt-D wird die eigenständige Regleränderung abgesichert: ein geteiltes Alt-D-Eingabemesh wird vor der Änderung kopiert. Manuelle Edit-Mode-Änderungen an einem bewusst geteilten Alt-D-Mesh sind weiterhin normale Blender-Operationen und können beide Objekte betreffen. Die Regler gelten nicht für ein ungültiges Haus, Edit Mode oder eine manuell vom erwarteten Rechteck abweichende Eingabe. Rotation und vorhandene Objektskalierung werden beim Verstellen nicht zurückgesetzt; nichtunitäre Objektskalierung wirkt **zusätzlich** auf die lokalen Maße.

## Vergleich und überprüfte Gestalt

Für den Dreiervergleich sind Seed 29, zwei Stockwerke, Krümmung 1,66 und dieselben Farben gewählt. Die Hausposition beeinflusst im Originalgraph zusätzliche Zufalls-IDs, weshalb sich Dachdetails auch ohne Presetwechsel unterscheiden können. Die drei sichtbaren Gebäude unterscheiden sich aber zusätzlich in ihren **gemessenen** Bodenbreiten und -tiefen. Frontbilder: [Blender](../tests/addon/phase7/blender_three_presets.png), [Godot](../tests/addon/phase7/godot_three_fronts.png); [Blender vor](../tests/addon/phase7/blender_width_before.png) und [nach](../tests/addon/phase7/blender_width_after.png) der live eingegebenen Breite 4,4 m.

Sowohl 0.2-Kontrollauswertungen als auch 0.3-Exporte und Godot bestätigen Hauskörper, Fenster und Dach. Typische Einschränkung des unveränderten Generators: Der breite Bau kann sehr viele Steine und weitere Instanzen erzeugen; `Wide` enthält 181.248 Dreiecke gegenüber 86.975 bei `Compact`. Die Presets sind eine erprobte begrenzte Auswahl, keine Freigabe für beliebige Architektur oder garantiert manifold Meshes.
