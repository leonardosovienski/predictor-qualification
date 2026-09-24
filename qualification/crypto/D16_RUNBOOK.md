# D-16 — runbook (missão crypto)

Estado antes da D-16: 26 gates `PASS`, 5 `NOT_RUN` com `BLOCKED: D-16 pendente`
(`E2E`, `SOAK`, `CRYPTO_UNCOMFORTABLE_CASES`, `CRYPTO_ECONOMIC_METRICS`,
`CRYPTO_NEGATIVE_CONTROLS`), P0 = P1 = 0. Os cinco exigem dados reais no Linux
primário (C11). Fixture sintética não vale como PASS.

Alvo congelado: `qualification/crypto/runtime_target.json` (cripto-predictor
`341d270`, wheel `v1.2.0rc2` com sha256; Core 3.2.1 e Ops 4.2.2rc1 pelo `uv.lock`).

## 1. O que só o dono faz

Registrar a D-16 em `qualification/DECISIONS.json` com `status: APPROVED`, por PR
e merge. O texto precisa dizer:

* **onde roda** o Linux primário. O schema da attestation aceita só
  `github_actions` e `cloud_vm`, e a D-9 também. Uma máquina física própria com
  Linux **não** se encaixa: usar a outra máquina só como console, disparando o
  workflow (opção A) ou abrindo uma VM na nuvem ou um Codespace (opção B). Para
  rodar numa máquina física, a D-16 precisa emendar a D-9 e o schema
  (C14, "Núcleo"), o que é bem maior;
* **dados**: Binance data.vision públicos (BTCUSDT UM, klines 1d + funding),
  baixados no host, conferidos pelo `.CHECKSUM` publicado e nunca versionados (D-11);
  só o `MANIFEST.json` com os sha256 entra na evidência;
* que a D-16 autoriza rodar os 5 gates acima no alvo congelado, sem mudar
  parâmetros, vetores nem perfil (C15).

Sem D-16 `APPROVED` no checkout usado, `d16_linux.sh` para com
`BLOCKED: D-16 não está APPROVED` e exit 4 (trava testada).

## 2. Execução

### Opção A — GitHub Actions (recomendada; nada a instalar)

De qualquer máquina com `gh` autenticado (`gh auth login`):

```bash
gh workflow run crypto-d16.yml -R leonardosovienski/predictor-qualification --ref main
gh run watch -R leonardosovienski/predictor-qualification $(gh run list -R leonardosovienski/predictor-qualification -w crypto-d16.yml -L1 --json databaseId -q '.[0].databaseId')
```

O job (`ubuntu-latest`, Python 3.13, timeout de 180 min) sobe o artefato `crypto-d16`.

### Opção B — VM Linux na nuvem ou Codespace (Ubuntu x86_64, descartável)

```bash
git clone https://github.com/leonardosovienski/predictor-qualification.git
bash predictor-qualification/qualification/shared/HYGIENE/scripts/provision_linux_vm.sh   # uv por sha256 + Python 3.13
export PATH="$HOME/qualificacao/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$HOME/qualificacao/tools/python" UV_PYTHON_PREFERENCE=only-managed
bash predictor-qualification/qualification/crypto/scripts/d16_linux.sh ~/d16-out
tar czf d16-out.tgz -C ~ d16-out
```

Trazer o `d16-out.tgz` para esta máquina (ex.: `scp`) e destruir a VM depois.
Nenhum segredo é necessário: repositórios públicos e dados públicos.

## 3. Depois da execução (agente, numa branch nova)

1. Copiar a saída **sem editar** para
   `qualification/crypto/RAW_LOGS/d16/<run_id ou vm-AAAAMMDD>/`
   (Actions: `gh run download <run_id> -n crypto-d16 -D <dir>`).
2. `python qualification/crypto/scripts/d16_finalize.py qualification/crypto/RAW_LOGS/d16/<id>`.
   O script confere a D-16, o commit e o sha256 da wheel contra o `runtime_target.json`,
   e fecha cada gate em `PASS` ou `FAIL` pelos critérios congelados. A attestation
   anterior (`eb3e79f4…`) é preservada byte a byte como
   `QUALIFICATION_ATTESTATION_superseded_<sha12>.json`, e a nova aponta para ela
   em `supersedes_sha256`.
3. `python qualification/crypto/scripts/evidence_numbers.py --out EVIDENCE_NUMBERS_D16.json …` (apontando para a pasta d16) para os números do
   `SOAK_REPORT.md` e do `SCIENTIFIC_INTEGRITY_REPORT.md` (seção D-16, C20).
4. `python qualification/crypto/scripts/attest.py final`, depois `attest.py check`.
5. Varredura de segredos na evidência nova, `QUALIFICATION_CHANGELOG.md`, PR.
   O merge do dono aprova (e com ele o `DOMAIN_RESEARCH_CONTRACT.json` já no `main`).

Resultado possível: `QUALIFIED` se os 5 gates passarem, ou `NOT_QUALIFIED` com o
gate que falhou. `QUALIFIED` não é edge nem autoriza capital (C22). No diagnóstico
com dados reais no Windows, o líquido foi −83 bps/semana, `INCONCLUSIVE`/`NO_EDGE`.

## Diagnóstico já feito (Windows, não conta como prova)

O mesmo kit (`soak.py --real`, `e2e_runtime.py --real`, `science_real.py`) rodou no
runtime Windows do rc2 com dados reais. Serve para achar defeito de kit antes da D-16.
Não substitui o Linux primário (C11, C2).

Soak `--real` de diagnóstico (Windows local, rc2, 2026-09-24): log bruto em
`RAW_LOGS/d16-diagnostic-windows/soak_real.jsonl`, com `summary` e `verdict` no próprio log.
Não entra em nenhum gate.

Kit ensaiado num clone descartável com entradas substitutas, sem gerar evidência:
* sem D-16 → para;
* commit divergente do `runtime_target.json` → para;
* tudo verde → `QUALIFIED`, `attest.py check` OK e `supersedes_sha256 = eb3e79f4…`;
* soak com veredito negativo → `SOAK`/`CRYPTO_UNCOMFORTABLE_CASES` `FAIL` → `NOT_QUALIFIED`.
