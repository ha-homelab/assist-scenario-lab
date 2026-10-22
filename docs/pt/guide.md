# Avaliação de cenários de voz registrados

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

## Instalação e limites

Instale a partir de uma cópia do repositório com `python3 -m pip install .` em um ambiente virtual. Há suporte a Python 3.11+. Não existem dependências de execução além do Python. `assist-lab --help --lang en` lista os comandos; `ru`, `de` e `es` também funcionam. A entrada pelo módulo é `python3 -m assist_scenario_lab`.

O carregamento de arquivos exige as flags do sistema operacional `O_NOFOLLOW` e `O_NONBLOCK`, disponíveis no Linux e macOS. Sem qualquer uma delas, a CLI retorna código 2 com `unsupported_platform` antes de abrir a entrada. As APIs Python de avaliação e importação em memória não exigem essas flags.

Este é um avaliador offline, não um firmware de satélite, detector acústico, coletor em tempo real, integração HA ou benchmark completo. Execute os testes reais de aceitação do produto com as ferramentas de firmware apropriadas. Forneça a esta ferramenta as evidências resultantes, de tamanho limitado, somente após revisar a privacidade.

## Entrada canônica

Comece por `examples/synthetic-pass.json`. A raiz exige `schema: assist-scenario-lab/v1`, o booleano `synthetic`, um objeto `requirements` e entre 1 e 500 `sessions`. Campos desconhecidos são rejeitados. Uma sessão tem um `id` exclusivo, além de `platform`, `scenario`, `clock`, `events` e `checks`. Os identificadores têm de 1 a 64 letras ASCII, dígitos, sublinhados ou hífens e começam com letra ou dígito. Use pseudônimos, não nomes de cômodos, endereços ou identificadores de dispositivos.

`clock` é `relative_monotonic` ou `utc_derived`. Eventos contêm `stage`, `at_ms`, `origin`. Os tempos são finitos, não negativos, limitados a 12 horas e ordenados sem decrescer. O primeiro evento é `request` em zero. Cada etapa ocorre uma vez. Etapas suportadas: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Pipelines diferentes podem transmitir em fluxo; por isso, intencionalmente não há ordem fixa entre TTS e reprodução além dos timestamps cronológicos.

As origens são `pipeline`, `satellite`, `operator` e `acoustic`. Somente `operator` ou `acoustic` podem originar `audible_start`. Cada sessão deve fornecer as três verificações: `intent_correct`, `action_observed`, `audible`. Cada uma tem `result` (`pass`, `fail`, `unknown`) e `method`. Um resultado desconhecido exige `none`. Os outros métodos válidos são `operator`/`intent_assertion` para intenção, `operator`/`ha_state` para ação e `operator`/`acoustic` para audibilidade. Um timestamp audível exige uma verificação de audibilidade aprovada. A ferramenta verifica consistência, não veracidade.

Os requisitos podem ativar qualquer uma das três verificações e, opcionalmente, `max_audible_ms`. Verificações omitidas ou falsas não são obrigatórias: uma política somente de API pode passar sem evidência física e deve ser identificada assim. Os exemplos incluídos exigem todas as verificações. Um erro do pipeline sempre falha. A ausência de `protocol_end` indica incompletude. Uma falha obrigatória prevalece sobre observações desconhecidas. Latência acima do limite falha; ausência de latência obrigatória é incompleta.

## Importar uma execução do HA

O adaptador consome um **array de objetos de evento**, não um log WebSocket completo nem um ZIP de diagnóstico. Extraia localmente o corpo de cada evento. Os objetos têm exatamente `type`, `timestamp`, `data`; os dados podem ser um objeto ou null. Os timestamps devem ser ISO 8601 com fuso horário. Comece por `run-start`, preserve a ordem cronológica e não misture execuções. Etapas mapeadas repetidas são rejeitadas.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

O segundo comando retorna 3 intencionalmente. `run-end` vira `protocol_end`, não sucesso físico. `tts-end` vira `tts_ready`, não som audível. Todos os `data` são descartados, incluindo transcrições, texto de entrada, erros, URLs/tokens de TTS e metadados do pipeline. Eventos de início, progresso e VAD são reconhecidos, mas não retidos. Os tempos convertidos usam `utc_derived`: subtrair horários não é uma medição monotônica de latência e pode sofrer efeitos de ajustes do relógio. As três verificações físicas/semânticas permanecem desconhecidas.

## Relatórios e comparação

`--format text|json|html|junit` escolhe o relatório. O redirecionamento do shell grava o resultado no caminho local escolhido. A CLI nunca sobrescreve uma entrada por conta própria. Códigos de saída: 0, requisitos registrados satisfeitos; 1, falha; 2, entrada/argumentos inválidos; 3, incompleto. JUnit representa sessões incompletas como ignoradas; a CI ainda deve respeitar o código 3.

Os grupos JSON usam plataforma + cenário + relógio + método de medição audível. Nunca trate relógios diferentes, ou observações humanas e acústicas, como medições intercambiáveis. p50/p95 usam o método do posto mais próximo. p95 é null abaixo de 20 amostras; 20 é um limiar de apresentação, não evidência de confiança estatística. Sessões com falha e áudio observado permanecem na população de amostras de latência e sua contagem de falhas continua visível. Não selecione apenas tentativas aprovadas. Áudio bruto e transcrições não são exportados. Identificadores ainda podem revelar informações, portanto revise-os.

O HTML lista todas as sessões e traça as primeiras 50 observações audíveis em uma escala comum. Leia a plataforma e o método de cada linha; a visão geral não é um ranking estatístico. `evidence_verified: false` está sempre presente. `synthetic: false` significa que o autor não marcou a execução como sintética, não que o hardware foi validado de forma independente.

## Coletar evidências relevantes

Defina a intenção esperada e o alvo antes de executar uma tentativa. Especifique consistentemente o evento inicial: a solicitação do pipeline não é necessariamente o início da frase falada. Mantenha um registro externo com versões do software, idioma, condições de rede, posição do microfone e alto-falante, método de observação e número de tentativas. Use uma medição acústica adequada para cronometrar precisamente o som audível; não a substitua pelo primeiro fragmento de rede. Registre falhas, tempos esgotados e evidências ausentes. Este pacote não realiza sincronização acústica nem gestão de consentimento.

## Solução de problemas

- `object_fields`: compare as chaves com o fixture canônico; um dump completo de diagnóstico não é aceito.
- `ha_timestamp` / `time_order`: exporte uma execução, inclua fusos horários e examine correções do relógio. Não reordene eventos para fabricar uma latência.
- `stage`: uma etapa é desconhecida ou duplicada; verifique se duas execuções foram concatenadas.
- `audible_origin` / `conflicting_audible`: metadados de reprodução não substituem ouvir o som.
- Código 3 após uma API bem-sucedida: esperado até registrar as observações obrigatórias.
- `unsupported_platform`: o sistema não tem `O_NOFOLLOW` ou `O_NONBLOCK`; use um ambiente que forneça ambos (Linux ou macOS). A entrada é rejeitada antes de abrir, em vez de enfraquecer as verificações de links simbólicos ou FIFO.
- `file_size_type`: apenas arquivos JSON UTF-8 regulares, de até 2 MiB. Diretórios, FIFOs e links simbólicos no último componente são rejeitados. Links em diretórios ancestrais não são uma fronteira de sandbox.
- `number`: não são permitidos timestamps negativos, não finitos, booleanos ou acima de 12 horas.

Os erros imprimem um resumo traduzido e um código estável, não o conteúdo da origem nem caminhos locais. Os exemplos públicos são totalmente sintéticos. Mantenha exportações fora desta cópia do repositório, preferencialmente em um diretório temporário privado.

## Arquitetura, traduções e fontes

![Fluxo offline](../../assets/architecture.svg)

`core.py` faz validação, importação e avaliação puras; `cli.py` renderiza os formatos; `locales/*.json` contém quatro catálogos. Os testes exigem paridade entre suas chaves. Chaves de máquina e códigos de diagnóstico não são traduzidos. Os guias completos abrangem os 24 idiomas de documentação de ha-homelab; CLI e README continuam em inglês, russo, alemão e espanhol. Contribua com traduções de referência adicionais, testes de paridade e exemplos revisados.

O mapeamento do protocolo foi conferido com a [documentação do Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) e os [modelos de eventos do HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). O ciclo de vida do satélite está documentado no [guia oficial da entidade](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Essas APIs upstream não prometem verificação acústica; separá-la aqui é uma decisão de projeto.
