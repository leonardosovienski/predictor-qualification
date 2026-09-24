"""stocks / D-16: o pré-filtro de liquidez PIT do construtor não muda o universo.

Roda com o Python do runtime suportado (wheel instalada). Carrega o painel filtrado (o objeto
que vai para o ReferenceStore) e o painel completo (todas as ações/units do COTAHIST na janela)
com `stocks_predictor.research_pit.Panel`, monta o calendário de rebalances do protocolo real
(`rebalance_sessions`, warmup = min_history + liquidity_lookback) e compara, em cada rebalance,
o universo PIT (`Panel.universe`: membros, ranks, CNPJ, ticker, mediana de volume). Qualquer
diferença = falha fechada (o painel filtrado não pode ser usado).

Uso: python verify_prefilter.py <panel.json> <panel_full.json> <protocol.json> <saída.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from stocks_predictor.research_pit import Panel, rebalance_sessions


def main() -> int:
    panel_path, full_path, protocol_path, out_path = (Path(a) for a in sys.argv[1:5])
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    universe_cfg = protocol["universe"]
    raw = json.loads(panel_path.read_text(encoding="utf-8"))
    full_raw = json.loads(full_path.read_text(encoding="utf-8"))
    as_of = raw["data_cutoff"]
    panel = Panel(raw, as_of=as_of, minimum_pit_class="PIT_RECONSTRUCTED")
    full = Panel(full_raw, as_of=as_of, minimum_pit_class="PIT_RECONSTRUCTED")
    cfg = {"top_n": universe_cfg["top_n"], "liquidity_lookback_sessions": universe_cfg["liquidity_lookback_sessions"],
           "min_history_sessions": universe_cfg["min_history_sessions"]}
    warmup = universe_cfg["min_history_sessions"] + universe_cfg["liquidity_lookback_sessions"]
    schedule = rebalance_sessions(panel.calendar, universe_cfg["rebalance_every_sessions"], warmup)
    schedule_full = rebalance_sessions(full.calendar, universe_cfg["rebalance_every_sessions"], warmup)
    differences = []
    sizes = []
    for session in schedule:
        a = panel.universe(session, cfg)
        b = full.universe(session, cfg)
        sizes.append(len(a["members"]))
        if a["members"] != b["members"] or a["universe_identity_hash"] != b["universe_identity_hash"]:
            differences.append({"session": session, "filtered": [m["security_id"] for m in a["members"]],
                                "full": [m["security_id"] for m in b["members"]]})
    report = {
        "panel_securities": len(panel.securities), "full_securities": len(full.securities),
        "calendar_equal": panel.calendar == full.calendar, "sessions": len(panel.calendar),
        "schedule_equal": schedule == schedule_full, "rebalances": len(schedule),
        "first_rebalance": schedule[0] if schedule else None, "last_rebalance": schedule[-1] if schedule else None,
        "universe_sizes": {"min": min(sizes) if sizes else None, "max": max(sizes) if sizes else None},
        "differences": differences,
        "counters": {"panel": panel.counters, "full": full.counters},
    }
    report["ok"] = report["calendar_equal"] and report["schedule_equal"] and not differences and bool(schedule)
    Path(out_path).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("ok", "rebalances", "first_rebalance", "last_rebalance",
                                              "universe_sizes", "calendar_equal", "schedule_equal")}))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
