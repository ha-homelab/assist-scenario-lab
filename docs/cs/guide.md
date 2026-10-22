# Vyhodnocení zaznamenaných hlasových scénářů

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

## Instalace a hranice

Nainstalujte projekt z pracovní kopie příkazem `python3 -m pip install .` ve virtuálním prostředí. Podporován je Python 3.11+. Kromě Pythonu nejsou žádné běhové závislosti. `assist-lab --help --lang en` vypíše příkazy; fungují také `ru`, `de` a `es`. Spuštění jako modul má podobu `python3 -m assist_scenario_lab`.

Načítání souborů vyžaduje příznaky operačního systému `O_NOFOLLOW` a `O_NONBLOCK`, dostupné na Linuxu a macOS. Pokud některý chybí, CLI ještě před otevřením vstupu skončí kódem 2 s `unsupported_platform`. Python API pro vyhodnocení a import v paměti tyto příznaky nepotřebují.

Jde o offline vyhodnocovač, nikoli firmware satelitu, akustický detektor, živý sběrač dat, integraci HA ani úplný benchmark. Skutečné uživatelské přejímací testy produktu provádějte odpovídajícími nástroji firmwaru. Výsledné podklady omezeného rozsahu předávejte tomuto nástroji až po kontrole soukromí.

## Kanonický vstup

Začněte souborem `examples/synthetic-pass.json`. Kořen vyžaduje `schema: assist-scenario-lab/v1`, booleovské `synthetic`, objekt `requirements` a 1–500 `sessions`. Neznámá pole jsou odmítnuta. Relace má jedinečné `id` a dále `platform`, `scenario`, `clock`, `events` a `checks`. Identifikátory obsahují 1–64 písmen ASCII, číslic, podtržítek nebo pomlček a začínají písmenem či číslicí. Používejte pseudonymy, nikoli názvy místností, adresy nebo identifikátory zařízení.

`clock` je `relative_monotonic` nebo `utc_derived`. Události obsahují `stage`, `at_ms`, `origin`. Časy jsou konečné, nezáporné, nejvýše 12 hodin a neklesající. První událostí je `request` v nule. Každá fáze nastane jednou. Podporované fáze: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Různé pipeline mohou streamovat; mimo chronologické časové značky proto záměrně není pevné pořadí TTS a přehrávání.

Původy jsou `pipeline`, `satellite`, `operator` a `acoustic`. Pouze `operator` nebo `acoustic` smějí být zdrojem `audible_start`. Každá relace musí dodat všechny tři kontroly: `intent_correct`, `action_observed`, `audible`. Každá má `result` (`pass`, `fail`, `unknown`) a `method`. Neznámý výsledek vyžaduje `none`. Další platné metody jsou `operator`/`intent_assertion` pro záměr, `operator`/`ha_state` pro akci a `operator`/`acoustic` pro slyšitelnost. Časová značka slyšitelného zvuku vyžaduje úspěšnou kontrolu slyšitelnosti. Nástroj ověřuje konzistenci, nikoli pravdivost.

Požadavky mohou zapnout libovolnou ze tří kontrol a volitelně `max_audible_ms`. Vynechané či nepravdivé kontroly nejsou požadovány: politika pouze pro API může uspět bez fyzických důkazů a musí tak být označena. Dodané příklady požadují všechny kontroly. Chyba pipeline vždy znamená neúspěch. Chybějící `protocol_end` znamená neúplnost. Neúspěch povinné kontroly má přednost před neznámými pozorováními. Latence nad mezí neprojde; chybějící povinná latence je neúplná.

## Import běhu HA

Adaptér přijímá jedno **pole objektů událostí**, nikoli celý protokol WebSocket ani diagnostický ZIP. Tělo každé události vyjměte lokálně. Objekty mají přesně `type`, `timestamp`, `data`; data mohou být objekt nebo null. Časové značky musí být ISO 8601 s časovým pásmem. Začněte `run-start`, zachovejte chronologické pořadí a nemíchejte běhy. Opakované mapované fáze jsou odmítnuty.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

Druhý příkaz záměrně vrátí 3. `run-end` se mapuje na `protocol_end`, ne na fyzický úspěch. `tts-end` se mapuje na `tts_ready`, ne na slyšitelný zvuk. Veškerá `data` se zahodí, včetně přepisů, vstupního textu, chyb, TTS URL/tokenů a metadat pipeline. Události začátku, průběhu a VAD se rozpoznají, ale neuchovávají. Převedené časy používají `utc_derived`: odečítání běžných hodin není monotónní měření latence a může je ovlivnit oprava hodin. Všechny tři fyzické/sémantické kontroly zůstávají neznámé.

## Reporty a porovnání

`--format text|json|html|junit` vybere report. Přesměrování shellu zapíše výsledek do zvolené lokální cesty. Samotné CLI nikdy nepřepisuje vstup. Návratové kódy: 0, zaznamenané požadavky splněny; 1, neúspěch; 2, neplatný vstup/argumenty; 3, neúplnost. JUnit zobrazuje neúplné relace jako přeskočené; CI musí přesto respektovat kód 3.

JSON seskupuje podle platformy, scénáře, hodin a metody měření slyšitelnosti. Různé hodiny ani lidská a akustická pozorování nikdy nepovažujte za zaměnitelná měření. p50/p95 používají nejbližší pořadí. Při méně než 20 vzorcích je p95 null; 20 je práh reportování, nikoli důkaz statistické spolehlivosti. Neúspěšné relace s pozorovaným zvukem zůstávají ve výběru latencí a jejich počet neúspěchů je nadále viditelný. Nevybírejte pouze úspěšné pokusy. Neexportuje se nezpracované audio ani přepis. Identifikátory přesto mohou prozradit informace, proto je zkontrolujte.

HTML vypíše všechny relace a vykreslí prvních 50 slyšitelných pozorování se společnou stupnicí. Čtěte platformu a metodu každého řádku; přehled není statistickým žebříčkem. Vždy je přítomno `evidence_verified: false`. `synthetic: false` znamená, že autor běh neoznačil jako syntetický, nikoli že byl hardware nezávisle ověřen.

## Sběr smysluplných podkladů

Před pokusem definujte očekávaný záměr a cíl. Počáteční událost určujte konzistentně: požadavek pipeline není nutně začátkem vyslovené fráze. Veďte samostatný záznam pokusů s verzemi softwaru, jazykem, podmínkami sítě, umístěním mikrofonu a reproduktoru, metodou pozorování a počtem pokusů. Pro přesné časování slyšitelného zvuku použijte vhodné akustické měření; nenahrazujte je prvním síťovým blokem. Zaznamenávejte neúspěchy, timeouty a chybějící podklady. Balíček neprovádí akustickou synchronizaci ani správu souhlasů.

## Řešení problémů

- `object_fields`: porovnejte klíče s kanonickými testovacími daty; úplný diagnostický výpis se nepřijímá.
- `ha_timestamp` / `time_order`: exportujte jeden běh, zahrňte časová pásma a prověřte opravy hodin. Neměňte pořadí událostí pro umělé vytvoření latence.
- `stage`: fáze je neznámá nebo opakovaná; zkontrolujte, zda nebyly spojeny dva běhy.
- `audible_origin` / `conflicting_audible`: metadata přehrávání nenahrazují slyšení zvuku.
- Kód 3 po úspěšném API: očekávaný, dokud nejsou zaznamenána povinná pozorování.
- `unsupported_platform`: systému chybí `O_NOFOLLOW` nebo `O_NONBLOCK`; použijte prostředí s oběma příznaky (Linux nebo macOS). Vstup se odmítne před otevřením, místo aby se oslabily kontroly symlinků nebo FIFO.
- `file_size_type`: pouze běžné UTF-8 JSON soubory do 2 MiB. Adresáře, FIFO a symbolické odkazy v poslední části cesty jsou odmítnuty. Odkazy v nadřazených adresářích nejsou hranicí sandboxu.
- `number`: žádné záporné, nekonečné, booleovské ani více než 12hodinové časové značky.

Chyby vypisují přeložené shrnutí a stabilní kód, nikoli obsah zdroje nebo lokální cesty. Veřejné příklady jsou zcela syntetické. Exporty uchovávejte mimo tuto pracovní kopii, nejlépe v soukromém dočasném adresáři.

## Architektura, překlady a zdroje

`core.py` zajišťuje čistou validaci, import a vyhodnocení; `cli.py` vytváří výstupní formáty; `locales/*.json` obsahuje čtyři katalogy. Testy vyžadují shodu klíčů katalogů. Strojové klíče a diagnostické kódy se nepřekládají. Úplné příručky pokrývají 24 dokumentačních jazyků ha-homelab; CLI a README zůstávají anglicky, rusky, německy a španělsky. Přispívejte dalšími referenčními překlady s kontrolami shody a zrevidovanými příklady.

![Offline tok](../../assets/architecture.svg)

Mapování protokolu bylo ověřeno podle [dokumentace Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) a [modelů událostí HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Životní cyklus satelitu popisuje [oficiální průvodce entitou](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Tato upstream API neslibují akustické ověření; jeho oddělení je zde návrhovým rozhodnutím.
