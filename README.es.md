# Assist Scenario Lab

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md)

Evalúa sesiones de voz registradas de Home Assistant sin confundir el final de una llamada API con una acción correcta o una respuesta audible. Lee JSON local y genera texto, JSON, HTML o JUnit. No se conecta a Home Assistant ni controla dispositivos.

**Versión beta: 0.1.1b2. Todos los tiempos incluidos son sintéticos.** Esta versión no ha comparado altavoces físicamente. Las observaciones son declaraciones del archivo; `evidence_verified` siempre es false.

![Tres niveles de evidencia](assets/evidence-layers.svg)


[![Informe sintético de escenarios de voz en perspectiva](assets/report-hero.png)](assets/report-preview.png)

El informe HTML real generado con los ejemplos sintéticos del proyecto, no una medición del rendimiento de dispositivos. Haz clic para abrir el original sin cambios.

## Instalación y uso

Se necesita Python 3.11 o posterior. Desde el repositorio descargado:

La carga de archivos requiere los indicadores del sistema operativo `O_NOFOLLOW` y `O_NONBLOCK`, disponibles en Linux y macOS. Si falta cualquiera, la CLI termina con código 2 y `unsupported_platform` antes de abrir la entrada. Las API de Python para evaluar e importar datos en memoria no requieren estos indicadores.

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install .
assist-lab evaluate examples/synthetic-pass.json --lang es
assist-lab evaluate examples/synthetic-pass.json --format html --lang es > /tmp/assist-report.html
assist-lab evaluate examples/synthetic-incomplete.json --lang es
```

El último comando termina intencionadamente con **3**: finalizó el protocolo, pero no se confirmó el sonido. **0** indica requisitos cumplidos por los datos declarados, **1** un fallo y **2** una entrada inválida. Un resultado físico desconocido no se convierte en éxito.

## Funciones y límites

Esquema estricto con límites de tamaño, métodos de observación explícitos y umbrales de latencia. El adaptador sin conexión importa los eventos de una ejecución de HA y descarta todos sus datos, incluidos textos y tokens de audio. Los resúmenes separan plataforma, escenario, reloj y método. p95 requiere al menos 20 observaciones; es un umbral de visualización, no una garantía de confianza estadística.

La CLI, ayuda e informes están disponibles en español, inglés, ruso y alemán. Los códigos JSON no cambian con el idioma. La referencia técnica completa está disponible en 24 idiomas, incluido el [español](docs/es/guide.md). El [índice de idiomas y las instrucciones de mantenimiento](docs/translations.md) describen toda la cobertura; este README español sigue siendo una introducción funcional.

![Latencias sintéticas, no comparación de productos](assets/synthetic-latency.svg)

[Wiki](wiki/Home.md) · [Contribuciones y traducciones](CONTRIBUTING.md) · [Seguridad](SECURITY.md) · [Cambios](CHANGELOG.md)

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 tools/render_docs.py
```

Licencia MIT. Proyecto independiente, no es un componente oficial de Home Assistant.
