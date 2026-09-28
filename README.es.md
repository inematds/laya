# Laya INEMA — triage práctica en portugués

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

Adaptación de [Laya, de Convai Innovations](https://github.com/NandhaKishorM/laya), con interfaz local, API, CLI y evaluación reproducible. El SDK upstream sigue disponible; la aplicación adicional está en `practical/`.

**[Guía de uso](https://inematds.github.io/laya/guia/es/)** · **[Curso v2, en un repositorio separado](https://inematds.github.io/laya-curso/)** · [README upstream preservado](docs/README-UPSTREAM.md)

## Empezar

Se recomienda Python 3.10+ para la aplicación (probado con 3.12). Se necesita internet durante la primera carga para descargar el checkpoint; funciona con CPU y la GPU es opcional.

```bash
git clone https://github.com/inematds/laya.git
cd laya
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e . -r practical/requirements.txt
python3 -m practical download
python3 -m practical serve
```

Abre **http://127.0.0.1:8765** en el navegador de la misma máquina. ¿El puerto está ocupado? Usa `serve --port 8875`. Para una instalación compatible con CUDA, usa `python3 -m practical --device cuda serve`. El modelo usa la instalación de PyTorch de la máquina; consulta la distribución oficial de PyTorch para tu hardware. La guía en GitHub Pages no aloja la API ni ejecuta los pesos en el navegador.

```bash
python3 -m practical triage --message "Fui cobrado duas vezes e quero o reembolso."
python3 -m practical --device cuda evaluate --output avaliacao.json
python3 -m practical --model-path /caminho/do/checkpoint triage --message "Quero contratar o plano empresarial."
```

`--device`, `--threshold` y `--model-path` van **antes** del subcomando. La ruta local debe contener `rl_agent_config.json`, `model.safetensors`, el tokenizador y la configuración del encoder.

## API

```bash
curl http://127.0.0.1:8765/api/health
curl -X POST http://127.0.0.1:8765/api/triage \
  -H 'Content-Type: application/json' \
  -d '{"message":"Fui cobrado duas vezes.","subject":"Cobrança"}'
```

- `answers`: departamento (`choice`), urgencia (`score` 0–2), amenaza explícita de cancelación y solicitud explícita de reembolso (`noul`).
- `policy`: destino sugerido, motivos de revisión y `automated_action_executed: false`.
- `runtime`: dispositivo efectivo, tokens y tiempo de inferencia. No incluye la descarga ni la carga; la primera inferencia aún requiere calentamiento.
- `422`: entrada no válida o mayor que el espacio disponible en tokens. `503`: modelo no disponible. Los fallos no se convierten en predicciones falsas.

## Qué se adaptó

- Checkpoint **multilingual explícito** para la cola en portugués; una instancia residente por proceso.
- Protección contra el truncamiento silencioso: el tokenizador real verifica que el estado quepa en todas las preguntas.
- Inferencia serializada en el proceso; validación de las distribuciones, los números y las categorías antes de aplicar la política.
- Interfaz con ejemplos, estado de carga, errores, lectura del JSON y descarga voluntaria del resultado.
- API local, sin ejecutar acciones externas ni guardar tickets automáticamente.
- 16 tickets sintéticos etiquetados e informe con exactitud, baseline, Brier y ECE.

## Evidencia y límites

La ejecución local real en NVIDIA GB10 acertó **13/16 (81,25%)** departamentos. Los errores y las distribuciones están en [docs/avaliacao-local.json](docs/avaliacao-local.json). La muestra es pequeña y sintética, y no valida el uso en producción. Brier (suma multiclase): 0,30835; ECE con la probabilidad máxima y 10 bins: 0,17988.

**Toda salida requiere revisión humana.** El umbral 0,85 sirve para agregar un motivo de revisión; no autoriza la automatización. No ejecutamos reembolsos, llamadas de agentes ni cambios en cuentas. `act_probability` del upstream no es un permiso operativo.

`choice.confidence` es la entropía normalizada invertida, no la probabilidad de acertar. El multilingual no está calibrado para tu dominio. El nombre `churn_risk` en este esquema significa **amenaza explícita en el texto**, no una predicción longitudinal de churn. El score es experimental y debe verificarse.

La primera carga descarga pesos de Hugging Face. El texto de los tickets se procesa en esta máquina. El autoalojamiento evita la tarifa de Laya por llamada, pero tiene costos de hardware y operación. El servidor escucha solo en loopback y es un laboratorio local; no incluye autenticación, límite de solicitudes distribuido, cola duradera ni endpoint público.

## Verificación

```bash
python3 -m pip install httpx
python3 -m unittest discover -s tests/practical -v
python3 tests/test_router.py
python3 tests/test_criteria.py
python3 -m practical --device cuda evaluate --output avaliacao.json
```

Las dos pruebas upstream son **scripts**, no módulos pytest. La prueba upstream `test_local_e2e.py` requiere checkpoints adicionales y no forma parte de esta suite mínima.

## Procedencia y licencia

Base upstream: `42626c348753fbb17572a813127df2278a1ec527`. Adaptación INEMA: **v0.4.4**. [Análisis de las fuentes](docs/ANALISE.md) · [Changelog](CHANGELOG.md) · [Licencia Apache 2.0](LICENSE).

El código y los pesos siguen atribuidos a sus autores originales. Los materiales integrales de terceros (video, transcripción, artículos) se conservan en el archivo local de investigación; el repositorio publica una síntesis original, referencias y evidencias del laboratorio. En esta entrega no se ejecutó Jev ni se entrenó un modelo nuevo.
