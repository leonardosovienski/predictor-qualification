"""integration-stocks: registra a D-26 (famílias congeladas do main do stocks) em qualification/DECISIONS.json.

A D-26 muda só um ponto da D-24 (2): a lista de famílias congeladas do CAIN para o stocks passa a somar as famílias do
research/scientific_state.json do main do stocks-predictor, num commit fixado, ao que a base 61fc017 já dá. As palavras
do dono e o texto da opção vão literais. Confere antes de gravar:
  * que DECISIONS.json regravado com o mesmo formato dá os mesmos bytes (nenhuma entrada reformatada);
  * que D-26 ainda não existe;
  * o blob e o sha256 do arquivo no commit fixado e as famílias que ele acrescenta à base.

Uso: python owner_decision_d26.py <raiz do predictor-qualification> <clone do stocks-predictor>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT, STOCKS = Path(sys.argv[1]), Path(sys.argv[2])
PATH = ROOT / "qualification/DECISIONS.json"
COMMIT = "4c82885eddab233f2b57442046875fdc2c8f0932"
STATE = "research/scientific_state.json"
BLOB = "3fc34e5e24778cc2501a78d5832c369486e06155"
SHA256 = "1f7eeff798a1ac378393e9f9225f5708004d5cd54c6d912d1547c4bc390c6ec7"
ADDED = ["quality_net_margin", "quality_roe_leverage_double_filter"]
QUESTION = ("Famílias do stocks que o CAIN não conhece: a D-24 manda o estado do CAIN vir só da base 61fc017, e o main "
            "do stocks tem 2 nomes de família a mais. Mudo?")
WORDS = "Somar as famílias do main (Recomendado)"
OPTION = ("Nova decisão sobre a D-24, só para a lista de famílias congeladas: o CAIN bloqueia também as famílias do "
          "scientific_state.json do main do stocks (só acrescenta, nunca tira). O resto do estado continua da base. "
          "Entra no stocks.json da rc13, com ciclo 4 dos congelados.")
OTHER = "Manter a D-24: O CAIN continua só com a base. Os dois nomes seguem desconhecidos (o ID da H12 continua bloqueado)."


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(STOCKS), *args], capture_output=True, check=True).stdout


def dump(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    raw = PATH.read_bytes()
    decisions = json.loads(raw)
    if dump(decisions) != raw:
        raise SystemExit("DECISIONS.json não volta aos mesmos bytes com indent=2: formato diferente, nada gravado")
    if any(d["decision_id"] == "D-26" for d in decisions["decisions"]):
        raise SystemExit("D-26 já existe no DECISIONS.json")
    state_raw = git("show", f"{COMMIT}:{STATE}")
    blob = git("rev-parse", f"{COMMIT}:{STATE}").decode().strip()
    if (blob, hashlib.sha256(state_raw).hexdigest()) != (BLOB, SHA256):
        raise SystemExit("blob ou sha256 do scientific_state.json no commit fixado diverge")
    frozen = json.loads((ROOT / "qualification/integration-stocks/FROZEN_PARAMETERS.json").read_bytes())
    base = frozen["decision_policy"]["stocks_config"]["frozen_families"]
    added = sorted(set(json.loads(state_raw)["frozen_families"]) - set(base))
    if added != ADDED:
        raise SystemExit(f"famílias acrescentadas divergem: {added}")
    text = (
        f"Decisão do dono em 2026-09-28, na sessão integration-stocks (pergunta com opções). Pergunta: \"{QUESTION}\". "
        f"Palavras do dono: \"{WORDS}\". Texto da opção escolhida: \"{OPTION}\" (a outra opção era \"{OTHER}\"). "
        "**Alcance.** Muda só a D-24 (2), e só quanto à lista de famílias congeladas do CAIN para o stocks. "
        "`frozen_families` do stocks passa a ser a união das famílias das hipóteses encerradas da base "
        "`61fc017256ffea815ae96bbe02b847dccdb395cc` (trials_v2.json e trials.json, como já era) com a lista "
        f"`frozen_families` de `{STATE}` do stocks-predictor no commit `{COMMIT}` (blob `{BLOB}`, sha256 `{SHA256}`), "
        "lido por `git show` com o SHA completo. A união acrescenta `quality_net_margin` (H12; a base chama "
        "`net_margin`) e `quality_roe_leverage_double_filter` (H10; a base chama `quality_roe_leverage_intersection`). "
        "Nenhuma família sai. **O que continua da D-24.** Desse arquivo só entra a lista `frozen_families`. Hipóteses, "
        "estados, custos, baselines, `handler_allowlist`, memória, fixtures, N+1 e referências continuam só da base e do "
        "contrato. `policy/stocks-evaluation-policy-v1.json`, `stocks_predictor/v2` e o holdout selado do protocolo v2 "
        "continuam fora. `qualification/stocks/runtime_target.json` não muda, e a base de execução continua "
        "`61fc017`/`0.3.0rc2`. **Materialização.** A lista entra pelo ciclo 4 dos parâmetros congelados da "
        "integration-stocks (`decision_policy.stocks_config.additional_frozen_families`: repositório, commit, caminho, "
        "blob, sha256 e as famílias acrescentadas) e pelo `tools/build_domain_config.py` do cain (cain#78), que confere "
        "blob e sha256, lê só essa lista e nunca remove uma família. Ela vai para o `stocks.json` da cain 0.4.13rc13. "
        "**Motivo.** O main do stocks deu nomes novos às famílias da H10 e da H12. Uma proposta do CAIN que declarasse "
        "um desses nomes não era bloqueada pela família congelada (R05); só o ID da H12 era."
    )
    decisions["decisions"].append({
        "decision_id": "D-26",
        "question": ("integration-stocks: famílias congeladas do stocks que o CAIN não conhecia (nomes do main do "
                     "stocks-predictor) — exceção à D-24 (2) só para a lista de famílias"),
        "text": text,
        "origin": "decisão do dono no chat da sessão integration-stocks (pergunta com opções), 2026-09-28",
        "status": "APPROVED",
    })
    PATH.write_bytes(dump(decisions))
    print(json.dumps({"decisions": len(decisions["decisions"]), "added": added,
                      "sha256": hashlib.sha256(PATH.read_bytes()).hexdigest()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
