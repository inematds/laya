# Validação — 2026-09-21

- `python3 -m unittest discover -s tests/practical -v`: **14 passaram** (API, entradas inválidas, falhas, distribuições, política sem execução).
- `python3 tests/test_router.py`: **106 passaram**.
- `python3 tests/test_criteria.py`: **34 passaram**.
- Wheel v0.4.4 construído sem dependências e inspecionado: inclui HTML, JSONL e servidor do pacote practical.
- Modelo multilingual baixado e executado em CUDA/GB10: **13/16** rótulos de departamento corretos. Evidência detalhada em `avaliacao-local.json`.
- POST real da API pelo navegador: quatro perguntas respondidas e revisão humana. Mensagem de 5.509 tokens recusada com HTTP 422 (orçamento calculado: 965), sem truncamento.
- Interface inspecionada em desktop e mobile; análise real e exportação JSON disponíveis.
- Curso irmão: check estático de 15 páginas publicáveis, 48 tópicos, todos os links/âncoras/manifestos locais válidos.
- Navegador: retomada cross-page, accordion, modal/ESC, notas persistentes, progresso entre módulos, export/import sem perda de campo extra, import inválido sem mutação, jornada com inert e devolução de foco.
- Texto do curso legível sem JS; armazenamento bloqueado usa estado efêmero.
- Contraste de prosa secundária sobre fundo: dark 7,53; claro/foco 7,24; sépia 4,83; alto contraste 12,18. Todos ≥4,5. Sem overflow em viewport de 390 px; console sem erros na rodada final.

Limites: amostra sintética pequena; não é benchmark controlado de latência nem validação de produção. Não executados treinamento, Jev ou suíte upstream e2e com todos os checkpoints. Artefatos de navegador no acervo local `../output/laya/`.
