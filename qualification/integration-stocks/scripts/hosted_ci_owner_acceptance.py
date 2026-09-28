"""integration-stocks, reemissão 1: aplica a decisão do dono sobre o CI do stocks-predictor (IS-F004 e IS-F005, opção b).

Decisão do dono no chat da sessão (2026-09-28): "aceita o run workflow_dispatch (b) e reemite". Só para o
stocks-predictor, o run workflow_dispatch do CI Pipeline no SHA exato vale como o run de C21 / prompt 9.3 e de
C24.3 (f), desde que o job secrets esteja vermelho só pelo falso positivo pré-existente, fora da branch da missão.
Este script não relaxa nada sozinho. Ele confere, com dados coletados agora pelo gh, que o run é o que a decisão
descreve, e grava o resultado:
  * a decisão está registrada no FINDINGS.json (IS-F004 e IS-F005 com status ACCEPTED_LIMITATION e as palavras do dono);
  * o run é workflow_dispatch do CI Pipeline, com headSha igual ao final_commit, e só o job secrets falhou;
  * no log do job secrets, o gitleaks acusa exatamente 1 vazamento, e o commit dele não é ancestral do final_commit;
  * os passos do job secrets: o gitleaks falhou, os passos seguintes ficaram pulados por isso (registrados) e o
    upload final falhou por falta dos arquivos desses passos;
  * a base (61fc017) tem o run workflow_dispatch da Etapa A com todos os jobs verdes.
Uso: python hosted_ci_owner_acceptance.py <qualification/integration-stocks> <clone do stocks-predictor> <out_dir>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "leonardosovienski/stocks-predictor"
FINAL = "6f857b232eaa63f3fccda6a16f92dbfc8983ab3b"
BASE = "61fc017256ffea815ae96bbe02b847dccdb395cc"
FINAL_RUN = 36363108348
BASE_RUN = 35953418753
DECISION_WORDS = "aceita o run workflow_dispatch (b) e reemite"


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def main() -> int:
    mission, clone, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    findings = {f["id"]: f for f in json.loads((mission / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]}
    for fid in ("IS-F004", "IS-F005"):
        f = findings[fid]
        check(f"{fid}: decisão do dono registrada (ACCEPTED_LIMITATION, palavras do dono)",
              f["status"] == "ACCEPTED_LIMITATION" and f.get("owner_decision_taken", {}).get("words") == DECISION_WORDS,
              status=f["status"], decision=f.get("owner_decision_taken"))
    runs = {}
    for label, run_id in (("final", FINAL_RUN), ("base", BASE_RUN)):
        raw = gh("run", "view", str(run_id), "-R", REPO, "--json",
                 "databaseId,workflowName,event,headSha,headBranch,status,conclusion,createdAt,updatedAt,url,jobs")
        (out / f"stocks-predictor_run{run_id}.json").write_text(raw, encoding="utf-8")
        runs[label] = json.loads(raw)
    fr, br = runs["final"], runs["base"]
    jobs = {j["name"]: j for j in fr["jobs"]}
    check("final: CI Pipeline, workflow_dispatch, headSha == final_commit",
          fr["workflowName"] == "CI Pipeline" and fr["event"] == "workflow_dispatch" and fr["headSha"] == FINAL,
          workflow=fr["workflowName"], event=fr["event"], head_sha=fr["headSha"])
    quality = {n: j["conclusion"] for n, j in jobs.items() if n.startswith("Quality")}
    check("final: jobs Quality verdes", quality and all(c == "success" for c in quality.values()), quality=quality)
    failed = sorted(n for n, j in jobs.items() if j["conclusion"] != "success")
    check("final: o único job não verde é secrets", failed == ["secrets"], not_green=failed)
    secrets_job = jobs["secrets"]
    steps = [{"name": s["name"], "conclusion": s["conclusion"]} for s in secrets_job["steps"]]
    (out / "secrets_job_steps.json").write_text(json.dumps(steps, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    log = gh("run", "view", str(FINAL_RUN), "-R", REPO, "--job", str(secrets_job["databaseId"]), "--log")
    (out / f"stocks-predictor_run{FINAL_RUN}_secrets_job.log").write_text(log, encoding="utf-8")
    leaks = re.findall(r"leaks found: (\d+)", log)
    fingerprints = re.findall(r"Fingerprint:\s+(\S+)", log)
    check("final: gitleaks acusa exatamente 1 vazamento", leaks == ["1"] and len(fingerprints) == 1,
          leaks_found=leaks, fingerprints=fingerprints)
    outside = []
    for fp in fingerprints:
        commit, path, rule, line = fp.split(":")
        rc = subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", commit, FINAL]).returncode
        branches = subprocess.run(["git", "-C", str(clone), "branch", "-r", "--contains", commit],
                                  capture_output=True, text=True).stdout.split()
        outside.append({"commit": commit, "path": path, "rule": rule, "line": int(line),
                        "ancestor_of_final_commit": rc == 0, "remote_branches_containing": branches})
    check("final: o commit do vazamento não é ancestral do final_commit (fora da branch da missão)",
          outside and not any(o["ancestor_of_final_commit"] for o in outside), leaks=outside)
    # passos do job definidos no ci.yml do final_commit; os passos do runner (Set up job, Post Run, Complete job) não
    # entram na conta
    by_name = {s["name"]: s["conclusion"] for s in steps}
    gitleaks_step = [n for n in by_name if "gitleaks-action" in n]
    skipped_by_design = ["Scan the complete tracked tree including merged code",
                         "Prove an exempted file still detects a synthetic token"]
    upload = "Retain complete tree scan"
    other_failures = [n for n, c in by_name.items() if c == "failure" and n not in gitleaks_step + [upload]]
    check("final: passos do job secrets (gitleaks vermelho; varredura da árvore e controle pulados por isso; upload "
          "final sem os arquivos deles; nenhuma outra falha)",
          len(gitleaks_step) == 1 and by_name[gitleaks_step[0]] == "failure"
          and all(by_name.get(n) == "skipped" for n in skipped_by_design) and by_name.get(upload) == "failure"
          and "No files were found with the provided path" in log and not other_failures,
          steps=steps, other_failures=other_failures)
    after = [s for s in steps if s["name"] in skipped_by_design]
    check("base: run workflow_dispatch da Etapa A no SHA exato, todos os jobs verdes",
          br["event"] == "workflow_dispatch" and br["headSha"] == BASE and br["conclusion"] == "success"
          and all(j["conclusion"] == "success" for j in br["jobs"]),
          jobs={j["name"]: j["conclusion"] for j in br["jobs"]}, url=br["url"])
    doc = {"schema": "integration-stocks/HOSTED_CI_OWNER_ACCEPTANCE/1", "decision_words": DECISION_WORDS,
           "repo": REPO, "final_commit": FINAL, "final_run": fr["url"], "base_commit": BASE, "base_run": br["url"],
           "skipped_after_gitleaks": [s["name"] for s in after if s["conclusion"] == "skipped"],
           "checks": checks, "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks)}
    doc["accepted"] = doc["failed"] == 0
    (out / "stocks_dispatch_acceptance.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                                                          encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("accepted", "passed", "failed", "skipped_after_gitleaks")}, ensure_ascii=False))
    for c in checks:
        if not c["ok"]:
            print("FAILED", json.dumps(c, ensure_ascii=False)[:600])
    return 0 if doc["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
