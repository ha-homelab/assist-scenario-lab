# Valutazione di scenari vocali registrati

<!-- language-navigation:start -->
<p dir="ltr">
<a href="Guide.md" lang="en" dir="ltr">English</a> ·
<a href="Guide-ar.md" lang="ar" dir="rtl">العربية</a> ·
<a href="Guide-bn.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="Guide-cs.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="Guide-de.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="Guide-es.md" lang="es" dir="ltr">Español</a> ·
<a href="Guide-fa.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="Guide-fr.md" lang="fr" dir="ltr">Français</a> ·
<a href="Guide-he.md" lang="he" dir="rtl">עברית</a> ·
<a href="Guide-hi.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="Guide-id.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="Guide-it.md" lang="it" dir="ltr">Italiano</a> ·
<a href="Guide-ja.md" lang="ja" dir="ltr">日本語</a> ·
<a href="Guide-ko.md" lang="ko" dir="ltr">한국어</a> ·
<a href="Guide-nl.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="Guide-pl.md" lang="pl" dir="ltr">Polski</a> ·
<a href="Guide-pt.md" lang="pt" dir="ltr">Português</a> ·
<a href="Guide-RU.md" lang="ru" dir="ltr">Русский</a> ·
<a href="Guide-th.md" lang="th" dir="ltr">ไทย</a> ·
<a href="Guide-tr.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="Guide-uk.md" lang="uk" dir="ltr">Українська</a> ·
<a href="Guide-vi.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="Guide-zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="Guide-zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

## Installazione e limiti

Installare da una copia del repository con `python3 -m pip install .` in un ambiente virtuale. È supportato Python 3.11+. Non esistono dipendenze di esecuzione oltre a Python. `assist-lab --help --lang en` elenca i comandi; funzionano anche `ru`, `de` ed `es`. L'avvio come modulo è `python3 -m assist_scenario_lab`.

Il caricamento dei file richiede i flag del sistema operativo `O_NOFOLLOW` e `O_NONBLOCK`, disponibili su Linux e macOS. Se ne manca uno, la CLI termina con codice 2 e `unsupported_platform` prima di aprire l'input. Le API Python di valutazione e importazione in memoria non richiedono questi flag.

Questo è un valutatore offline, non un firmware per satelliti, un rilevatore acustico, un raccoglitore in tempo reale, un'integrazione HA o un benchmark completo. Eseguire le vere prove di accettazione del prodotto con gli strumenti firmware appropriati. Fornire a questo strumento le evidenze risultanti, di dimensione limitata, solo dopo averne verificato la riservatezza.

## Input canonico

Partire da `examples/synthetic-pass.json`. La radice richiede `schema: assist-scenario-lab/v1`, il booleano `synthetic`, un oggetto `requirements` e da 1 a 500 `sessions`. I campi sconosciuti sono rifiutati. Una sessione contiene un `id` univoco, oltre a `platform`, `scenario`, `clock`, `events` e `checks`. Gli identificatori sono composti da 1–64 lettere ASCII, cifre, trattini bassi o trattini e iniziano con una lettera o cifra. Usare pseudonimi, non nomi di stanze, indirizzi o identificatori di dispositivi.

`clock` è `relative_monotonic` oppure `utc_derived`. Gli eventi contengono `stage`, `at_ms`, `origin`. I tempi sono finiti, non negativi, al massimo di 12 ore e ordinati in modo non decrescente. Il primo evento è `request` a zero. Ogni fase compare una sola volta. Fasi supportate: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Pipeline diverse possono operare in streaming; non viene quindi imposto un ordine fisso tra TTS e riproduzione oltre alla cronologia dei timestamp.

Le origini sono `pipeline`, `satellite`, `operator` e `acoustic`. Solo `operator` o `acoustic` possono originare `audible_start`. Ogni sessione deve fornire tutte e tre le verifiche: `intent_correct`, `action_observed`, `audible`. Ciascuna ha `result` (`pass`, `fail`, `unknown`) e `method`. Un risultato sconosciuto richiede `none`. Gli altri metodi validi sono `operator`/`intent_assertion` per l'intento, `operator`/`ha_state` per l'azione e `operator`/`acoustic` per l'udibilità. Un timestamp udibile richiede una verifica di udibilità superata. Lo strumento verifica la coerenza, non la verità.

I requisiti possono abilitare qualsiasi delle tre verifiche e, facoltativamente, `max_audible_ms`. Le verifiche omesse o false non sono obbligatorie: una politica limitata alle API può passare senza prove fisiche e deve essere indicata come tale. Gli esempi inclusi richiedono tutte le verifiche. Un errore della pipeline causa sempre un fallimento. L'assenza di `protocol_end` significa incompletezza. Il fallimento di un requisito prevale sulle osservazioni sconosciute. Una latenza oltre soglia fallisce; l'assenza della latenza richiesta è incompleta.

## Importare un'esecuzione HA

L'adattatore accetta un **array di oggetti evento**, non un intero log WebSocket o uno ZIP diagnostico. Estrarre localmente il corpo di ciascun evento. Gli oggetti hanno esattamente `type`, `timestamp`, `data`; i dati possono essere un oggetto o null. I timestamp devono essere ISO 8601 con fuso orario. Iniziare con `run-start`, mantenere l'ordine cronologico e non mescolare esecuzioni. Le fasi mappate ripetute sono rifiutate.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

Il secondo comando restituisce volutamente 3. `run-end` diventa `protocol_end`, non successo fisico. `tts-end` diventa `tts_ready`, non suono udibile. Tutti i `data` vengono eliminati, comprese trascrizioni, testo in ingresso, errori, URL/token TTS e metadati della pipeline. Gli eventi di inizio, avanzamento e VAD sono riconosciuti ma non conservati. I tempi convertiti usano `utc_derived`: sottrarre orari non è una misurazione monotona della latenza e può risentire delle correzioni dell'orologio. Tutte e tre le verifiche fisiche/semantiche restano sconosciute.

## Rapporti e confronto

`--format text|json|html|junit` sceglie il rapporto. La redirezione della shell scrive il risultato nel percorso locale scelto. La CLI non sovrascrive mai autonomamente un input. Codici di uscita: 0, requisiti registrati soddisfatti; 1, fallimento; 2, input/argomenti non validi; 3, incompleto. JUnit rappresenta le sessioni incomplete come saltate; la CI deve comunque rispettare il codice 3.

I gruppi JSON usano piattaforma + scenario + orologio + metodo di temporizzazione udibile. Non confrontare orologi diversi o osservazioni umane e acustiche come misurazioni intercambiabili. p50/p95 usano il rango più vicino. p95 è null sotto 20 campioni; 20 è una soglia di presentazione, non una prova di affidabilità statistica. Le sessioni fallite con audio osservato restano nella popolazione di campioni della latenza e il loro conteggio dei fallimenti resta visibile. Non selezionare solo le prove riuscite. Non vengono esportati audio grezzo o trascrizioni. Gli identificatori possono comunque rivelare informazioni: esaminarli.

L'HTML elenca tutte le sessioni e rappresenta graficamente le prime 50 osservazioni udibili su una scala condivisa. Leggere piattaforma e metodo di ogni riga; la panoramica non è una classifica statistica. `evidence_verified: false` è sempre presente. `synthetic: false` significa che l'autore non ha marcato l'esecuzione come sintetica, non che l'hardware sia stato validato indipendentemente.

## Raccogliere evidenze significative

Definire intento atteso e destinazione prima di una prova. Specificare coerentemente l'evento iniziale: la richiesta della pipeline non coincide necessariamente con l'inizio della frase pronunciata. Conservare un registro esterno con versioni software, lingua, condizioni di rete, posizione di microfono e altoparlante, metodo di osservazione e numero di prove. Per una temporizzazione precisa del suono udibile usare una misura acustica adatta; non sostituirla con il primo frammento di rete. Registrare fallimenti, timeout ed evidenze mancanti. Questo pacchetto non esegue sincronizzazione acustica o gestione del consenso.

## Risoluzione dei problemi

- `object_fields`: confrontare le chiavi con il fixture canonico; un dump diagnostico completo non è accettato.
- `ha_timestamp` / `time_order`: esportare una sola esecuzione, includere i fusi orari, verificare le correzioni dell'orologio. Non riordinare gli eventi per fabbricare una latenza.
- `stage`: una fase è sconosciuta o duplicata; verificare se due esecuzioni sono state concatenate.
- `audible_origin` / `conflicting_audible`: i metadati di riproduzione non possono sostituire l'ascolto del suono.
- Codice 3 dopo un'API riuscita: previsto finché non si registrano le osservazioni richieste.
- `unsupported_platform`: manca `O_NOFOLLOW` o `O_NONBLOCK`; usare un ambiente che fornisca entrambi (Linux o macOS). L'input viene rifiutato prima dell'apertura, senza indebolire i controlli su link simbolici o FIFO.
- `file_size_type`: solo normali file JSON UTF-8, massimo 2 MiB. Directory, FIFO e link simbolici nell'ultimo componente sono rifiutati. I link nelle directory superiori non costituiscono un confine di sandbox.
- `number`: nessun timestamp negativo, non finito, booleano o superiore a 12 ore.

Gli errori mostrano un riepilogo tradotto e un codice stabile, non il contenuto sorgente o i percorsi locali. Gli esempi pubblici sono interamente sintetici. Conservare le esportazioni fuori da questa copia del repository, preferibilmente in una directory temporanea privata.

## Architettura, traduzioni e fonti

![Flusso offline](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` gestisce validazione, importazione e valutazione pure; `cli.py` genera i formati; `locales/*.json` contiene quattro cataloghi. I test richiedono parità delle chiavi dei cataloghi. Le chiavi macchina e i codici diagnostici non sono tradotti. Le guide complete coprono le 24 lingue della documentazione ha-homelab; CLI e README restano in inglese, russo, tedesco e spagnolo. Contribuire con altre traduzioni di riferimento, test di parità ed esempi revisionati.

La mappatura del protocollo è stata verificata sulla [documentazione Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) e sui [modelli degli eventi HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Il ciclo di vita del satellite è documentato nella [guida ufficiale dell'entità](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Queste API upstream non promettono verifica acustica; separarla qui è una scelta progettuale.
