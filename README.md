# Laya INEMA — triagem prática em português

Adaptação do [Laya, da Convai Innovations](https://github.com/NandhaKishorM/laya), com interface local, API, CLI e avaliação reproduzível. O SDK upstream permanece disponível; a aplicação adicional vive em `practical/`.

**[Guia de uso](https://inematds.github.io/laya/guia/)** · **[Curso v2, em repositório separado](https://inematds.github.io/laya-curso/)** · [README upstream preservado](docs/README-UPSTREAM.md)

## Começar

Python 3.10+ recomendado para a aplicação (testado com 3.12). Internet na primeira carga para baixar o checkpoint; CPU funciona, GPU é opcional.

```bash
git clone https://github.com/inematds/laya.git
cd laya
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e . -r practical/requirements.txt
python3 -m practical download
python3 -m practical serve
```

Abra **http://127.0.0.1:8765** no navegador da mesma máquina. Porta ocupada? Use `serve --port 8875`. Para CUDA compatível, use `python3 -m practical --device cuda serve`. O modelo usa a instalação PyTorch da máquina; consulte a distribuição oficial do PyTorch para seu hardware. O guia no GitHub Pages não hospeda a API nem roda pesos no navegador.

```bash
python3 -m practical triage --message "Fui cobrado duas vezes e quero o reembolso."
python3 -m practical --device cuda evaluate --output avaliacao.json
python3 -m practical --model-path /caminho/do/checkpoint triage --message "Quero contratar o plano empresarial."
```

`--device`, `--threshold` e `--model-path` vêm **antes** do subcomando. O caminho local precisa conter `rl_agent_config.json`, `model.safetensors`, tokenizer e configuração do encoder.

## API

```bash
curl http://127.0.0.1:8765/api/health
curl -X POST http://127.0.0.1:8765/api/triage \
  -H 'Content-Type: application/json' \
  -d '{"message":"Fui cobrado duas vezes.","subject":"Cobrança"}'
```

- `answers`: departamento (`choice`), urgência (`score` 0–2), ameaça explícita de cancelamento e pedido explícito de reembolso (`noul`).
- `policy`: destino sugerido, razões de revisão e `automated_action_executed: false`.
- `runtime`: dispositivo efetivo, tokens e tempo de inferência. Não inclui download/carga; a primeira inferência ainda tem aquecimento.
- `422`: entrada inválida ou maior que o espaço disponível em tokens. `503`: modelo indisponível. Falhas não viram previsões falsas.

## O que foi adaptado

- Checkpoint **multilingual explícito** para a fila em português; uma instância residente por processo.
- Proteção contra truncamento silencioso: o tokenizer real verifica se o estado cabe em todas as perguntas.
- Inferência serializada no processo; validação das distribuições, números e categorias antes da política.
- Interface com exemplos, estado de carregamento, erros, leitura do JSON e download voluntário do resultado.
- API local, sem execução de ações externas nem persistência automática dos tickets.
- 16 tickets sintéticos rotulados e relatório com acurácia, baseline, Brier e ECE.

## Evidência e limites

A execução local real em NVIDIA GB10 acertou **13/16 (81,25%)** departamentos. Os erros e distribuições estão em [docs/avaliacao-local.json](docs/avaliacao-local.json). A amostra é pequena, sintética e não valida produção. Brier (soma multiclasses): 0,30835; ECE com top probability e 10 bins: 0,17988.

**Toda saída exige revisão humana.** O limiar 0,85 serve para acrescentar um motivo de revisão; não autoriza automação. Não executamos reembolsos, chamadas de agentes ou mudanças em contas. `act_probability` do upstream não é permissão operacional.

`choice.confidence` é entropia normalizada invertida, não probabilidade de acerto. O multilingual não está calibrado para o seu domínio. O nome `churn_risk` neste esquema significa **ameaça explícita no texto**, não previsão longitudinal de churn. Score é experimental e deve ser conferido.

A primeira carga baixa pesos do Hugging Face. O texto dos tickets é processado nesta máquina. Self-hosted evita tarifa Laya por chamada, mas tem custo de hardware e operação. O servidor liga somente em loopback e é um laboratório local; não inclui autenticação, rate limit distribuído, fila durável ou endpoint público.

## Verificação

```bash
python3 -m pip install httpx
python3 -m unittest discover -s tests/practical -v
python3 tests/test_router.py
python3 tests/test_criteria.py
python3 -m practical --device cuda evaluate --output avaliacao.json
```

Os dois testes upstream são **scripts**, não módulos pytest. O teste `test_local_e2e.py` do upstream requer checkpoints adicionais e não faz parte dessa suíte mínima.

## Proveniência e licença

Base upstream: `42626c348753fbb17572a813127df2278a1ec527`. Adaptação INEMA: **v0.4.4**. [Análise das fontes](docs/ANALISE.md) · [Changelog](CHANGELOG.md) · [Licença Apache 2.0](LICENSE).

Código e pesos continuam atribuídos aos autores originais. Materiais integrais de terceiros (vídeo, transcrição, artigos) ficam no acervo local de pesquisa; o repositório publica síntese autoral, referências e evidências do laboratório. Não foi executado Jev nem treinamento de um novo modelo nesta entrega.
