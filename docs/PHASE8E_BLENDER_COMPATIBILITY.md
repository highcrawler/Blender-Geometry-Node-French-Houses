# Phase 8E – Blender-5.2.2-Kompatibilitätsprotokoll (Nachtrag nach Benutzerdatei)

**Status: PARTIAL – Showcase lädt; Generator fehlt.** Die benutzerbereitgestellte `Blender 4 Hay Roofs Geometry Node Showcase.blend` wurde **nur als Hash-identische Kopie außerhalb Git** mit Blender **5.2.2 LTS** und [`inspect_showcase.py`](../experiments/external_thatch_08e/inspect_showcase.py) geöffnet. Dateiversion **4.1.24**, Dateigröße **59.190.752 B**, SHA-256 `1c96cd1701148c08ae5c4b3f5e7b4190e8230b34a870e94b5476eb867f135399`. Reproduzierbare [Inventardaten](../experiments/external_thatch_08e/inspection.json), keine fremde `.blend`, Textur oder Node-Gruppe versioniert.

| Prüfung | Tatsächlicher Befund |
|---|---|
| Datei laden | Blender 5.2.2 liest die Datei ohne relevante Ladefehler; **kein** Beweis für Kompatibilität eines nicht enthaltenen Generators. |
| Node-Gruppen und Modifier | `bpy.data.node_groups`: **0 insgesamt**, davon **0 GeometryNodeTree**. **0 Geometry-Nodes-Modifikatoren**, keine Seed-, Dichte-, Längen-, Gravity- oder Kurven-Sockets. Keine alten Nodes zu migrieren; der Kerngegenstand fehlt. |
| Vorgefertigte Geometrie | `HayRoof` **270.000 Vertices, 235.000 Polygone, 460.000 statische Dreiecke** ohne Modifier; `TestRoof` **6 Vertices, 2 Polygone, 4 Dreiecke**. Diese Zahlen sind **keine** gemessene Cottage-Dachgeometrie und keine Dichtestufe eines funktionierenden Node-Generators. |
| Materialien | Fünf vorhandene Material-Datenblöcke (`Dots Stroke`, `Hay.001`, `Material`, `Material.001`, `Wood`). `HayRoof` verwendet `Hay.001`, `TestRoof` `Wood`. Drei 2048²-Wood-Bilder sind gepackt; zwei `hay.mp4`-Movie-Bilder verweisen auf fehlende Dateien, eines auf einen Windows-Laufwerkspfad. Das Hay-Material selbst nutzt kein externes Image-Texture-Node. Fehlende Videoressourcen sind **kein** Beweis für einen kaputten Hay-Shader, aber verhindern eine vollständige Wiedergabe aller Showcase-Materialien. |
| Tatsächliche GeoNodes-Auswertung, Instanzen, Parameter | **Nicht durchführbar**, da weder Node-Gruppe noch Node-Modifier existiert. Keine verifizierbare Traufrichtung, keine anpassbare Dichte, kein Seed, keine testbare reduzierte Dichte. |
| Speicher/Datei/Timing | **59.190.752 B Datei auf Platte**; keine Speicherbelegung und keine Generator-Auswertungsdauer behauptet. Die statischen 460k Dreiecke sind ein Vorführ-Asset, **kein** Kostenbeweis für das verkaufte Produkt. |

**Lokales Reproduktionsverfahren** (vom Repo-Root, eigene Datei außerhalb Git bereitstellen; niemals Original überschreiben):

```sh
SHOWCASE_BLEND="$HOME/private-assets/3d-tudor/showcase-original.blend"
blender -b "$SHOWCASE_BLEND" -t 4 -P experiments/external_thatch_08e/inspect_showcase.py
```

Das Skript schreibt nur selbst ermittelte Metadaten in `inspection.json`; das fremde Asset bleibt unverändert. Der lokale Versuch endet **vor** einem Cottage-Adapter: die vorhandene [8D-Long-Cottage-Konfiguration](../experiments/cottage_generator_08d/long.json) (5,1 × 7,3 m, Wandhöhe 2,3 m, Pitch 40°, Seed 23) kann ohne eine externe Generator-Node-Gruppe nicht gezielt mit Stroh versehen werden. Eine rein statische Übertragung des kleinen `HayRoof`-Demo-Meshes auf 7,3 m Dachlänge wäre kein Test des beworbenen prozeduralen Systems; sie ist ausdrücklich unterblieben. Grundriss, Tür, Balken und Dach aller bestehenden Cottage-Experimente bleiben unverändert.

**Wiederanlaufbedingung:** ein vom Anbieter bereitgestelltes, rechtmäßig lokal nutzbares **funktionierendes Node-Asset** mit seinen konkret dokumentierten Sockets/Lizenzbedingungen. Dass diese Showcase-Datei keine Nodes enthält, beweist weder Unbrauchbarkeit noch Blender-5-Inkompatibilität der kostenpflichtigen Ausgabe.
