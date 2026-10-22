# Auswertung aufgezeichneter Sprachszenarien

<!-- language-navigation:start -->
<p dir="ltr">
<a href="../en/guide.md" lang="en" dir="ltr">English</a> ·
<a href="../ar/guide.md" lang="ar" dir="rtl">العربية</a> ·
<a href="../bn/guide.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="../cs/guide.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="../de/guide.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="../es/guide.md" lang="es" dir="ltr">Español</a> ·
<a href="../fa/guide.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="../fr/guide.md" lang="fr" dir="ltr">Français</a> ·
<a href="../he/guide.md" lang="he" dir="rtl">עברית</a> ·
<a href="../hi/guide.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="../id/guide.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="../it/guide.md" lang="it" dir="ltr">Italiano</a> ·
<a href="../ja/guide.md" lang="ja" dir="ltr">日本語</a> ·
<a href="../ko/guide.md" lang="ko" dir="ltr">한국어</a> ·
<a href="../nl/guide.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="../pl/guide.md" lang="pl" dir="ltr">Polski</a> ·
<a href="../pt/guide.md" lang="pt" dir="ltr">Português</a> ·
<a href="../ru/guide.md" lang="ru" dir="ltr">Русский</a> ·
<a href="../th/guide.md" lang="th" dir="ltr">ไทย</a> ·
<a href="../tr/guide.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="../uk/guide.md" lang="uk" dir="ltr">Українська</a> ·
<a href="../vi/guide.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="../zh-Hans/guide.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="../zh-Hant/guide.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

## Installation und Grenzen

Installieren Sie das Projekt aus einem Checkout mit `python3 -m pip install .` in einer virtuellen Umgebung. Python 3.11+ wird unterstützt. Außer Python gibt es keine Laufzeitabhängigkeiten. `assist-lab --help --lang en` listet die Befehle auf; `ru`, `de` und `es` funktionieren ebenfalls. Der Moduleinstieg lautet `python3 -m assist_scenario_lab`.

Zum Laden von Dateien werden die Betriebssystem-Flags `O_NOFOLLOW` und `O_NONBLOCK` benötigt, die unter Linux und macOS verfügbar sind. Fehlt eines davon, beendet sich die CLI vor dem Öffnen der Eingabe mit Code 2 und `unsupported_platform`. Die Python-APIs für Auswertung und Import im Speicher benötigen diese Flags nicht.

Dies ist ein Offline-Auswerter, keine Satelliten-Firmware, kein akustischer Detektor, Live-Datensammler, keine HA-Integration und kein vollständiger Benchmark. Führen Sie tatsächliche Produktabnahmetests mit den geeigneten Firmware-Werkzeugen durch. Übergeben Sie diesem Werkzeug die daraus gewonnenen, im Umfang begrenzten Nachweise erst nach einer Datenschutzprüfung.

## Kanonische Eingabe

Beginnen Sie mit `examples/synthetic-pass.json`. Die Wurzel benötigt `schema: assist-scenario-lab/v1`, den booleschen Wert `synthetic`, ein `requirements`-Objekt und 1–500 `sessions`. Unbekannte Felder werden abgelehnt. Eine Sitzung hat eine eindeutige `id` sowie `platform`, `scenario`, `clock`, `events` und `checks`. IDs bestehen aus 1–64 ASCII-Buchstaben, Ziffern, Unterstrichen oder Bindestrichen und beginnen mit Buchstaben oder Ziffern. Verwenden Sie Pseudonyme statt Raumnamen, Adressen oder Gerätekennungen.

`clock` ist `relative_monotonic` oder `utc_derived`. Ereignisse enthalten `stage`, `at_ms`, `origin`. Zeitwerte sind endlich, nicht negativ, höchstens 12 Stunden und nicht absteigend sortiert. Das erste Ereignis ist `request` bei null. Jede Stufe tritt einmal auf. Unterstützte Stufen: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Verschiedene Pipelines können streamen; über die chronologischen Zeitstempel hinaus gibt es bewusst keine feste Reihenfolge zwischen TTS und Wiedergabe.

Ursprünge sind `pipeline`, `satellite`, `operator` und `acoustic`. Nur `operator` oder `acoustic` dürfen Ursprung von `audible_start` sein. Jede Sitzung muss alle drei Prüfungen liefern: `intent_correct`, `action_observed`, `audible`. Jede hat `result` (`pass`, `fail`, `unknown`) und `method`. Ein unbekanntes Ergebnis verlangt `none`. Sonstige gültige Methoden sind `operator`/`intent_assertion` für die Absicht, `operator`/`ha_state` für die Aktion und `operator`/`acoustic` für die Hörbarkeit. Ein Zeitstempel für hörbaren Ton verlangt eine bestandene Hörbarkeitsprüfung. Das Werkzeug prüft Konsistenz, nicht Wahrheit.

Die Anforderungen können jede der drei Prüfungen und optional `max_audible_ms` aktivieren. Ausgelassene oder falsche Prüfungen sind nicht erforderlich: Eine reine API-Richtlinie kann ohne physische Nachweise bestehen und muss entsprechend gekennzeichnet sein. Die mitgelieferten Beispiele verlangen alle Prüfungen. Ein Pipeline-Fehler führt immer zum Fehlschlag. Fehlt `protocol_end`, ist das Ergebnis unvollständig. Eine erforderliche fehlgeschlagene Prüfung hat Vorrang vor unbekannten Beobachtungen. Latenz über dem Grenzwert bedeutet Fehlschlag; fehlende erforderliche Latenz bedeutet Unvollständigkeit.

## Einen HA-Lauf importieren

Der Adapter verarbeitet ein **Array von Ereignisobjekten**, kein vollständiges WebSocket-Protokoll oder Diagnose-ZIP. Extrahieren Sie jeden Ereignisinhalt lokal. Objekte haben genau `type`, `timestamp`, `data`; die Daten dürfen ein Objekt oder null sein. Zeitstempel müssen ISO 8601 mit Zeitzone entsprechen. Beginnen Sie mit `run-start`, behalten Sie die chronologische Reihenfolge bei und mischen Sie keine Läufe. Wiederholte zugeordnete Stufen werden abgelehnt.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

Der zweite Befehl liefert absichtlich 3 zurück. `run-end` wird zu `protocol_end`, nicht zu physischem Erfolg. `tts-end` wird zu `tts_ready`, nicht zu hörbarem Ton. Sämtliche `data` werden verworfen, einschließlich Transkripten, Eingabetext, Fehlern, TTS-URLs/-Tokens und Pipeline-Metadaten. Start-, Fortschritts- und VAD-Ereignisse werden erkannt, aber nicht aufbewahrt. Umgerechnete Zeiten verwenden `utc_derived`: Die Subtraktion von Uhrzeiten ist keine monotone Latenzmessung und kann von Uhrkorrekturen beeinflusst werden. Alle drei physischen/semantischen Prüfungen bleiben unbekannt.

## Berichte und Vergleiche

`--format text|json|html|junit` wählt den Bericht. Shell-Umleitung schreibt das Ergebnis an einen gewählten lokalen Pfad. Die CLI selbst überschreibt niemals eine Eingabe. Exit 0: aufgezeichnete Anforderungen erfüllt; 1: fehlgeschlagen; 2: ungültige Eingabe/Argumente; 3: unvollständig. JUnit stellt unvollständige Sitzungen als übersprungen dar; CI muss dennoch Exit 3 beachten.

JSON gruppiert nach Plattform, Szenario, Uhr und Methode zur Messung des hörbaren Beginns. Vergleichen Sie unterschiedliche Uhren oder menschliche und akustische Beobachtungen niemals als austauschbare Messungen. p50/p95 verwenden die Nearest-Rank-Methode. Unter 20 Stichproben ist p95 null; 20 ist eine Berichtsschwelle, kein Nachweis statistischer Sicherheit. Fehlgeschlagene Sitzungen mit beobachtetem Ton bleiben in der Latenzstichprobe, und ihre Fehleranzahl bleibt sichtbar. Wählen Sie nicht nur erfolgreiche Versuche aus. Rohaudio und Transkripte werden nicht exportiert. IDs können dennoch Informationen offenlegen; prüfen Sie sie deshalb.

HTML listet alle Sitzungen auf und zeichnet die ersten 50 hörbaren Beobachtungen auf einer gemeinsamen Skala. Beachten Sie Plattform und Methode jeder Zeile; die Übersicht ist keine statistische Rangliste. `evidence_verified: false` ist immer enthalten. `synthetic: false` bedeutet, dass der Autor den Lauf nicht als synthetisch markiert hat, nicht dass Hardware unabhängig validiert wurde.

## Aussagekräftige Nachweise sammeln

Definieren Sie vor jedem Versuch die erwartete Absicht und das Ziel. Legen Sie einheitlich das Startereignis fest: Eine Pipeline-Anfrage ist nicht unbedingt der Anfang der gesprochenen Äußerung. Führen Sie außerhalb des Werkzeugs ein Versuchsprotokoll mit Softwareversionen, Sprache, Netzwerkbedingungen, Mikrofon- und Lautsprecherposition, Beobachtungsmethode und Versuchsanzahl. Für präzise hörbare Zeitpunkte ist eine geeignete akustische Messung nötig; ersetzen Sie sie nicht durch das erste Netzwerkfragment. Zeichnen Sie Fehler, Zeitüberschreitungen und fehlende Nachweise auf. Dieses Paket führt weder akustische Synchronisation noch Einwilligungsverwaltung durch.

## Fehlerbehebung

- `object_fields`: Vergleichen Sie die Schlüssel mit dem kanonischen Testdatensatz; ein vollständiger Diagnose-Dump wird nicht akzeptiert.
- `ha_timestamp` / `time_order`: Exportieren Sie einen Lauf, geben Sie Zeitzonen an und prüfen Sie Uhrkorrekturen. Ordnen Sie Ereignisse nicht um, um Latenzwerte zu erzeugen.
- `stage`: Eine Stufe ist unbekannt oder doppelt; prüfen Sie, ob zwei Läufe zusammengefügt wurden.
- `audible_origin` / `conflicting_audible`: Wiedergabemetadaten können hörbaren Ton nicht ersetzen.
- Exit 3 nach erfolgreicher API: erwartet, bis die erforderlichen Beobachtungen aufgezeichnet sind.
- `unsupported_platform`: Dem Betriebssystem fehlt `O_NOFOLLOW` oder `O_NONBLOCK`; verwenden Sie eine Umgebung mit beiden Flags (Linux oder macOS). Die Eingabe wird vor dem Öffnen abgelehnt, statt Symlink- oder FIFO-Prüfungen abzuschwächen.
- `file_size_type`: Nur reguläre UTF-8-JSON-Dateien, höchstens 2 MiB. Verzeichnisse, FIFOs und Symlinks in der letzten Pfadkomponente werden abgelehnt. Symlinks in übergeordneten Verzeichnissen sind keine Sandbox-Grenze.
- `number`: Keine negativen, nicht endlichen, booleschen oder mehr als 12 Stunden umfassenden Zeitstempel.

Fehler geben eine übersetzte Zusammenfassung und einen stabilen Code aus, keine Quelldaten oder lokalen Pfade. Die öffentlichen Beispiele sind vollständig synthetisch. Bewahren Sie Exporte außerhalb dieses Checkouts auf, vorzugsweise in einem privaten temporären Verzeichnis.

## Architektur, Übersetzungen und Quellen

![Offline-Datenfluss](../../assets/architecture.svg)

`core.py` übernimmt reine Validierung, Import und Auswertung; `cli.py` rendert Formate; `locales/*.json` enthält vier Kataloge. Tests verlangen identische Katalogschlüssel. Maschinelle Schlüssel und Diagnosecodes werden nicht übersetzt. Vollständige Anleitungen decken die 24 Dokumentationssprachen von ha-homelab ab; CLI und README bleiben Englisch, Russisch, Deutsch und Spanisch. Ergänzen Sie Referenzübersetzungen mit Konsistenztests und geprüften Beispielen.

Die Protokollzuordnung wurde anhand der [Home Assistant Assist-Dokumentation](https://developers.home-assistant.io/docs/voice/pipelines/) und der [Ereignismodelle von HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py) geprüft. Der Satellitenlebenszyklus ist in der [offiziellen Entitätsanleitung](https://developers.home-assistant.io/docs/core/entity/assist-satellite/) beschrieben. Diese Upstream-APIs versprechen keine akustische Verifizierung; ihre Trennung ist hier eine Entwurfsentscheidung.
