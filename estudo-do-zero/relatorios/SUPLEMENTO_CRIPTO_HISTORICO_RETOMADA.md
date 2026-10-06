# Cripto: fechamento da revisão histórica (partições 0, 1 e 3) — retomada 2026-09-30

Concluída a leitura semântica dos 79 objetos históricos que ficaram pendentes na pausa: partição 0 índices 0–8 (9 objetos, novo bloco 19), partição 1 índices 0–39 (40 objetos, stem `shared-archive-1`) e partição 3 blocos 007–020 (30 objetos, arquivo `archive-root-extra-domains-coverage.json`). `save_resume.py` recalcula 0 pendentes em 193/193/194/193. Nenhum objeto histórico foi importado ou executado.

## Ambiente e identidade

A retomada correu em Linux (Claude Code), num clone independente do remoto `leonardosovienski/cripto-predictor` (main 74113ef) que contém o commit da linha de base 88158f25 no histórico. Os objetos do arquivo são content-addressed: o sha256 de cada um foi conferido contra `archive-derivation-assignment-{0,1,3}.json`. As bases foram lidas com `git show 88158f25:<base>` (blob LF). O `base_sha256` registrado pela sessão Windows é o hash do mesmo texto com CRLF (checkout com autocrlf); a equivalência foi verificada para todas as bases usadas. O original `C:\CRIPTO\pesquisa-20260909` não foi acessado nesta sessão; a identidade é por conteúdo, não por caminho.

## Método

Para cada objeto: diff completo contra a base em 88158f25 (inserções, exclusões e contexto), corpo integral quando sem base, e, para 54 objetos que são variantes byte-a-byte de irmãos já certificados, diff contra o irmão mais próximo com as notas do irmão à vista. Vinte e nove variantes diferem só em fim de linha (CRLF/LF), linhas em branco finais ou formatação ruff; as demais têm diferenças reais registradas nas notas (por exemplo: `backtest_v3` com barreiras SL/TP, curva de equity com netting, filtro econômico IS-only, H7/H9 e grade de thresholds; `attest_harness` com staging por Core 3.2 recusar árvore suja; `main.py` sem validação de `--output-dir`; `feature_builder` sem `build_volume_index`; `TradeIntent` sem campos científicos).

## O que a evolução preservada mostra

As versões históricas são sistematicamente mais permissivas que a base em 88158f25: `feature_store` sem `BEGIN IMMEDIATE`, sem regra de vintage observado, sem escrow de inputs de previsão e sem `closed_daily_price`; `execution` sem idempotência por `fill_id` e com reconciliação só por quantidade; `signal_engine` mutável, sem fingerprint de política e com append sem lock; `regime_engine` sem hash do dado de treino e aceitando modelo sem fingerprint; `coingecko` aceitando o ponto parcial do dia e volume ausente como zero; `macro_features` com lag presumido em vez de `available_at` por vintage; `quality_snapshot` sem guarda de prefixo da cadeia do ledger. Esses comportamentos pertencem aos hashes históricos citados nas notas e não são achados sobre a implementação atual.

Os entregáveis de sessão (deliver_retro, carry_deliver/carry_analyze, deliver_forward, deliver_immediate, package_profit_comparison, finalize_research, prepare_git_main_delivery, reconcile_records, implement_core) documentam a disciplina de preservação da época (hashes, ZIPs exclusivos, errata H6/H9, migração Core 3.2.0 com DSR estrito e atestados de poder) e também sua limitação de proveniência: contagens de testes e resultados escritos como constantes no código, não derivados de log. `report_phase2.py` é a exceção, lendo tudo dos JSONs de resultado. Nenhum desses scripts demonstra lucro ou autoriza capital; vários declaram explicitamente o contrário.

## Registro

Notas por objeto: `evidencias/cripto-predictor/archive-derivation-0-block19-coverage.json`, `shared-archive-1-notes.json` (índices 0–39) e `archive-root-extra-domains-coverage.json`; consolidação em `crypto-archive-coverage-merged.json` (773) e `crypto-active-coverage-merged.json` (440). `coverage.json` passou a marcar as 773 linhas como certificadas por derivação histórica. Leituras e checkpoints estão em `REGISTRO.log`.

Limite: revisão estática integral por derivação verificável; não houve execução destes objetos, validação de mercado ou atestação econômica.
