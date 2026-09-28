"""Relatório do teste conjunto do ecossistema (não é gate da integration-brasileirao), gerado do SUMMARY.json publicado.

Números por item (1–13) e a tabela da disputa da trava vêm do SUMMARY.json da tentativa publicada; as tentativas
anteriores (privadas, não publicadas) entram só pelo sha256 do SUMMARY/arquivo e pela causa, passados na linha de comando.
Uso: python ecosystem_joint_report.py <qualification/integration-brasileirao> <run> <attempts.json>
"""

from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    q, run, attempts = Path(sys.argv[1]), sys.argv[2], json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    base = q / "RAW_LOGS" / "runtime" / run / "ecosystem-joint"
    summary = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))
    items = collections.defaultdict(lambda: [0, 0])
    for c in summary["checks"]:
        items[c["check"].split(":")[0]][0 if c["ok"] else 1] += 1
    sha = {p: hashlib.sha256((base / p).read_bytes()).hexdigest()
           for p in ("SUMMARY.json", "commands.log", "lock-contention/commands.log", "no_data_rows_check.json")}
    rows = []
    for d, reps in summary["lock_contention"].items():
        loser = collections.Counter(r.get("loser_published") for r in reps)
        rows.append(f"| {d} | {len(reps)} | {sum(r['experiments'] == 1 for r in reps if r['allow'])} | "
                    f"{', '.join(f'{k} {v}' for k, v in sorted(loser.items()))} | {sum(bool(r.get('died')) for r in reps)} | "
                    f"{', '.join(str(r['rep']) for r in reps if r.get('loser_published') == 'RECONCILIATION_REQUIRED') or '—'} |")
    failed = [c["check"] for c in summary["checks"] if not c["ok"]]
    text = f"""# Teste conjunto do ecossistema — cain 0.4.13rc12

> Gerado por `scripts/ecosystem_joint_report.py` a partir de `RAW_LOGS/runtime/{run}/ecosystem-joint/SUMMARY.json`.
> Não é gate da integration-brasileirao (QUALIFIED, attestation inalterada). Pedido do dono no chat da sessão cripto;
> lista de conferências combinada com as sessões cripto e STOCKS; rodado no PC 2 (WSL) pelo runtime integrado.

Resultado da tentativa publicada: **{summary['passed']} de {summary['passed'] + summary['failed']}** conferências.

| Item | Passaram | Falharam |
|---|---|---|
{chr(10).join(f"| {k} | {v[0]} | {v[1]} |" for k, v in sorted(items.items(), key=lambda kv: int(kv[0])))}

Falhas: {'; '.join(failed) if failed else 'nenhuma'}.

## Disputa da trava do Ops (item 13): dois consumidores do mesmo domínio na mesma task

| Domínio | Repetições | 1 experimento | O perdedor publicou | Quedas | Repetições com RECONCILIATION_REQUIRED |
|---|---|---|---|---|---|
{chr(10).join(rows)}

`OPS_FAILED_RETRYABLE` do perdedor não é terminal e não tem efeito. `RECONCILIATION_REQUIRED` falso tem efeito: o
CAIN trava o domínio (R09 DOMAIN_RECONCILIATION_PENDING) até um humano. No stocks isso vem de uma materialização de
referência fora da trava do Ops (achado da sessão STOCKS, confirmado aqui). Fica em aberto para o dono.

LLM (item 10): {json.dumps(summary.get('llm'), ensure_ascii=False)}

## Arquivos (sha256)
{chr(10).join(f"- `{p}` `{h}`" for p, h in sha.items())}

## Tentativas anteriores (privadas, não publicadas)
{chr(10).join(f"- tentativa {a['n']}: {a['result']}; {a['why']} (sha256 `{a['sha256']}`)" for a in attempts)}
"""
    (q / "ECOSYSTEM_JOINT_REPORT.md").write_text(text, encoding="utf-8")
    print("ECOSYSTEM_JOINT_REPORT.md", len(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
