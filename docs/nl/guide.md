# Opgenomen spraakscenario's evalueren

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

## Installatie en grenzen

Installeer vanuit een checkout met `python3 -m pip install .` in een virtuele omgeving. Python 3.11+ wordt ondersteund. Er zijn geen runtimeafhankelijkheden buiten Python. `assist-lab --help --lang en` toont de opdrachten; `ru`, `de` en `es` werken ook. Het startpunt als module is `python3 -m assist_scenario_lab`.

Voor het laden van bestanden zijn de OS-vlaggen `O_NOFOLLOW` en `O_NONBLOCK` nodig, beschikbaar op Linux en macOS. Ontbreekt een van beide, dan stopt de CLI vóór het openen van de invoer met afsluitcode 2 en `unsupported_platform`. De Python-API's voor evaluatie en import in het geheugen hebben deze vlaggen niet nodig.

Dit is een offline evaluator, geen satellietfirmware, akoestische detector, live gegevensverzamelaar, HA-integratie of volledige benchmark. Voer echte productacceptatietests uit met de juiste firmwaretools. Geef het resulterende bewijsmateriaal van beperkte omvang pas aan deze tool na een privacycontrole.

## Canonieke invoer

Begin met `examples/synthetic-pass.json`. De hoofdstructuur vereist `schema: assist-scenario-lab/v1`, de booleaanse waarde `synthetic`, een `requirements`-object en 1–500 `sessions`. Onbekende velden worden geweigerd. Een sessie heeft een unieke `id` plus `platform`, `scenario`, `clock`, `events` en `checks`. ID's bestaan uit 1–64 ASCII-letters, cijfers, onderstrepingstekens of koppeltekens en beginnen met een letter of cijfer. Gebruik pseudoniemen, geen kamernamen, adressen of apparaat-ID's.

`clock` is `relative_monotonic` of `utc_derived`. Gebeurtenissen bevatten `stage`, `at_ms`, `origin`. Tijden zijn eindig, niet negatief, maximaal 12 uur en niet-aflopend gesorteerd. De eerste gebeurtenis is `request` op nul. Een fase komt één keer voor. Ondersteunde fasen: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Verschillende pipelines kunnen streamen; er is bewust geen vaste volgorde tussen TTS en afspelen buiten de chronologische tijdstempels.

Bronnen zijn `pipeline`, `satellite`, `operator` en `acoustic`. Alleen `operator` of `acoustic` kunnen de bron van `audible_start` zijn. Elke sessie moet alle drie controles leveren: `intent_correct`, `action_observed`, `audible`. Elke controle heeft `result` (`pass`, `fail`, `unknown`) en `method`. Een onbekend resultaat vereist `none`. Andere geldige methoden zijn `operator`/`intent_assertion` voor intentie, `operator`/`ha_state` voor actie en `operator`/`acoustic` voor hoorbaarheid. Een tijdstempel voor hoorbaar geluid vereist een geslaagde hoorbaarheidscontrole. De tool controleert consistentie, niet waarheid.

De eisen kunnen elk van de drie controles activeren en optioneel `max_audible_ms`. Weggelaten of onware controles zijn niet vereist: een beleid voor alleen API's kan zonder fysiek bewijs slagen en moet als zodanig worden aangeduid. De meegeleverde voorbeelden vereisen alle controles. Een pipelinefout leidt altijd tot mislukking. Ontbrekende `protocol_end` betekent onvolledig. Een verplichte mislukking weegt zwaarder dan onbekende waarnemingen. Latentie boven de grens mislukt; ontbrekende vereiste latentie is onvolledig.

## Een HA-run importeren

De adapter verwerkt één **array van gebeurtenisobjecten**, geen volledig WebSocket-logboek of diagnostisch ZIP-bestand. Extraheer de inhoud van elke gebeurtenis lokaal. Objecten hebben precies `type`, `timestamp`, `data`; de gegevens kunnen een object of null zijn. Tijdstempels moeten ISO 8601 met tijdzone gebruiken. Begin met `run-start`, behoud de chronologische volgorde en meng geen runs. Herhaalde gekoppelde fasen worden geweigerd.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

De tweede opdracht retourneert bewust 3. `run-end` wordt `protocol_end`, geen fysiek succes. `tts-end` wordt `tts_ready`, geen hoorbaar geluid. Alle `data` worden weggegooid, waaronder transcripties, invoertekst, fouten, TTS-URL's/-tokens en pipelinemetadata. Start-, voortgangs- en VAD-gebeurtenissen worden herkend maar niet bewaard. Omgerekende tijden gebruiken `utc_derived`: kloktijden aftrekken is geen monotone latentiemeting en kan door klokcorrecties worden beïnvloed. Alle drie fysieke/semantische controles blijven onbekend.

## Rapporten en vergelijking

`--format text|json|html|junit` kiest het rapport. Shell-omleiding schrijft het resultaat naar een gekozen lokaal pad. De CLI overschrijft zelf nooit invoer. Afsluitcodes: 0, geregistreerde eisen gehaald; 1, mislukt; 2, ongeldige invoer/argumenten; 3, onvolledig. JUnit toont onvolledige sessies als overgeslagen; CI moet afsluitcode 3 toch respecteren.

JSON groepeert op platform + scenario + klok + methode voor hoorbare timing. Behandel verschillende klokken of menselijke en akoestische waarnemingen nooit als uitwisselbare metingen. p50/p95 gebruiken de nearest-rank-methode. Onder 20 monsters is p95 null; 20 is een rapportagedrempel, geen bewijs van statistische betrouwbaarheid. Mislukte sessies met waargenomen audio blijven deel van de latentiesteekproef en hun aantal mislukkingen blijft zichtbaar. Selecteer niet alleen geslaagde pogingen. Er worden geen ruwe audio of transcripties geëxporteerd. ID's kunnen nog steeds informatie onthullen; controleer ze daarom.

HTML toont alle sessies en tekent de eerste 50 hoorbare waarnemingen op dezelfde schaal. Lees platform en methode van elke rij; het overzicht is geen statistische ranglijst. `evidence_verified: false` is altijd aanwezig. `synthetic: false` betekent dat de auteur de run niet als synthetisch heeft gemarkeerd, niet dat de hardware onafhankelijk is gevalideerd.

## Betekenisvol bewijs verzamelen

Bepaal vóór een proef de verwachte intentie en het doel. Definieer steeds dezelfde startgebeurtenis: een pipelineverzoek is niet noodzakelijk het begin van de gesproken zin. Houd een extern proeflogboek bij met softwareversies, taal, netwerkomstandigheden, plaatsing van microfoon en luidspreker, waarnemingsmethode en aantal proeven. Gebruik een geschikte akoestische meting voor nauwkeurige hoorbare timing; vervang die niet door het eerste netwerkfragment. Registreer mislukkingen, time-outs en ontbrekend bewijs. Dit pakket voert geen akoestische synchronisatie of toestemmingsbeheer uit.

## Problemen oplossen

- `object_fields`: vergelijk de sleutels met de canonieke testgegevens; een volledige diagnostische dump wordt niet geaccepteerd.
- `ha_timestamp` / `time_order`: exporteer één run, neem tijdzones op en controleer klokcorrecties. Herschik gebeurtenissen niet om latentie te fabriceren.
- `stage`: een fase is onbekend of dubbel; controleer of twee runs zijn samengevoegd.
- `audible_origin` / `conflicting_audible`: afspeelmetadata kunnen het horen van geluid niet vervangen.
- Afsluitcode 3 na een geslaagde API: verwacht totdat de vereiste waarnemingen zijn vastgelegd.
- `unsupported_platform`: het OS mist `O_NOFOLLOW` of `O_NONBLOCK`; gebruik een omgeving met beide (Linux of macOS). Invoer wordt vóór opening geweigerd, in plaats van controles op symbolische links of FIFO's te verzwakken.
- `file_size_type`: alleen gewone UTF-8-JSON-bestanden, maximaal 2 MiB. Mappen, FIFO's en symbolische links in de laatste padcomponent worden geweigerd. Links in bovenliggende mappen vormen geen sandboxgrens.
- `number`: geen negatieve, niet-eindige, booleaanse of meer dan 12 uur grote tijdstempels.

Fouten tonen een vertaalde samenvatting en stabiele code, geen broninhoud of lokale paden. De openbare voorbeelden zijn volledig synthetisch. Bewaar exports buiten deze checkout, bij voorkeur in een privétijdelijke map.

## Architectuur, vertalingen en bronnen

![Offline gegevensstroom](../../assets/architecture.svg)

`core.py` verzorgt pure validatie, import en evaluatie; `cli.py` rendert formaten; `locales/*.json` bevat vier catalogi. Tests vereisen gelijke catalogussleutels. Machinesleutels en diagnostische codes worden niet vertaald. Volledige handleidingen omvatten de 24 documentatietalen van ha-homelab; CLI en README blijven Engels, Russisch, Duits en Spaans. Draag aanvullende referentievertalingen bij met gelijkheidscontroles en beoordeelde voorbeelden.

De protocolkoppeling is gecontroleerd aan de hand van de [Home Assistant Assist-documentatie](https://developers.home-assistant.io/docs/voice/pipelines/) en de [HA 2026.10.0-gebeurtenismodellen](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). De satellietlevenscyclus staat in de [officiële entiteitshandleiding](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Deze upstream-API's beloven geen akoestische verificatie; die hier apart houden is een ontwerpkeuze.
