"""stocks: resumo da reverificação de 2026-09-24 a partir dos logs brutos (C20). Não decide gate: confere.

Lê RAW_LOGS/d16/recheck-20260924/ (CIs de stocks-predictor/Core/Ops, runtime da Etapa A com as wheels
publicadas, suíte no checkout, build reprodutível da rc, conjunto protegido, attestation, parciais) e os
números da reexecução da D-16 (d16_finalize.py sobre o run de reverificação), comparando-os com
D16_EVIDENCE_NUMBERS.json (run de evidência 35983568296).

Uso: python recheck_summary.py <dir recheck> <numbers da reexecução D-16> <saída.json>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

QC = Path(__file__).resolve().parents[1]


def tail_exit(path: Path):
    if not path.is_file():
        return None
    found = re.findall(r"^\[exit (\d+)\]$", path.read_text(encoding="utf-8", errors="replace"), re.M)
    return int(found[-1]) if found else None


def pytest_line(path: Path):
    if not path.is_file():
        return None
    lines = [x for x in path.read_text(encoding="utf-8", errors="replace").splitlines()
             if re.search(r"\d+ (passed|failed|errors?)\b", x)]
    return lines[-1].strip() if lines else None


def main() -> int:
    rc, d16_numbers, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    s: dict = {"ci": {}, "runtime": {}, "suite": {}}
    for f in sorted(rc.glob("ci_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        s["ci"][f.stem] = {"workflow": d["name"], "head": d["headSha"], "event": d["event"], "conclusion": d["conclusion"],
                           "jobs": {j["name"]: j["conclusion"] for j in d["jobs"]}}
    for env_dir in sorted(rc.glob("run*/stocks-runtime-*")):
        e2e = json.loads((env_dir / "e2e" / "E2E_SUMMARY.json").read_text(encoding="utf-8")) \
            if (env_dir / "e2e" / "E2E_SUMMARY.json").is_file() else {}
        soak = [json.loads(x) for x in (env_dir / "soak.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] \
            if (env_dir / "soak.jsonl").is_file() else []
        env_log = (env_dir / "env.log").read_text(encoding="utf-8", errors="replace")
        s["runtime"][env_dir.name] = {
            "run": env_dir.parent.name, "setup_ok": "SETUP FAIL" not in env_log and "\ndone " in env_log,
            "wheel_sha256": (env_dir / "stocks_wheel.sha256").read_text().split()[0],
            "uv_lock_check_exit": tail_exit(env_dir / "uv_lock_check.log"),
            "conformance": pytest_line(env_dir / "conformance.log"), "conformance_exit": tail_exit(env_dir / "conformance.log"),
            "full_suite_against_wheel": pytest_line(env_dir / "full_suite.log"), "full_suite_exit": tail_exit(env_dir / "full_suite.log"),
            "e2e_checks": f"{sum(c['ok'] for c in e2e.get('checks', []))}/{len(e2e.get('checks', []))}", "e2e_all_ok": e2e.get("all_ok"),
            "soak_zero_tolerance_ok": next((r["zero_tolerance_ok"] for r in soak if r.get("kind") == "verdict"), None),
            "science_exit": tail_exit(env_dir / "science.log"),
        }
    for env_dir in sorted(rc.glob("run*/stocks-suite-*")):
        s["suite"][env_dir.name] = {"run": env_dir.parent.name, "head": (env_dir / "head.txt").read_text().strip(),
                                    "pytest": pytest_line(env_dir / "pytest.log"), "pytest_exit": tail_exit(env_dir / "pytest.log"),
                                    "doctor_exit": tail_exit(env_dir / "doctor.log")}
    receipt = next(rc.glob("run*/stocks-rc-build/build-receipt.json"), None)
    if receipt:
        r = json.loads(receipt.read_text(encoding="utf-8"))
        s["build_rc"] = {"run": receipt.parent.parent.name, "distributions": r.get("distributions"),
                         "wheel_equals_published": (r.get("distributions") or {}).get("stocks_predictor-0.3.0rc2-py3-none-any.whl")
                         == "92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8"}
    s["protected_git"] = {}
    for f in sorted(rc.glob("protected_check_git_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        s["protected_git"][d["final_commit"][:7]] = {"items": d["git_items"], "changed": len(d["git_changed"]),
                                                     "missing": len(d["git_missing"]),
                                                     "new": len(d["git_new_items_matching_patterns"])}
    att = json.loads((rc / "verify_attestation_main.json").read_text(encoding="utf-8"))
    s["attestation_main"] = {"commit": att["commit"], "sha256": att["attestation_sha256"], "all_ok": att["all_ok"],
                             "rules": {c["rule"]: c["ok"] for c in att["checks"]}}
    par = json.loads((rc / "verify_partials_main.json").read_text(encoding="utf-8"))
    s["partials_main"] = {"partials": par["partials"],
                          "evidence_intact": sum(1 for c in par["checks"] if "every cited" in c["check"] and c["ok"]),
                          "failed_checks": par["failed"]}
    new = json.loads(d16_numbers.read_text(encoding="utf-8"))
    old = json.loads((QC / "D16_EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))
    s["d16_reexecution"] = {
        "gates": {g: v["status"] for g, v in new["gates"].items()},
        "panel_sha256": {k: v["panel_sha256"] for k, v in new["environments"].items()},
        "same_panel_as_evidence": all(v["panel_sha256"] == old["expected_panel_sha256"] for v in new["environments"].values()),
        "same_economic_metrics_as_evidence": new["economic"]["metrics"] == old["economic"]["metrics"],
        "same_negative_control_counts": new["gates"]["STOCKS_NEGATIVE_CONTROLS"]["supported_counts"]
        == old["gates"]["STOCKS_NEGATIVE_CONTROLS"]["supported_counts"],
        "soak_counts": {k: v for k, v in new["gates"]["SOAK"]["counts"].items() if k != "summary"},
    }
    out.write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if len(sys.argv) > 4:
        render(s, Path(sys.argv[4]))
    print(json.dumps(s["d16_reexecution"], ensure_ascii=False))
    return 0


def render(s: dict, path: Path) -> None:
    r, d = s["runtime"], s["d16_reexecution"]
    lines = [
        "# Reverificação da missão stocks — 2026-09-24 (depois do merge do #20 e do #21)",
        "",
        "Gerado por `d16/recheck_summary.py` a partir de `RAW_LOGS/d16/recheck-20260924/RECHECK_SUMMARY.json` (logs brutos"
        " nessa pasta). Reexecuta o que dá para reexecutar fora do PC 1; não decide gate nem muda a attestation.",
        "",
        "## CI hospedado (workflow_dispatch)",
        "",
        "| Repo | Workflow | Commit | Conclusão | Jobs |",
        "|---|---|---|---|---|",
        *[f"| {k.split('_')[1]} | {v['workflow']} | `{v['head'][:7]}` | {v['conclusion']} | "
          + ", ".join(f"{j}: {c}" for j, c in v["jobs"].items()) + " |" for k, v in s["ci"].items()],
        "",
        "## Runtime da Etapa A com as wheels publicadas (stocks-runtime.yml, fora do checkout)",
        "",
        "| Ambiente | Wheel | lock | Conformidade | E2E sintético | Soak diag. | Suíte legada contra a wheel |",
        "|---|---|---|---|---|---|---|",
        *[f"| {k.replace('stocks-runtime-', '')} | `{v['wheel_sha256'][:12]}…` | exit {v['uv_lock_check_exit']} | {v['conformance']} "
          f"(exit {v['conformance_exit']}) | {v['e2e_checks']} | "
          f"{'não roda neste ambiente (só Linux)' if v['soak_zero_tolerance_ok'] is None else v['soak_zero_tolerance_ok']} | "
          f"{v['full_suite_against_wheel']} "
          f"(exit {v['full_suite_exit']}) — ST-F004 |" for k, v in r.items()],
        "",
        "## Suíte completa no checkout do alvo (stocks-suite.yml, uv sync --locked)",
        "",
        *[f"* {k.replace('stocks-suite-', '')}: `{v['head'][:7]}` — {v['pytest']} (exit {v['pytest_exit']}); doctor exit {v['doctor_exit']}"
          for k, v in s["suite"].items()],
        "",
        "## Build reprodutível da rc (stocks-build-rc.yml)",
        "",
        f"* {s['build_rc']['run']}: {s['build_rc']['distributions']}; wheel = asset publicado: {s['build_rc']['wheel_equals_published']}",
        "",
        "## Conjunto protegido (parte git; dados de C:\\STOCKS\\data só no PC 1, não re-hasheados)",
        "",
        *[f"* `{c}`: {v['items']} itens, {v['changed']} mudados, {v['missing']} ausentes, {v['new']} novos" for c, v in s["protected_git"].items()],
        "",
        "## Attestation e parciais no main",
        "",
        f"* `QUALIFICATION_ATTESTATION.json` (`{s['attestation_main']['sha256'][:12]}…`) no main `{s['attestation_main']['commit'][:7]}`: "
        + ", ".join(f"{k}: {'ok' if v else 'FALHA'}" for k, v in s["attestation_main"]["rules"].items()),
        f"* {s['partials_main']['partials']} parciais, {s['partials_main']['evidence_intact']} com toda evidência íntegra no commit de "
        f"emissão; checagens que divergiram: {s['partials_main']['failed_checks']} (esperado: o estado agora é 31 PASS)",
        "",
        "## Reexecução da D-16 (pin novo às 13:09 UTC; mesmo painel)",
        "",
        f"* gates: {d['gates']}",
        f"* painel igual ao da evidência nos 3 jobs: {d['same_panel_as_evidence']}; métricas econômicas iguais: "
        f"{d['same_economic_metrics_as_evidence']}; contagens dos controles iguais: {d['same_negative_control_counts']}",
        f"* soak: {d['soak_counts']}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
