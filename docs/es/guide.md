# Evaluación de escenarios de voz registrados

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

## Instalación y límites

Instale desde una copia del repositorio con `python3 -m pip install .` en un entorno virtual. Se admite Python 3.11+. No hay dependencias de ejecución aparte de Python. `assist-lab --help --lang en` enumera los comandos; también funcionan `ru`, `de` y `es`. La entrada mediante módulo es `python3 -m assist_scenario_lab`.

La carga de archivos necesita los indicadores del sistema operativo `O_NOFOLLOW` y `O_NONBLOCK`, disponibles en Linux y macOS. Si falta cualquiera, la CLI devuelve el código 2 con `unsupported_platform` antes de abrir la entrada. Las API de evaluación e importación de Python en memoria no necesitan esos indicadores.

Este es un evaluador sin conexión, no firmware de satélite, detector acústico, recolector en vivo, integración de HA ni banco de pruebas completo. Realice las pruebas de aceptación reales del producto con las herramientas del firmware adecuadas. Entregue a esta herramienta las evidencias acotadas resultantes solo después de revisar su privacidad.

## Entrada canónica

Empiece con `examples/synthetic-pass.json`. La raíz requiere `schema: assist-scenario-lab/v1`, el booleano `synthetic`, un objeto `requirements` y entre 1 y 500 `sessions`. Se rechazan campos desconocidos. Una sesión tiene un `id` único, además de `platform`, `scenario`, `clock`, `events` y `checks`. Los identificadores tienen entre 1 y 64 letras ASCII, dígitos, guiones bajos o guiones; empiezan por letra o dígito. Use seudónimos, no nombres de habitaciones, direcciones ni identificadores de dispositivos.

`clock` es `relative_monotonic` o `utc_derived`. Los eventos contienen `stage`, `at_ms`, `origin`. Los tiempos son finitos, no negativos, como máximo de 12 horas y están ordenados de forma no decreciente. El primer evento es `request` en cero. Cada etapa aparece una vez. Etapas admitidas: `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Los distintos pipelines pueden transmitir en flujo; deliberadamente no hay un orden fijo entre TTS y reproducción más allá de las marcas temporales cronológicas.

Los orígenes son `pipeline`, `satellite`, `operator` y `acoustic`. Solo `operator` o `acoustic` pueden originar `audible_start`. Cada sesión debe aportar las tres comprobaciones: `intent_correct`, `action_observed`, `audible`. Cada una tiene `result` (`pass`, `fail`, `unknown`) y `method`. Un resultado desconocido requiere `none`. Los demás métodos válidos son `operator`/`intent_assertion` para intención, `operator`/`ha_state` para acción y `operator`/`acoustic` para audibilidad. Una marca temporal audible requiere una comprobación de audibilidad aprobada. La herramienta verifica coherencia, no veracidad.

Los requisitos pueden activar cualquiera de las tres comprobaciones y, opcionalmente, `max_audible_ms`. Las comprobaciones omitidas o falsas no son obligatorias: una política solo de API puede aprobar sin evidencia física y debe etiquetarse así. Los ejemplos incluidos exigen todas las comprobaciones. Un error del pipeline siempre causa fallo. La ausencia de `protocol_end` implica un resultado incompleto. Un fallo obligatorio prevalece sobre observaciones desconocidas. La latencia por encima del umbral falla; la ausencia de latencia requerida es incompleta.

## Importar una ejecución de HA

El adaptador consume un **array de objetos de evento**, no un registro WebSocket completo ni un ZIP de diagnóstico. Extraiga localmente el cuerpo de cada evento. Los objetos tienen exactamente `type`, `timestamp`, `data`; los datos pueden ser un objeto o null. Las marcas temporales deben ser ISO 8601 con zona horaria. Empiece con `run-start`, conserve el orden cronológico y no mezcle ejecuciones. Se rechazan etapas mapeadas repetidas.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

El segundo comando devuelve 3 de forma intencionada. `run-end` se convierte en `protocol_end`, no en éxito físico. `tts-end` se convierte en `tts_ready`, no en sonido audible. Se descartan todos los `data`, incluidos transcripciones, texto de entrada, errores, URL/tokens TTS y metadatos del pipeline. Los eventos de inicio, progreso y VAD se reconocen pero no se conservan. Los tiempos convertidos usan `utc_derived`: restar horas del reloj no es una medición monótona de latencia y puede verse afectada por ajustes del reloj. Las tres comprobaciones físicas/semánticas siguen siendo desconocidas.

## Informes y comparación

`--format text|json|html|junit` elige el informe. La redirección del shell escribe el resultado en la ruta local elegida. La CLI nunca sobrescribe por sí misma una entrada. Códigos de salida: 0, requisitos registrados satisfechos; 1, fallo; 2, entrada/argumentos no válidos; 3, incompleto. JUnit representa las sesiones incompletas como omitidas; CI debe seguir respetando el código 3.

Los grupos JSON usan plataforma + escenario + reloj + método de medición audible. Nunca trate distintos relojes, u observaciones humanas y acústicas, como mediciones intercambiables. p50/p95 usan el rango más próximo. p95 es null por debajo de 20 muestras; 20 es un umbral de presentación, no evidencia de confianza estadística. Las sesiones fallidas con audio observado permanecen en la población de muestras de latencia y su número de fallos sigue visible. No seleccione solo intentos aprobados. No se exportan audio bruto ni transcripciones. Los identificadores aún pueden revelar información, así que revíselos.

El HTML enumera todas las sesiones y grafica las primeras 50 observaciones audibles usando una escala común. Lea la plataforma y el método de cada fila; la vista general no es una clasificación estadística. Siempre está presente `evidence_verified: false`. `synthetic: false` significa que el autor no marcó la ejecución como sintética, no que el hardware se haya validado de forma independiente.

## Recoger evidencia útil

Defina la intención esperada y el objetivo antes de cada intento. Especifique coherentemente el evento inicial: la solicitud del pipeline no es necesariamente el comienzo de la frase hablada. Mantenga un registro externo con versiones del software, idioma, condiciones de red, ubicación de micrófono y altavoz, método de observación y número de intentos. Use una medición acústica adecuada para cronometrar con precisión el sonido audible; no la sustituya por el primer fragmento de red. Registre fallos, tiempos agotados y evidencias ausentes. Este paquete no realiza sincronización acústica ni gestión del consentimiento.

## Solución de problemas

- `object_fields`: compare las claves con el conjunto canónico; no se acepta un volcado de diagnóstico completo.
- `ha_timestamp` / `time_order`: exporte una ejecución, incluya zonas horarias y revise correcciones del reloj. No reordene eventos para fabricar latencia.
- `stage`: una etapa es desconocida o está duplicada; compruebe si se concatenaron dos ejecuciones.
- `audible_origin` / `conflicting_audible`: los metadatos de reproducción no sustituyen el hecho de oír sonido.
- Código 3 después de una API exitosa: se espera hasta registrar las observaciones requeridas.
- `unsupported_platform`: el sistema carece de `O_NOFOLLOW` o `O_NONBLOCK`; use un entorno que ofrezca ambos (Linux o macOS). La entrada se rechaza antes de abrirla en vez de debilitar los controles de enlaces simbólicos o FIFO.
- `file_size_type`: solo archivos JSON UTF-8 normales, de hasta 2 MiB. Se rechazan directorios, FIFO y enlaces simbólicos en el último componente. Los enlaces de directorios padres no son una frontera de sandbox.
- `number`: no se permiten marcas temporales negativas, no finitas, booleanas ni superiores a 12 horas.

Los errores muestran un resumen traducido y un código estable, no el contenido original ni rutas locales. Los ejemplos públicos son completamente sintéticos. Guarde las exportaciones fuera de esta copia del repositorio, preferiblemente en un directorio temporal privado.

## Arquitectura, traducciones y fuentes

![Flujo sin conexión](../../assets/architecture.svg)

`core.py` gestiona validación, importación y evaluación puras; `cli.py` presenta los formatos; `locales/*.json` contiene cuatro catálogos. Las pruebas exigen paridad de claves entre catálogos. No se traducen las claves de máquina ni los códigos de diagnóstico. Las guías completas cubren los 24 idiomas de documentación de ha-homelab; CLI y README siguen en inglés, ruso, alemán y español. Aporte traducciones de referencia adicionales con pruebas de paridad y ejemplos revisados.

El mapeo del protocolo se verificó con la [documentación de Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) y los [modelos de eventos de HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). El ciclo de vida del satélite se documenta en la [guía oficial de la entidad](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Estas API upstream no prometen verificación acústica; separarla aquí es una decisión de diseño.
