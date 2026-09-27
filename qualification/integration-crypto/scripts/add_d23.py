"""Acrescenta a D-23 ao fim de qualification/DECISIONS.json sem reformatar as entradas existentes."""

import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
raw = path.read_text(encoding="utf-8")
before = json.loads(raw)
assert all(d["decision_id"] != "D-23" for d in before["decisions"])

d23 = {
    "decision_id": "D-23",
    "question": (
        "integration-crypto: base de execução do cripto-predictor com o main do repositório à frente do "
        "runtime_target (PRs #128–#134), origem do estado do domínio usado pelo CAIN, e WINDOWS_SMOKE no PC 2"
    ),
    "text": (
        "Decisão do dono em 2026-09-27, no prompt da sessão integration-crypto. "
        "**(1) Base de execução.** A Etapa B usa a base de `qualification/crypto/runtime_target.json`: commit "
        "`341d270e4d709150c581c3cd93f4518d483009eb`, versão `1.2.0rc2`. Fatos: `341d270` não é ancestral do `main` do "
        "`cripto-predictor`; entrou por squash como `174573d` no PR #127, com a mesma árvore; depois de `174573d` o "
        "`main` recebeu 7 commits (PRs #128–#134, pesquisa dos Prompts 1–4), nenhum toca "
        "`GarimpoInvestimentos/adapters/`, mas alteram outras partes do pacote, testes e docs; o `pyproject.toml` do "
        "`main` ainda declara `1.2.0rc2`, embora o código seja diferente da wheel publicada. Consequências: a base é "
        "`341d270` / `1.2.0rc2`; o `main` atual não é base nem runtime; nada de #128–#134, nem o que entrar no `main` "
        "depois de `be116eb`, entra na missão por cherry-pick, merge, rebase, cópia ou reescrita equivalente; "
        "`runtime_target.json` não é atualizado; essa divergência é anterior à Etapa B e, sozinha, não reabre C24.4; "
        "ela é registrada como achado com evidência e classificada pela C6. "
        "**(2) Memória e configuração do CAIN.** O CAIN usa somente o estado de "
        "`341d270e4d709150c581c3cd93f4518d483009eb`. Hipóteses H1..H9, família congelada, custos, baselines, "
        "`handler_allowlist`, configuração e memória do domínio vêm somente dessa árvore e do contrato no `main` do "
        "`predictor-qualification`. Toda leitura por `git show` do registro do cripto pelo CAIN usa o SHA completo "
        "`341d270e4d709150c581c3cd93f4518d483009eb`. Nada de `174573d..main` entra em memória, retrieval, "
        "`DecisionPolicy`, fixtures, N+1 ou referências. A política de decisão v1 do PR #132 não é a `DecisionPolicy` "
        "do CAIN nem sua configuração. O holdout futuro selado do PR #133 não é lido, usado nem referenciado. Se algo "
        "aparentemente exigido só existir no `main` posterior à base, esse conteúdo não é usado: registra-se a "
        "pendência. "
        "**(3) WINDOWS_SMOKE no PC 2.** Pasta autorizada: `C:\\Cripto\\qualificacao\\runtime\\integration-crypto\\`, "
        "exceção específica à regra de não escrever em `/mnt/c` e à convenção de que `C:\\` seria o PC 1. Escrita no "
        "Windows somente por PowerShell, nunca por `/mnt/c`, somente na pasta autorizada; criar "
        "`C:\\Cripto\\qualificacao\\` para chegar nela é permitido; nada mais em `C:\\Cripto`. uv e Python 3.13 ficam "
        "gerenciados dentro da pasta; podem ser copiados de `C:\\QUALIFICACAO\\runtime\\brasileirao2\\tools\\`, "
        "conferindo o sha256 do zip do uv contra o `.sha256`. Nunca Python do sistema, instalação global, PATH "
        "persistente, variável persistente ou Registro do Windows. CAIN e cripto vêm somente de `uv.lock` e wheels "
        "publicadas. Dados: somente as cópias públicas verificadas de `~/predictors/data/d16/cripto/`, copiadas para a "
        "pasta, com sha256 conferido antes e depois. Nunca criar nem tocar `C:\\Cripto\\operacao`, "
        "`C:\\Cripto\\pesquisa-20260909`, `C:\\Cripto\\restaurado-20260908`, `C:\\CAIN\\`. Na attestation, o item de "
        "`environments` respeita estritamente o schema e contém somente `os`, `python`, `role: secondary`, "
        "`where: local_windows`, `result` e `evidence` (sem `note`); a identificação \"PC 2\" aparece na evidência/log "
        "do ambiente Windows e no `QUALIFICATION_CHANGELOG.md`. No fim, a pasta Windows não é apagada; logs usados "
        "como evidência vão para `RAW_LOGS`, com sha256 conferido na cópia."
    ),
    "origin": "decisão do dono no prompt da sessão integration-crypto, 2026-09-27",
    "status": "APPROVED",
}

tail = "\n    }\n  ]\n}\n"
assert raw.endswith(tail), repr(raw[-40:])
entry = json.dumps(d23, ensure_ascii=False, indent=2)
entry = "\n".join("    " + line for line in entry.splitlines())
new = raw[: -len(tail)] + "\n    },\n" + entry + "\n  ]\n}\n"
after = json.loads(new)
assert after["decisions"][:-1] == before["decisions"]
assert after["decisions"][-1] == d23
path.write_text(new, encoding="utf-8")
print("D-23 acrescentada;", len(after["decisions"]), "decisões")
