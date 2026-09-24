"""Missão crypto: resumo da revalidação completa (reexecução dos gates depois do fechamento da D-16),
tirado só dos logs brutos de RAW_LOGS/<pasta> e comparado com as referências já versionadas
(V1.1 e run D-16 definitivo). Não altera gate nem attestation: é reconfirmação.

Uso: python revalidation_summary.py revalidacao-20260924 [--out REVALIDACAO_20260924.md]
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "crypto"
RAW = QC / "RAW_LOGS"
REF_RUNTIME = RAW / "cleanroom-final" / "run35925914768"
REF_OPS = RAW / "ops-failure-v1.1"
REF_D16 = RAW / "d16" / "35978221282"


def junit(path: Path) -> tuple[dict, list[str]]:
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root[0]
    failed = sorted(f"{c.get('classname')}::{c.get('name')}" for c in root.iter("testcase")
                    if c.find("failure") is not None or c.find("error") is not None)
    return {k: int(suite.get(k, 0)) for k in ("tests", "failures", "errors", "skipped")}, failed


def last_exit(path: Path) -> int | None:
    found = re.findall(r"\[exit (\d+)\]", path.read_text(encoding="utf-8", errors="replace"))
    return int(found[-1]) if found else None


def soak(path: Path) -> dict:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    summary = next(r for r in rows if r["kind"] == "summary")
    faults: dict[str, int] = {}
    for r in rows:
        if r["kind"] == "process":
            faults[r.get("fault") or "none"] = faults.get(r.get("fault") or "none", 0) + 1
    corruption = [r for r in rows if r["kind"] == "corruption"]
    return {"calls": sum(faults.values()), "faults": dict(sorted(faults.items())),
            "corruptions": len(corruption),
            "corruptions_fail_closed": sum(1 for r in corruption if r["show_exit"] == 5 and r["retry_exit"] == 5
                                           and r["file_not_repaired"]),
            "results": summary["stored_results"], "expected": summary["requests_with_result"],
            "lost": len(summary["lost"]), "unexpected": len(summary["unexpected"]),
            "violations": len(summary["violations"]), "reread_mismatch": len(summary["reread_mismatch"]),
            "ops_success_per_job_max": summary["ops_success_per_job_max"], "reconcile_exit": summary["reconcile_exit"],
            "reconcile_foreign": len(summary.get("reconcile_foreign_findings") or []),
            "reconcile_missed": len(summary.get("reconcile_missed_corruptions") or []),
            "zero_tolerance_ok": next(r for r in rows if r["kind"] == "verdict")["zero_tolerance_ok"]}


def d16(folder: Path) -> dict:
    env = (folder / "env.log").read_text(encoding="utf-8", errors="replace")
    head = dict(re.findall(r"(\w+)=(\S+)", env.splitlines()[0]))
    science = json.loads((folder / "science" / "SCIENCE_REAL.json").read_text(encoding="utf-8"))
    manifest = json.loads((folder / "data_MANIFEST.json").read_text(encoding="utf-8"))
    files = [f for f in manifest["files"] if "copy_sha256" in f]
    return {"where": head.get("where"), "commit": head.get("commit"), "wheel_sha256": head.get("sha256"),
            "done": re.search(r"^done ", env, re.M) is not None, "setup_fail": "SETUP FAIL" in env,
            "blocked": "BLOCKED" in env,
            "exits": {s: last_exit(folder / f"{s}.log") for s in ("e2e_real", "e2e_cases", "science", "soak_real", "conformance")},
            "e2e_real": json.loads((folder / "e2e_real" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["all_ok"],
            "e2e_cases": json.loads((folder / "e2e_cases" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["all_ok"],
            "conformance": junit(folder / "conformance.junit.xml")[0],
            "economic": {k: science["economic_metrics"][k] for k in ("gross_return_bps", "gross_ci_bps", "net_return_bps",
                                                                   "net_ci_bps", "sample_size", "scientific_state", "economic_state")},
            "controls": {"future_injection": science["negative_controls"]["future_injection"]["accepted_results"],
                         "temporal_ablation": science["negative_controls"]["temporal_ablation"]["accepted_results"],
                         "shuffled_supported": science["negative_controls"]["shuffled_labels"]["supported"],
                         "canary_leaks": len(science["future_canary"]["leaks"])},
            "data": {"files": len(files), "checksum_ok": sum(f["published_sha256"] == f["copy_sha256"] for f in files),
                     "objects": {k: v["sha256"] for k, v in manifest["objects"].items()}},
            "soak": soak(folder / "soak_real.jsonl")}


def runtime(folder: Path, ref: Path) -> dict:
    out = {}
    for name in ("conformance", "full_suite"):
        (counts, failed), (ref_counts, ref_failed) = junit(folder / f"{name}.junit.xml"), junit(ref / f"{name}.junit.xml")
        out[name] = {**counts, "same_failures_as_v1_1": failed == ref_failed, "v1_1": ref_counts}
    out["e2e"] = json.loads((folder / "e2e" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["all_ok"]
    identity = json.loads((folder / "core_identity.json").read_text(encoding="utf-8"))["packages"]
    identity = identity if isinstance(identity, list) else list(identity.values())
    out["wheels"] = {p["name"]: (p.get("direct_url") or {}).get("archive_info", {}).get("hash", "") for p in identity
                     if p["name"] in ("cripto-predictor", "predictor-core", "predictor-ops")}
    out["done"] = "done " in (folder / "env.log").read_text(encoding="utf-8", errors="replace")
    if (folder / "soak.jsonl").exists():
        out["soak"] = soak(folder / "soak.jsonl")
    return out


def ops(folder: Path) -> dict:
    summary = json.loads((folder.parent / "OPS_FAILURE_SUMMARY.json").read_text(encoding="utf-8"))["sources"]
    reference = json.loads((REF_OPS / "OPS_FAILURE_SUMMARY.json").read_text(encoding="utf-8"))["sources"]
    keys = ("shared003_test", "shared004_tests", "full_tests_v2", "probe_real_tree", "probe_startup",
            "probe_test_exact", "probe_a_b_delay")

    def view(src: dict) -> dict:
        out = {}
        for envs in src.values():
            for env, data in envs.items():
                out[env] = {k: {kk: vv for kk, vv in data[k].items() if isinstance(vv, (int, bool))} for k in keys if k in data}
        return out

    now, ref = view(summary), view(reference)
    lockrace = {}
    for env_dir in sorted(folder.iterdir()):
        logs = sorted(env_dir.glob("shared005_lockrace_run*.log"))
        lockrace[env_dir.name] = {"runs": len(logs), "exit_0": sum(1 for p in logs if "[exit 0]" in p.read_text(
            encoding="utf-8", errors="replace"))}
    return {"per_env": now, "same_as_v1_1": now == ref, "lockrace": lockrace}


def ci(folder: Path) -> list[dict]:
    rows = []
    for run_file in sorted(folder.glob("run_*.json")):
        run = json.loads(run_file.read_text(encoding="utf-8"))
        jobs = json.loads(run_file.with_name(run_file.name.replace("run_", "jobs_", 1)).read_text(encoding="utf-8"))["jobs"]
        log = run_file.with_name(f"log_{run['repository']['name']}_{run['id']}_attempt{run['run_attempt']}.txt")
        counts = sorted(set(re.findall(r"\d+ passed(?:, \d+ skipped)?", log.read_text(encoding="utf-8", errors="replace")))) if log.exists() else []
        rows.append({"repo": run["repository"]["name"], "sha": run["head_sha"][:7], "run": run["id"], "attempt": run["run_attempt"],
                     "event": run["event"], "conclusion": run["conclusion"],
                     "jobs": {j["name"]: j["conclusion"] for j in jobs}, "pytest": counts})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="REVALIDACAO_20260924.md")
    args = ap.parse_args()
    base = RAW / args.folder
    [d16_dir] = sorted((base / "d16").iterdir())
    new, ref = d16(d16_dir), d16(REF_D16)
    [rt_dir] = sorted((base / "runtime").iterdir())
    rt = {env: runtime(rt_dir / f"crypto-runtime-{env}", REF_RUNTIME / f"crypto-runtime-{env}") for env in ("linux-primary", "windows-latest")}
    [ops_dir] = sorted(p for p in (base / "ops-failure").iterdir() if p.is_dir())
    op = ops(ops_dir)
    runs = ci(base / "ci-reruns")
    local = {p.name: [l for l in p.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
             for p in sorted((base / "local").glob("*.log"))}
    data = {"d16": new, "d16_same_as_definitive": {k: new[k] == ref[k] for k in ("e2e_real", "e2e_cases", "conformance",
                                                                                 "economic", "controls", "data", "soak", "exits")},
            "runtime": rt, "ops_failure": op, "ci_reruns": runs}
    (base / "revalidation_numbers.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    s = new["soak"]
    lines = [
        "# REVALIDACAO_20260924 — missão crypto (reexecução completa depois do fechamento da D-16)",
        "",
        "Pedido do dono: \"confere e executa tudo\". Reexecução de todos os gates que podem ser reexecutados, no alvo",
        f"congelado (cripto `{new['commit'][:7]}`, wheel `{new['wheel_sha256'][:8]}…`, core 3.2.1, ops 4.2.2rc1), sem mudar",
        "parâmetro, vetor, perfil ou limiar. **Não altera gate nem attestation**: é reconfirmação. Números gerados por",
        f"`scripts/revalidation_summary.py` a partir de `RAW_LOGS/{args.folder}/` (também em `revalidation_numbers.json`).",
        "",
        f"## D-16 (dados reais, Linux primário): run {d16_dir.name}",
        "",
        f"- `where={new['where']}`, `done`={new['done']}, `SETUP FAIL`={new['setup_fail']}, `BLOCKED`={new['blocked']}; exits {new['exits']}.",
        f"- E2E real all_ok={new['e2e_real']}; casos A/B/C all_ok={new['e2e_cases']}; conformidade {new['conformance']}.",
        f"- Soak real: {s['calls']} chamadas, falhas {s['faults']}, corrupções {s['corruptions']} (falha fechada em {s['corruptions_fail_closed']});"
        f" {s['results']}/{s['expected']} resultados, perdidos {s['lost']}, inesperados {s['unexpected']}, violações {s['violations']},"
        f" releitura divergente {s['reread_mismatch']}, SUCCEEDED por job ≤ {s['ops_success_per_job_max']}, reconcile exit {s['reconcile_exit']}"
        f" (estranhos {s['reconcile_foreign']}, não acusados {s['reconcile_missed']}), `zero_tolerance_ok={s['zero_tolerance_ok']}`.",
        f"- Econômico: {new['economic']}. Controles: {new['controls']}.",
        f"- Dados: {new['data']['checksum_ok']}/{new['data']['files']} conferidos pelo `.CHECKSUM`.",
        f"- Igual ao run definitivo 35978221282, campo a campo: {data['d16_same_as_definitive']}.",
        "",
        f"## Runtime suportado (cleanroom, identidade, conformidade, suíte pela wheel, E2E, soak sintético): {rt_dir.name}",
        "",
    ]
    for env, r in rt.items():
        lines.append(f"- **{env}**: done={r['done']}; conformidade {r['conformance']['tests']} testes, falhas {r['conformance']['failures']},"
                     f" skip {r['conformance']['skipped']}; suíte pela wheel {r['full_suite']['tests']} testes, falhas {r['full_suite']['failures']}"
                     f" (as mesmas da V1.1: {r['full_suite']['same_failures_as_v1_1']}; CR-F016); E2E all_ok={r['e2e']}; wheels {r['wheels']}.")
        if "soak" in r:
            rs = r["soak"]
            lines.append(f"  Soak sintético: {rs['calls']} chamadas, {rs['results']} resultados, perdidos {rs['lost']}, violações {rs['violations']},"
                         f" corrupções {rs['corruptions']}, `zero_tolerance_ok={rs['zero_tolerance_ok']}`.")
    lines += ["", f"## Ops (SHARED-003/004/005): {ops_dir.name}", "",
              f"- Mesmos números da V1.1 em todos os ambientes: {op['same_as_v1_1']}.",
              f"- Corrida de lock (SHARED-005): {op['lockrace']}.", ""]
    for env, v in op["per_env"].items():
        lines.append(f"- {env}: " + "; ".join(f"{k} {v[k]}" for k in v))
    lines += ["", "## CI hospedado (reexecutado nos commits do baseline e finais; `gh run rerun`)", "",
              "| Repo | Commit | Run | Tentativa | Evento | Resultado | Jobs | pytest |", "|---|---|---|---|---|---|---|---|"]
    for r in runs:
        jobs = ", ".join(f"{k}={v}" for k, v in r["jobs"].items())
        lines.append(f"| {r['repo']} | `{r['sha']}` | {r['run']} | {r['attempt']} | {r['event']} | {r['conclusion']} | {jobs} | {'; '.join(r['pytest'])} |")
    lines += ["", "O run Release do predictor-ops **não** foi reexecutado (publicaria asset; nunca sobrescrever).", "",
              "## Verificações determinísticas (PC 2, `local/`)", ""]
    for name, content in local.items():
        lines.append(f"- `{name}`:")
        lines += [f"  - {l.strip()}" for l in content if not l.startswith("$") and "tmp." not in l]
    lines += ["", "## Não reexecutável aqui", "",
              "- Windows local (secundário, D-3): é o PC 1 (`C:\\Cripto\\qualificacao\\runtime\\`). No PC 2 as regras proíbem escrever em",
              "  `/mnt/c`. A evidência de `WINDOWS_SMOKE` continua a da V1.1; o `windows-latest` acima é informação adicional.", ""]
    (QC / args.out).write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(json.dumps({"d16_same": data["d16_same_as_definitive"], "ops_same": op["same_as_v1_1"],
                      "ci": [(r["repo"], r["sha"], r["conclusion"]) for r in runs]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
