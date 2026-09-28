# Laya INEMA — practical triage in Portuguese

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

An adaptation of [Laya by Convai Innovations](https://github.com/NandhaKishorM/laya), with a local interface, API, CLI, and reproducible evaluation. The upstream SDK remains available; the additional application lives in `practical/`.

**[User guide](https://inematds.github.io/laya/guia/en/)** · **[Course v2, in a separate repository](https://inematds.github.io/laya-curso/)** · [Preserved upstream README](docs/README-UPSTREAM.md)

## Getting Started

Python 3.10+ is recommended for the application (tested with 3.12). Internet access is needed on first load to download the checkpoint; CPU works, GPU is optional.

```bash
git clone https://github.com/inematds/laya.git
cd laya
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e . -r practical/requirements.txt
python3 -m practical download
python3 -m practical serve
```

Open **http://127.0.0.1:8765** in a browser on the same machine. Port already in use? Use `serve --port 8875`. For a compatible CUDA setup, use `python3 -m practical --device cuda serve`. The model uses the machine's PyTorch installation; consult the official PyTorch distribution for your hardware. The GitHub Pages guide does not host the API or run model weights in the browser.

```bash
python3 -m practical triage --message "Fui cobrado duas vezes e quero o reembolso."
python3 -m practical --device cuda evaluate --output avaliacao.json
python3 -m practical --model-path /caminho/do/checkpoint triage --message "Quero contratar o plano empresarial."
```

`--device`, `--threshold`, and `--model-path` go **before** the subcommand. The local path must contain `rl_agent_config.json`, `model.safetensors`, the tokenizer, and the encoder configuration.

## API

```bash
curl http://127.0.0.1:8765/api/health
curl -X POST http://127.0.0.1:8765/api/triage \
  -H 'Content-Type: application/json' \
  -d '{"message":"Fui cobrado duas vezes.","subject":"Cobrança"}'
```

- `answers`: department (`choice`), urgency (`score` 0–2), explicit cancellation threat, and explicit refund request (`noul`).
- `policy`: suggested destination, review reasons, and `automated_action_executed: false`.
- `runtime`: effective device, tokens, and inference time. Does not include download/load; the first inference still has a warm-up period.
- `422`: invalid input or input larger than the available token space. `503`: model unavailable. Failures do not become false predictions.

## What Was Adapted

- **Explicitly multilingual** checkpoint for the Portuguese queue; one resident instance per process.
- Protection against silent truncation: the actual tokenizer checks whether the state fits in every question.
- Serialized inference in the process; distributions, numbers, and categories are validated before applying policy.
- Interface with examples, loading state, errors, JSON viewing, and voluntary result download.
- Local API, with no execution of external actions or automatic ticket persistence.
- 16 labeled synthetic tickets and a report with accuracy, baseline, Brier, and ECE.

## Evidence and Limitations

A real local run on NVIDIA GB10 correctly classified **13/16 (81,25%)** of departments. Errors and distributions are in [docs/avaliacao-local.json](docs/avaliacao-local.json). The sample is small and synthetic, and does not validate production use. Brier (multiclass sum): 0,30835; ECE with top probability and 10 bins: 0,17988.

**All output requires human review.** The 0.85 threshold adds a review reason; it does not authorize automation. We do not issue refunds, call agents, or make account changes. Upstream `act_probability` is not operational permission.

`choice.confidence` is inverted normalized entropy, not the probability of being correct. The multilingual model is not calibrated for your domain. In this schema, `churn_risk` means an **explicit threat in the text**, not a longitudinal churn prediction. The score is experimental and should be checked.

The first load downloads weights from Hugging Face. Ticket text is processed on this machine. Self-hosting avoids per-call Laya fees, but has hardware and operating costs. The server binds only to loopback and is a local lab; it does not include authentication, distributed rate limiting, a durable queue, or a public endpoint.

## Verification

```bash
python3 -m pip install httpx
python3 -m unittest discover -s tests/practical -v
python3 tests/test_router.py
python3 tests/test_criteria.py
python3 -m practical --device cuda evaluate --output avaliacao.json
```

The two upstream tests are **scripts**, not pytest modules. The upstream `test_local_e2e.py` test requires additional checkpoints and is not part of this minimal suite.

## Provenance and License

Upstream base: `42626c348753fbb17572a813127df2278a1ec527`. INEMA adaptation: **v0.4.4**. [Source analysis](docs/ANALISE.md) · [Changelog](CHANGELOG.md) · [Apache 2.0 License](LICENSE).

Code and weights remain attributed to their original authors. Complete third-party materials (videos, transcripts, articles) are kept in the local research archive; the repository publishes an original summary, references, and lab evidence. Jev was not run, and no new model was trained for this release.
