"""integration-stocks: acrescenta a D-24 ao fim de qualification/DECISIONS.json (item 5.5 do prompt da sessão).

Confere antes que o arquivo faz round-trip byte a byte com json.dumps(indent=2, ensure_ascii=False) e que as entradas
anteriores continuam iguais depois. Uso: python add_d24.py <caminho do DECISIONS.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
raw = path.read_text(encoding="utf-8")
data = json.loads(raw)


def dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


assert dump(data) == raw, "DECISIONS.json não faz round-trip; não editar"
ids = [d["decision_id"] for d in data["decisions"]]
assert "D-24" not in ids and ids[-1] == "D-23", ids

TEXT = (
    "Decisão do dono em 2026-09-27, no prompt da sessão integration-stocks. "
    "**(1) Base de execução.** A Etapa B usa a base de `qualification/stocks/runtime_target.json`: commit "
    "`61fc017256ffea815ae96bbe02b847dccdb395cc`, versão/wheel `0.3.0rc2`. Fatos (reconfirmados no pré-voo): `61fc017` é "
    "ancestral do `main` do `stocks-predictor`; o merge `36081a66004a464d5e9c5ea4bc6e208d0fcb582e` do PR #96 tem a mesma "
    "árvore (`bea6dce6adea5cc2c0d917b5e2265507ec64708d`); depois dele o `main` recebeu os PRs #99, #101, #102, #104, #105 e "
    "#106 (23 commits além da base; `main` conferido `01c2212`), trabalhos anteriores à Etapa B (pesquisa dos Prompts 2–4, "
    "protocolo v2, leitura pela CAIN); nenhum toca `stocks_predictor/adapters/`; alteram `stocks_predictor/v2/`, `tools/`, "
    "`tests/`, `research/scientific_state.json`, `policy/stocks-evaluation-policy-v1.json`, `AGENTS.md` e docs; "
    "`pyproject.toml` e `uv.lock` não mudaram; a versão continua `0.3.0rc2`, embora o código do `main` seja diferente da "
    "wheel rc2. Consequências: a base é `61fc017` / `0.3.0rc2`; o `main` atual não é base nem runtime; nada de #99–#106, "
    "nem o que entrar no `main` depois de `01c2212`, entra na missão por cherry-pick, merge, rebase, cópia ou reescrita "
    "equivalente; `runtime_target.json` não é atualizado; a divergência é anterior à Etapa B e, sozinha, não reabre C24.4; "
    "ela é registrada como achado com evidência e classificada pela C6. "
    "**(2) Estado do Stocks usado pelo CAIN.** O CAIN usa somente o estado de `61fc017256ffea815ae96bbe02b847dccdb395cc`. "
    "Famílias de sinal, hipóteses, baselines, custos, `handler_allowlist`, configuração e memória do Stocks vêm somente "
    "dessa base e do contrato do Stocks no `main` do `predictor-qualification`; nenhuma regra, hipótese, dado, custo ou "
    "baseline de outro domínio entra. Toda leitura por `git show` de registro do Stocks pelo CAIN usa "
    "`61fc017256ffea815ae96bbe02b847dccdb395cc`; `36081a66004a464d5e9c5ea4bc6e208d0fcb582e` pode representar o mesmo pino "
    "só porque a árvore é igual e porque `tools/hypothesis_sources.json` do CAIN já o usa, e o SHA efetivamente usado é "
    "registrado. `research/scientific_state.json` não existe na base (criado no PR #106) e não é lido em nenhum commit; o "
    "estado científico entra pelas fontes válidas de `tools/hypothesis_sources.json` na base; se a DecisionPolicy exigir "
    "`ingest-state` com esse arquivo, registra-se a pendência. Nada de `61fc017..main` entra em memória, retrieval, "
    "DecisionPolicy, fixtures, N+1 ou referências; leituras anteriores do CAIN em commits posteriores à base (inclusive "
    "`fe53b19` em `docs/evidence/2026-09-24-prompt7/runtime_demo.log`) não são reaproveitadas: refaz-se a leitura na base. "
    "Não se usam `policy/stocks-evaluation-policy-v1.json` como DecisionPolicy ou configuração dela, `stocks_predictor/v2` "
    "nem o holdout selado do protocolo v2. O que só existir depois da base vira pendência. "
    "**(3) WINDOWS_SMOKE.** O ambiente Windows da missão é GitHub Actions `windows-latest` × Python 3.13 (D-1); nada é "
    "instalado nem executado no Windows local do PC 2 para o Stocks. Na attestation, cada item de `environments` respeita o "
    "schema (`additionalProperties: false`) e contém somente `os`, `python`, `role: secondary`, `where: github_actions`, "
    "`result` e `evidence`. "
    "**(4) R8 e cobertura — resposta do dono ao conflito C19 entre a regra local R8 (`AGENTS.md` do `stocks-predictor`: "
    "mudança no pacote exige novos recibos de carga real e de capacidade, e o CI confere o selo com "
    "`tools/verify_operational_evidence.py`, que cobre todo `.py` de `stocks_predictor/`, `tests/` e `tools/`, "
    "`pyproject.toml`, `uv.lock`, `main.py`, `ci.yml`, `.gitattributes`, `.gitleaks.toml`, `.gitleaksignore` e "
    "`tools/build-requirements.txt`) e C24.3(a) (diff do domínio só nos `adapter_paths`).** Além de "
    "`stocks_predictor/adapters/` e das exceções normais de C24.3(a), ficam autorizados somente: (a) arquivos novos em "
    "`tests/adapters/`, que podem importar `stocks_predictor.adapters`, sem mudar teste existente e sem entrar na suíte de "
    "conformidade congelada; (b) o procedimento R8 no commit final do adapter: recibo real com "
    "`tools/operational_validation.py --archive` só sobre a cópia local `~/predictors/data/d16/stocks/COTAHIST_A2026.ZIP` "
    "(sha256 `34b774681cbd201ef197fb98af8d431e4d7302e801f58b66e54036d2935dc4f4`, 55.986 linhas, conferido antes e depois), "
    "reproduzindo o procedimento de `docs/engineering/2026-09-24-qualification-stage-a/evidence/operational-real.json`; "
    "recibo de capacidade com `--rows 250000` sintéticas; selo por `tools/materialize_current_operational_evidence.py`. "
    "Os recibos novos ficam só em `docs/engineering/<AAAA-MM-DD>-integration-stocks/evidence/` (só `.json`); fora dos "
    "`adapter_paths` entram só os arquivos produzidos pelo procedimento (os dois recibos e "
    "`docs/engineering/current-operational-evidence.json`), sem edição manual; recibos anteriores intactos. (c) Continuam "
    "intocados `tools/verify_operational_evidence.py`, `fail_under = 77`, `AGENTS.md`, `ci.yml`, o restante de `tests/` e "
    "de `docs/`; nenhum `.md` novo no `stocks-predictor`. Os recibos R8 são evidência de engenharia da regra local "
    "(precedente D-18), nunca evidência de gate; o COTAHIST_A2026.ZIP serve só ao R8. Antes de publicar o commit final, "
    "`verify_operational_evidence.py` passa localmente e a cobertura com os testes novos fica `>= 77`; sem o selo R8 o "
    "commit final não é publicado. Falha de sha256 da fonte, contagem de linhas, geração dos recibos, verificador R8 ou "
    "cobertura não é contornada nem reduz o piso: é bloqueio. O `CONTRACT_REVALIDATION_REPORT.md` lista em C24.3(a) esses "
    "paths como autorizados por esta decisão e demonstra por diff que nada mais mudou fora dos `adapter_paths`."
)

data["decisions"].append({
    "decision_id": "D-24",
    "question": "integration-stocks: base de execução do stocks-predictor com o main à frente do runtime_target "
                "(PRs #99–#106), origem do estado do Stocks usado pelo CAIN, WINDOWS_SMOKE no GitHub Actions e conflito "
                "C19 entre a regra local R8 do stocks-predictor e C24.3(a)",
    "text": TEXT,
    "origin": "decisão do dono no prompt da sessão integration-stocks, 2026-09-27",
    "status": "APPROVED",
})
new = dump(data)
before = json.loads(raw)["decisions"]
assert json.loads(new)["decisions"][: len(before)] == before
path.write_text(new, encoding="utf-8")
print(f"D-24 acrescentada; entradas anteriores iguais: {len(before)}; total: {len(before) + 1}")
