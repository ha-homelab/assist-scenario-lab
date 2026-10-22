# Ocena zarejestrowanych scenariuszy głosowych

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

## Instalacja i granice

Zainstaluj projekt z kopii repozytorium poleceniem `python3 -m pip install .` w środowisku wirtualnym. Obsługiwany jest Python 3.11+. Poza Pythonem nie ma zależności wykonawczych. `assist-lab --help --lang en` wyświetla polecenia; działają też `ru`, `de` i `es`. Uruchomienie jako moduł to `python3 -m assist_scenario_lab`.

Wczytywanie plików wymaga flag systemu operacyjnego `O_NOFOLLOW` i `O_NONBLOCK`, dostępnych w Linux i macOS. Jeśli którejś brakuje, CLI zwraca kod 2 z `unsupported_platform` przed otwarciem wejścia. API Pythona do oceny i importu w pamięci nie potrzebują tych flag.

To narzędzie oceny offline, a nie firmware satelity, detektor akustyczny, kolektor na żywo, integracja HA czy kompletny benchmark. Rzeczywiste testy akceptacyjne produktu wykonuj odpowiednimi narzędziami firmware. Otrzymane dowody o ograniczonym rozmiarze przekazuj temu narzędziu dopiero po sprawdzeniu prywatności.

## Kanoniczne wejście

Zacznij od `examples/synthetic-pass.json`. Obiekt główny wymaga `schema: assist-scenario-lab/v1`, wartości logicznej `synthetic`, obiektu `requirements` i od 1 do 500 `sessions`. Nieznane pola są odrzucane. Sesja ma unikatowe `id` oraz `platform`, `scenario`, `clock`, `events` i `checks`. Identyfikatory składają się z 1–64 liter ASCII, cyfr, podkreśleń lub łączników i zaczynają literą albo cyfrą. Używaj pseudonimów, nie nazw pomieszczeń, adresów czy identyfikatorów urządzeń.

`clock` ma wartość `relative_monotonic` lub `utc_derived`. Zdarzenia zawierają `stage`, `at_ms`, `origin`. Czasy są skończone, nieujemne, nie większe niż 12 godzin i uporządkowane niemalejąco. Pierwszym zdarzeniem jest `request` w chwili zero. Każdy etap występuje raz. Obsługiwane etapy: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Różne potoki mogą przesyłać strumieniowo; celowo nie narzucono stałej kolejności TTS i odtwarzania poza chronologicznymi znacznikami czasu.

Źródła to `pipeline`, `satellite`, `operator` i `acoustic`. Tylko `operator` lub `acoustic` mogą być źródłem `audible_start`. Każda sesja musi dostarczyć trzy kontrole: `intent_correct`, `action_observed`, `audible`. Każda ma `result` (`pass`, `fail`, `unknown`) i `method`. Wynik nieznany wymaga `none`. Pozostałe poprawne metody to `operator`/`intent_assertion` dla intencji, `operator`/`ha_state` dla działania oraz `operator`/`acoustic` dla słyszalności. Znacznik słyszalnego dźwięku wymaga pozytywnej kontroli słyszalności. Narzędzie sprawdza spójność, nie prawdziwość.

Wymagania mogą włączyć dowolną z trzech kontroli i opcjonalnie `max_audible_ms`. Pominięte lub fałszywe kontrole nie są wymagane: polityka tylko dla API może przejść bez fizycznych dowodów i musi być tak oznaczona. Dołączone przykłady wymagają wszystkich kontroli. Błąd potoku zawsze oznacza niepowodzenie. Brak `protocol_end` oznacza niekompletność. Niepowodzenie obowiązkowej kontroli ma pierwszeństwo przed nieznanymi obserwacjami. Opóźnienie ponad próg oznacza porażkę; brak wymaganego opóźnienia — niekompletność.

## Import przebiegu HA

Adapter przyjmuje jedną **tablicę obiektów zdarzeń**, a nie pełny dziennik WebSocket czy ZIP diagnostyczny. Wyodrębnij treść każdego zdarzenia lokalnie. Obiekty mają dokładnie `type`, `timestamp`, `data`; dane mogą być obiektem lub null. Znaczniki czasu muszą być ISO 8601 ze strefą czasową. Zacznij od `run-start`, zachowaj kolejność chronologiczną i nie mieszaj przebiegów. Powtórzone mapowane etapy są odrzucane.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

Drugie polecenie celowo zwraca 3. `run-end` jest mapowane na `protocol_end`, nie na fizyczny sukces. `tts-end` staje się `tts_ready`, nie słyszalnym dźwiękiem. Wszystkie `data` są odrzucane, łącznie z transkrypcjami, tekstem wejściowym, błędami, URL/tokenami TTS i metadanymi potoku. Zdarzenia początku, postępu i VAD są rozpoznawane, ale nie zachowywane. Przeliczone czasy używają `utc_derived`: odejmowanie wskazań zegara nie jest monotonicznym pomiarem opóźnienia i może zależeć od korekt zegara. Wszystkie trzy kontrole fizyczne/semantyczne pozostają nieznane.

## Raporty i porównywanie

`--format text|json|html|junit` wybiera raport. Przekierowanie powłoki zapisuje wynik we wskazanej lokalnej ścieżce. Samo CLI nigdy nie nadpisuje wejścia. Kody wyjścia: 0 — zapisane wymagania spełnione; 1 — niepowodzenie; 2 — nieprawidłowe wejście/argumenty; 3 — niekompletność. JUnit przedstawia niekompletne sesje jako pominięte; CI nadal musi respektować kod 3.

Grupy JSON używają platformy, scenariusza, zegara i metody pomiaru słyszalności. Nigdy nie traktuj różnych zegarów ani obserwacji ludzkich i akustycznych jako wymiennych pomiarów. p50/p95 używają metody najbliższej rangi. Poniżej 20 próbek p95 to null; 20 jest progiem raportowania, nie dowodem wiarygodności statystycznej. Nieudane sesje z zaobserwowanym dźwiękiem pozostają w populacji próbek opóźnienia, a liczba ich niepowodzeń jest widoczna. Nie wybieraj wyłącznie udanych prób. Surowy dźwięk i transkrypcje nie są eksportowane. Identyfikatory nadal mogą ujawnić informacje, więc je sprawdź.

HTML pokazuje wszystkie sesje i wykres pierwszych 50 obserwacji słyszalnych we wspólnej skali. Czytaj platformę i metodę każdego wiersza; podsumowanie nie jest rankingiem statystycznym. `evidence_verified: false` występuje zawsze. `synthetic: false` oznacza, że autor nie oznaczył przebiegu jako syntetyczny, a nie że sprzęt zweryfikowano niezależnie.

## Zbieranie wartościowych dowodów

Przed próbą określ oczekiwaną intencję i cel. Konsekwentnie definiuj zdarzenie początkowe: żądanie potoku nie musi być początkiem wypowiedzianej frazy. Prowadź osobny zapis prób z wersjami oprogramowania, językiem, warunkami sieciowymi, położeniem mikrofonu i głośnika, metodą obserwacji i liczbą prób. Do precyzyjnego czasu słyszalnego dźwięku używaj odpowiedniego pomiaru akustycznego; nie zastępuj go pierwszym fragmentem sieciowym. Zapisuj niepowodzenia, przekroczenia czasu i brakujące dowody. Pakiet nie wykonuje synchronizacji akustycznej ani zarządzania zgodą.

## Rozwiązywanie problemów

- `object_fields`: porównaj klucze z kanonicznymi danymi testowymi; pełny zrzut diagnostyczny nie jest akceptowany.
- `ha_timestamp` / `time_order`: eksportuj jeden przebieg, uwzględnij strefy czasowe i sprawdź korekty zegara. Nie zmieniaj kolejności zdarzeń, aby sztucznie uzyskać opóźnienie.
- `stage`: etap jest nieznany lub powtórzony; sprawdź, czy połączono dwa przebiegi.
- `audible_origin` / `conflicting_audible`: metadane odtwarzania nie zastępują usłyszenia dźwięku.
- Kod 3 po udanym API: oczekiwany, dopóki nie zapisano wymaganych obserwacji.
- `unsupported_platform`: system nie ma `O_NOFOLLOW` lub `O_NONBLOCK`; użyj środowiska z obiema flagami (Linux albo macOS). Wejście jest odrzucane przed otwarciem zamiast osłabiania kontroli dowiązań symbolicznych czy FIFO.
- `file_size_type`: tylko zwykłe pliki JSON UTF-8, najwyżej 2 MiB. Katalogi, FIFO i dowiązania symboliczne w ostatnim elemencie ścieżki są odrzucane. Dowiązania w katalogach nadrzędnych nie stanowią granicy piaskownicy.
- `number`: brak ujemnych, nieskończonych, logicznych lub przekraczających 12 godzin znaczników czasu.

Błędy wyświetlają przetłumaczone podsumowanie i stabilny kod, nie treść źródła ani lokalne ścieżki. Publiczne przykłady są całkowicie syntetyczne. Przechowuj eksporty poza tą kopią repozytorium, najlepiej w prywatnym katalogu tymczasowym.

## Architektura, tłumaczenia i źródła

![Przepływ offline](../../assets/architecture.svg)

`core.py` odpowiada za czystą walidację, import i ocenę; `cli.py` generuje formaty; `locales/*.json` zawiera cztery katalogi. Testy wymagają zgodności kluczy katalogów. Klucze maszynowe i kody diagnostyczne nie są tłumaczone. Pełne przewodniki obejmują 24 języki dokumentacji ha-homelab; CLI i README pozostają po angielsku, rosyjsku, niemiecku i hiszpańsku. Dodawaj kolejne tłumaczenia referencyjne z testami zgodności i sprawdzonymi przykładami.

Mapowanie protokołu sprawdzono według [dokumentacji Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) i [modeli zdarzeń HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Cykl życia satelity opisuje [oficjalny przewodnik encji](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Te API upstream nie gwarantują weryfikacji akustycznej; jej rozdzielenie tutaj jest decyzją projektową.
