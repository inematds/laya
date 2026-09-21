# Análise dos materiais — 21/09/2026

## Acervo e cobertura

Os dois textos enviados foram lidos integralmente e as três imagens inspecionadas. O link técnico principal foi clonado integralmente: [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya), commit `42626c348753fbb17572a813127df2278a1ec527`. Foram examinados README, BENCHMARKS, SDK (`agent`, `common`, `router`, `lang`, presets), testes, relatórios de pesquisa e notebook de fine-tuning (19 células extraídas para texto).

O [vídeo](https://www.youtube.com/watch?v=KySbNMsBU70) foi baixado via inemavox em 1080p e transcrito integralmente com Whisper large-v3: cerca de 26min10s, 401 segmentos, inglês. Vídeo e transcrição local em `/home/nmaldaner/projetos/output/laya/fontes/`. A transcrição automática troca ocasionalmente Laya por Leia/Leah e ModernBERT por Modern Bird; nomes técnicos foram normalizados na síntese.

Também foram baixados: artigo do criador no DEV.to (via Jina após 403 da API), fichas dos três checkpoints no Hugging Face, código app.py da demo, metadados PyPI e READMEs dos dois benchmarks independentes de Jev referenciados pelo upstream. Os arquivos de terceiros ficam no acervo local, sem republicação integral no curso. Consulte `fontes-manifesto.json` para hashes. Não fizemos uma varredura recursiva ilimitada de todo link de navegação de cada site.

## Síntese por material

- **Visão geral enviada:** boa estrutura para explicar decisões versus geração e uso em agentes. N0–N4 e LOOP-R são propostas de integração, não recursos já implementados pelo Laya. “Probabilidade” requer definição e avaliação.
- **Comparação enviada:** API gerenciada versus execução própria é um eixo útil. “Gratuito” deve excluir hardware e operação; “pronto” não elimina validação do domínio.
- **Imagens:** linguagem editorial de competição e substituição de LLMs. Foram aproveitadas com contexto; não sustentam conclusões técnicas.
- **Vídeo:** discute lançamento, autoria, arquitetura, exemplos, presets, limites de opções, especialização, calibração, revisão de números e reação comunitária. Relatos sobre financiamento, prioridade científica, comentários e popularidade não foram usados como prova técnica. Não reproduzimos contagens sociais ou uma conclusão sobre autoria científica.
- **Artigo do criador:** explica encoder, marcadores de opções, cabeças e RLCD. Algumas frases sobre inexistência de erros, calibração garantida e comparações são mais fortes que a evidência empírica atual. A escolha de objetivo probabilístico não garante calibração fora do domínio.
- **Fichas e código atuais:** multilingual tem 322M parâmetros totais; inglês/typed têm 421M. Router não seleciona typed automaticamente por padrão. `choice.confidence` usa entropia normalizada; `noul.confidence` tem outra definição.
- **Relatórios de benchmarks:** comparação com Jev é indireta, com protocolos e amostras diferentes. Banking77 menciona 72 versus 77 alternativas. O checkpoint especializado foi ajustado no split de treino do benchmark; isso deve ser declarado e não é, por si, prova de vazamento do teste.
- **Código de inferência:** um lote contém uma sequência por pergunta, não uma única representação gratuita para qualquer quantidade de perguntas. O estado pode ser truncado; nossa camada recusa a perda antes da inferência.
- **Notebook:** fornece caminho para treinamento e calibração; não foi executado. Não afirmamos que a adaptação é um modelo fine-tuned nem que o notebook garante a mesma duração em outro hardware.

## Divergências relevantes

| Material / afirmação | Tratamento na entrega |
|---|---|
| Vídeo menciona backbone multilíngue de ~135M | Curso usa ficha atual: mmBERT-base, 322M totais |
| Números iniciais ~84% vs ~68% | Apresentados como contexto histórico, não placar validado |
| README contém 0,342 e 0,352 em passagens diferentes | Não harmonizamos silenciosamente; em tabelas atuais a ficha multilingual usa 0,342; a tese relevante é desempenho base inferior à baseline nessa tarefa |
| Router “escolhe especializado” | Só por override ou opt-in; leitura do código prevalece |
| “Sem geração = sem alucinação” | Pode errar categoria, evidência e probabilidade; formato correto não prova correção |
| Confiança 95% | Não equivale automaticamente a 95% de acerto |
| Self-hosted = custo zero | Sem tarifa Laya por chamada; infraestrutura continua tendo custo |
| Churn | No esquema, ameaça explícita, não probabilidade longitudinal de cancelamento |

## Escolha prática

Fila de atendimento em português, quatro departamentos e quatro perguntas, checkpoint multilingual explícito. CLI + API + interface local, sem persistência automática de tickets. Entradas longas são recusadas para evitar decisões sobre texto truncado. Distribuições e números são validados. Toda saída vai à revisão humana; nenhuma ação externa é executada.

## Evidência local

16 exemplos sintéticos balanceados; **13/16 departamentos corretos**. Baseline majoritária 25%. Brier soma multiclasses 0,30835; ECE top probability, 10 bins, 0,17988. Erros: pt-03 (sales→billing), pt-08 e pt-16 (other→technical). Preservados integralmente em `avaliacao-local.json`.

GPU NVIDIA GB10, Python 3.12, torch 2.13.0+cu130, transformers 5.14.1. Primeira inferência medida: 1401 ms; seguintes aproximadamente 22–124 ms. Medição não controlada, com aquecimento e outra tarefa GPU na máquina: não extrapolar desempenho, não comparar diretamente com T4. Testes de integração separados verificam limites, API, política e falhas; não confundimos teste mockado com qualidade preditiva.

## Fontes

- https://github.com/NandhaKishorM/laya
- https://www.youtube.com/watch?v=KySbNMsBU70
- https://huggingface.co/convaiinnovations/laya
- https://huggingface.co/convaiinnovations/laya-multilingual
- https://huggingface.co/convaiinnovations/laya-typed-decisions
- https://huggingface.co/spaces/convaiinnovations/laya-demo
- https://dev.to/nandakishor_m_6cc0adfde9f/i-built-non-autoregressive-decision-models-a-year-ago-then-a-frontier-lab-called-it-a-18me
- https://github.com/AbdelStark/jev-benchmarks
- https://github.com/nibzard/decision-model-benchmark
- https://pypi.org/project/laya/
