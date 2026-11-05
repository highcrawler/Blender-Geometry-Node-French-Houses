# Phase 8F – Visuelle Vorher-/Nachher-Beurteilung

**VISUAL RESULT: WORSE** im vorgegebenen stilisierten Cottage-Kontext und besonders bei mittlerer Entfernung; **keine künstlerische Freigabe durch den Benutzer**. Technisch funktionieren beide Materialzustände. Jeder Zustand wurde neu und unabhängig mit Blender 5.2.2/Cycles gerendert; dieselben Long-Cottage-Meshes, dieselbe Kamera, Welt, zwei Flächenlichter, Belichtung, Auflösung und 16 Samples. **Nur** das Dachmaterial und die UV-Daten der CC0-Kopie unterscheiden sich. Die Tafeln ordnen echte Einzelrenderings verlustfrei nebeneinander (Pillow ist nicht der Renderer).

| Ansicht | Vorher: 8D-H-Material | Nachher: Poly Haven CC0 | Tafel |
|---|---|---|---|
| Isometrische Gesamtansicht | [BASELINE](../experiments/cottage_generator_08f/screenshots/baseline_iso.png) | [CC0](../experiments/cottage_generator_08f/screenshots/cc0_iso.png) | [direkter Vergleich](../experiments/cottage_generator_08f/screenshots/before_after.png) |
| Front | [BASELINE](../experiments/cottage_generator_08f/screenshots/baseline_front.png) | [CC0](../experiments/cottage_generator_08f/screenshots/cc0_front.png) | [Tafel](../experiments/cottage_generator_08f/screenshots/before_after_front.png) |
| Dach-Nahaufnahme | [BASELINE](../experiments/cottage_generator_08f/screenshots/baseline_detail.png) | [CC0](../experiments/cottage_generator_08f/screenshots/cc0_detail.png) | [Tafel](../experiments/cottage_generator_08f/screenshots/before_after_detail.png) |
| Trauf-Nahaufnahme | [BASELINE](../experiments/cottage_generator_08f/screenshots/baseline_eave.png) | [CC0](../experiments/cottage_generator_08f/screenshots/cc0_eave.png) | [Tafel](../experiments/cottage_generator_08f/screenshots/before_after_eave.png) |
| Gesamtgebäude ~300 px hoch, in Blender nativ 480×360 | [BASELINE](../experiments/cottage_generator_08f/screenshots/baseline_iso_300.png) | [CC0](../experiments/cottage_generator_08f/screenshots/cc0_iso_300.png) | **[entscheidender Vergleich](../experiments/cottage_generator_08f/screenshots/before_after_300.png)** |

## Beobachtungen (am wirklichen Vergleich, keine Produktwerbung)

- **Nahansicht:** CC0 zeigt viel mehr unregelmäßige fallgerichtete Faserstruktur auf der Hauptdachfläche. Der bisherige H-Shader wirkt daneben glatt und holzartig. Der Texturausschnitt ist nicht offensichtlich verdreht oder großflächig gezerrt. In der Nahaufnahme zeichnen sich einige gleiche Strukturdetails wiederholt ab; aus ~300 px ist das Kacheln kein dominierendes Problem.
- **Aus ~300 px:** Die zusätzlichen feinen Fasern verschmelzen zu einem dunklen, relativ einheitlichen Grau. Das Dach wirkt wie gealtertes Schilf, dunkler Schiefer oder raues Holz statt wie ein warmes, überzeugend **gebündeltes** Strohdach; es bildet keine neue erkennbare Volumenwirkung aus. Die Faserrichtung ist in der Nahaufnahme, nicht deutlich aus dieser Entfernung zu lesen.
- **Traufe:** Beide Zustände nutzen dieselben kurzen, einzeln erkennbaren H-Teilbündel. Das neue Material ändert weder Dichte, Form, Länge noch Kantenkontur. Die dunklen Schnittseiten lassen die fingerartigen/plättchenartigen Enden eher härter wirken. Vorhandene dunkle Ansatzbereiche und der kleine First-Giebel-Schatten bleiben.
- **Stil:** Die originalbelassene 2K-Diffuse wirkt kalt und sehr dunkel neben den hellen Putz-/Holzmaterialien; der bisherige Beige-Ton fügt sich trotz glatterer Oberfläche konsistenter in dieses Cottage ein. Eine nachträgliche Tönung wäre **ein anderer, hier nicht angeforderter Test** und wurde nicht vorgenommen. Normal/Roughness liefern Relief unter dem Studiolicht, aber keinen Ersatz für glaubwürdige Strohmasse an der Traufe.

**Urteil:** Texturdetail **besser**, Gesamtwirkung als stilisiertes, aus normaler Entfernung lesbares Strohdach **schlechter** als H; daher **WORSE** für das eigentliche Ziel. Kein Grund, das CC0-Material als neuen Cottage-Standard zu übernehmen. Vor einer neuen gestalterischen Vorgabe keine weiteren Material-/Dachvarianten.
