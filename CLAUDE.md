# predictor-qualification — regras para o agente

Evidência da qualificação pré-treinamento do stack CAIN × Ecosystem × Core ×
Ops × {Cripto, Brasileirão, Stocks}. Foco: **funcionar e dar resultado
confiável para ganhar dinheiro**. Projeto de um dono só; repos públicos.

Núcleo obrigatório em toda sessão:

@qualification/COMMON_QUALIFICATION_CORE.md

## Como uma sessão começa

1. C0 do núcleo (hashes, arquivos, pré-condições).
2. Seguir **só** o prompt indicado pelo dono em `prompts/`. Uma sessão = uma missão.
3. Retomar pelos `ATTESTATION_PARTIAL_*.json` mais recentes da missão.

## Regras fixas

- Um agente por missão, sem subagentes.
- Toda mudança por branch + PR. **Nunca** merge, push em `main`, rebase ou
  force-push. Aprovar = o dono fazer merge.
- Pode publicar releases pré-release (`rc`) dos repos que a missão altera;
  nunca sobrescrever asset.
- Etapa A: só o repo do domínio muda; `core-predictor` e `predictor-ops`
  congelados. Etapa B: domínios só nos `adapter_paths` (C24).
- Nunca tocar instalações operacionais: `C:\CAIN\` (inteiro; `C:\CAIN\projeto`
  só leitura), `C:\Cripto\operacao`, `C:\Cripto\pesquisa-20260909`,
  `C:\Cripto\restaurado-20260908`, `C:\STOCKS\data`, `C:\STOCKS\DADOS_STOCKS.zip*`,
  bancos e instalações do Brasileirão.
- Trabalhar só nos clones de qualificação: `C:\QUALIFICACAO\repos\*`,
  `C:\Cripto\qualificacao\cripto-predictor`, `C:\STOCKS\work\qualification\stocks-predictor`.
- Stocks: não criar venv nem instalar pacotes no Python do Windows; Python do
  Stocks roda no GitHub Actions.
- Linux = GitHub Actions ou VM na nuvem (D-9). Nada de "equivalente local".
- **Repos públicos:** nunca escrever segredo (`.env`, `pipeline.env`, chaves de
  API, de exchange, de odds, tokens) em arquivo, log, commit, relatório ou CI.
- Todo número em relatório vem de log bruto em `RAW_LOGS/` (C20).
- Conflito com regra local de repo, ou algo congelado precisando mudar: parar
  e perguntar ao dono.
- Nunca iniciar treinamento, nunca mover capital.
