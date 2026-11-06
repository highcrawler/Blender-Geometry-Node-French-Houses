# Research R01 – Procedural Building Architecture (Reddit-Funde)

**Status:** Architekturprinzipien übernommen; neue Features ausdrücklich **nicht** freigegeben.  
**Basis:** `feature/reusable-wooden-roof-module-09f`, Commit `30b0e16`, TECHNICAL PASS.  
**Ziel:** Das eigenständige mittelalterliche Village-Asset-Set langfristig architektonisch vielfältig machen, ohne das getestete Rechteckdach, den Cottage-Adapter oder den Export-Meilenstein umzubauen.

> Die konkreten Reddit-Posts unten wurden über öffentlich auffindbare Such-/Textresultate geprüft. Der ursprünglich übermittelte Reddit-Kurzlink `/r/proceduralgeneration/s/J9KxdXABoY` ließ sich bei der Recherche nicht eindeutig auf einen Einzelpost auflösen. Deshalb wird **nicht** behauptet, die folgenden Funde seien dessen Inhalt.

## Quellen und belastbare Beobachtungen

1. **Procedural Structures** (02.10.2026): <https://www.reddit.com/r/proceduralgeneration/comments/1wvgunj/>  
   Autorenbeschreibung: Mittelalterliches Bausystem aus Stein-, Pfosten-/Bretter- und Dachbestandteilen; Öffnungen, Dachformen und Geschosshöhen editierbar; Erosion/Zerstörung als optionale Erweiterung. **Quelle zeigt einen Ansatz, nicht übertragbaren Projektcode.**
2. **Towers & Battlements** (23.07.2026): <https://www.reddit.com/r/proceduralgeneration/comments/1v4li70/>  
   Autor erläutert Steinreihen, dynamische Mesh-Chunks von ca. 12–48 Steinen, Ausschnitte durch Entfernen betroffener Steine und angepasste Randsteine sowie eine Mörtelfläche gegen Lichtspalten. **Das Chunkmaß ist eine projektspezifische Entscheidung, kein Zielwert für uns.**
3. **Procedural Stone & Timber** (29.06.2026): <https://www.reddit.com/r/proceduralgeneration/comments/1uitmh6/>  
   Der Autor beschreibt Fachwerk als konstruktiv regelbasiert und nennt zusammengefügte Grundrisse/L-Formen ausdrücklich als noch ausstehende Schwierigkeit.
4. **I have base meshes for my procedural houses!** (05.12.2024): <https://www.reddit.com/r/proceduralgeneration/comments/1h6vzz4/>  
   Ein experimenteller Algorithmus nutzt Grundrisspunkte/Schnittpunkte zur Erzeugung von Dachabschnitten; die Diskussion thematisiert Dachentwässerung bei verbundenen Teilflächen. **Kein Beweis für einen vollständigen robusten Dachalgorithmus.**
5. **My second attempt at procedural houses** (04.12.2024): <https://www.reddit.com/r/proceduralgeneration/comments/1h66oph/>  
   Autor berichtet, dass vorgefertigte Blöcke für Wände funktionieren, bei Dächern/komplexen Formen jedoch wenig Kontrolle bieten; Wechsel zu punktbasiertem Grundriss.
6. **bpypolyskel**: <https://github.com/prochitecture/bpypolyskel>  
   Open-Source-Referenz für Straight-Skeleton-basierte **Walmdach**-Flächen aus Grundrisspolygonen; **GPL-3.0**. Für unsere verbundenen **Satteldächer** nicht automatisch geeignet; möglicher späterer Forschungsbaustein, **keine Übernahme von Code ohne Lizenz- und Integrationsprüfung**.
7. **country-slice**: <https://github.com/anopara/country-slice>  
   Öffentliches Rust-/Bevy-/OpenGL-Procedural-Experiment unter **MIT**. Als technische Inspiration, nicht als bereits validierte Blender-Bausteinbibliothek betrachten.

## Architekturentscheidungen für unser Projekt

### R01-A – Gebäudetypen durch Bauregeln unterscheiden: **ÜBERNEHMEN**

**Abgeleitete Projektentscheidung, nicht wörtliche Reddit-Vorgabe:** Ein neuer Gebäudetyp braucht eine erkennbare eigene Architektur. Breite/Tiefe/Seed allein sind **keine** hinreichende Variation. Ein zukünftiger Gebäude-Archetyp soll bei seiner Einführung festlegen:
- Zweck/Nutzung (z. B. Cottage, Scheune, Werkstatt)
- charakteristische Silhouette und Proportionen
- Wand-/Tragwerksaufbau
- Platzierung/Größe der funktionalen Öffnungen (Türen, Tore, Fenster)
- zulässige Dachkonfiguration/Anschluss an vorhandenes Dachmodul

**Gate für einen zweiten Gebäudetyp:** Er muss in einer gemeinsamen Szene bei vergleichbarer Größe und Kamera **ohne Beschriftung** als anderer Gebäudetyp erkennbar sein. Keine Freigabe allein aufgrund anderer Sliderwerte.

### R01-B – Erst semantische Bauteile, danach zusätzliche Details: **ÜBERNEHMEN**

Die bereits implementierte Teilung `Cottage-Körper` + `roof/wooden_rect.py` wird beibehalten. Für spätere Körpergeneratoren Fachwerk, Wandflächen, Öffnungen und Sockel als **konzeptionell getrennte Verantwortlichkeiten** betrachten. Nur bei realem Integrationsbedarf Code extrahieren; **kein sofortiges Wall-/Window-/Stone-Framework**.

Türen/Fenster künftig als echte architektonische Regeln prüfen (Abstand zu Ecken, Balken, Geschosshöhen, Nutzungszweck), nicht nur zufällig platzierte Dekorobjekte. Der existierende Cottage-Körper bleibt für den anstehenden Export-Meilenstein unverändert.

### R01-C – Geometrie sinnvoll bündeln: **ÜBERNEHMEN ALS LEITLINIE, NICHT JETZT IMPLEMENTIEREN**

Die Reddit-Implementierung bündelt Steine für Performance. Unser Holzschindeldach macht bereits etwas Verwandtes: ein gemeinsames Schindelmesh statt hunderter Blender-Objekte. Für zukünftige Stein-/Fachwerkkonstruktionen soll die Balance aus Editierbarkeit, Draw Calls, Exportvollständigkeit und Materialzuordnung **gemessen** werden. Keine pauschale Chunkgröße, kein vorschnelles LOD- oder Zerstörungssystem.

### R01-D – Grundriss zuerst, Dachübergang separat: **ARCHITEKTURRICHTUNG ÜBERNEHMEN, UMSETZUNG SPÄTER**

Das vorhandene `RoofSpec`-Modul ist bewusst **ein** rechteckiges Satteldach mit geradem First. Es bleibt so. Langfristige L-/U-Bauten benötigen einen eigenen Grundriss-/Dachverbindungs-Schritt, der:
- mehrere Baukörper bzw. Polygonumrisse und Höhenbezüge beschreibt,
- sichtbare/verdeckt liegende Dachflächen bestimmt,
- Schnittlinien und Dachkehlen erzeugt,
- Schindelreihen an Kehlen/Giebeln passend zuschneidet,
- First-/Traufanschlüsse und plausible Regenwasserführung berücksichtigt.

**Anti-Fehlannahme:** Zwei komplette Rechteckdächer zu überlagern ist **keine** korrekte L-Dach-Implementierung. Straight Skeleton ist eine denkbare Untersuchungsmethode, nicht die jetzt gewählte Lösung; Walmdachmethoden lösen unsere Satteldach-Spezifik nicht automatisch.

Für zukünftige Dokumente einen `Footprint`-/`BuildingWing`-Begriff als **Datenkonzept** zulassen, aber noch keine neue öffentliche API und keine Geometrieimplementierung anfangen.

### R01-E – Funktion vor Zufall bei der Dorfplatzierung: **ZURÜCKSTELLEN**

Spätere Dorfverteilung soll sich nicht nur auf Zufall verlassen (z. B. Werkstätten an Wegen, Wirtschaftsgebäude bei Höfen, Mühlen in Gewässernähe). Dies ist **eine eigene Weltgenerator-Aufgabe**, kein Teil des Blender-Gebäudemoduls. Die Recherche motiviert diese Richtung, spezifiziert jedoch keinen überprüften Platzierungsalgorithmus.

## Entscheidung zum aktuellen Meilenstein

**9F bleibt unverändert und freigegeben.** Die vorliegende Recherche eröffnet **kein** neues Kernsystem und erweitert nicht `RoofSpec`, `RoofResult`, den Cottage-Adapter oder die geprüften acht Konfigurationen.

**Nächster geplanter technischer Schritt bleibt 9G (Owner-Scoped Geometry/Pivot Collector)**, danach eigenständig zu prüfen:
1. Isolierter Einzelhaus-GLB-Export mit Boden-Pivot und vollständigen Materialien,
2. schlanke Add-on-Anbindung für Cottage,
3. **erst dann** ein zweiter, deutlich unterscheidbarer Gebäudetyp mit eigenem Archetyp-Vertrag und visueller Vergleichsabnahme.

Bei der späteren Auswahl dieses zweiten Gebäudetyps sollen R01-A bis R01-C explizite Abnahmekriterien werden. L-/U-Formen folgen einem separaten Dachtopologie-Meilenstein, **nicht** als beiläufige Erweiterung des Rechteck-Moduls.

## Anti-Ideenbuch / ausdrücklich derzeit nicht starten

- Runtime-Gebäudebearbeitung, Echtzeit-Destruktion/Erosion, kollabierende Mauern
- automatisches Bauen von Stein für Stein als Selbstzweck
- vollständiges Wall-/Window-/Building-Framework
- Wave Function Collapse oder großflächige prozedurale Siedlungssimulation
- sofortige Einführung fremder Straight-Skeleton-Bibliotheken
- L-/U-Dach-Implementierung vor validiertem Rechteck-Cottage-Export
- stilistische Komplettüberarbeitung des bereits akzeptierten Dachsystems

## Wiedervorlage-Gates

- **Vor zweitem Gebäudetyp:** R01-A/B in einer kleinen Archetyp-Spezifikation nachweisen; visuelle Unterschiede an 2–3 sinnvollen Modellen zeigen.
- **Vor L-/U-Experiment:** getrennte Testszenen mit mindestens einer L-Form, eindeutigen First-/Kehllinien, Schindelzuschnitt und Drainage-Plausibilitätsprüfung planen; Lizenzprüfung externer Algorithmen.
- **Vor Dorfplatzierung:** funktionale Gebäudekategorien und World-Generator-Meilenstein definieren.

**Diese Datei dokumentiert Entscheidungen und Grenzen, keine implementierte, getestete neue Funktion.**
