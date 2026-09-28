"""integration-stocks, fase hosted-ci (C21, HOSTED_CI): runs de push dos repositórios da missão nos SHAs exatos.

Só vale o run de `push` cujo `headSha` é exatamente o commit (run de pull_request testa outro SHA e não vale). Para
cada (repo, commit, papel) grava o JSON bruto de `gh run list --commit` e de `gh run view` (jobs) em
RAW_LOGS/hosted-ci/ e resume: todos os workflows de push concluídos com success, nenhum job pulado sem motivo.
Core e Ops não mudam nesta missão: o CI deles é o da Etapa A (HERDADO, citado no relatório, não recoletado aqui).

Adaptado de qualification/integration-crypto/scripts/hosted_ci.py (mesma lógica; missão integration-stocks).
Também grava, só como registro (não conta para o PASS), os runs de qualquer evento no SHA
(workflow_dispatch do stocks-predictor: IS-F004).
Uso: python hosted_ci.py <targets.json> <out_dir>
  targets.json: [{"repo": "owner/name", "commit": "<40 hex>", "role": "baseline|final"}, ...]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def main() -> int:
    targets = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for t in targets:
        repo, commit, role = t["repo"], t["commit"], t["role"]
        raw = gh("run", "list", "-R", repo, "--commit", commit, "--event", "push", "-L", "50", "--json",
                 "databaseId,name,headSha,headBranch,event,status,conclusion,url,createdAt,updatedAt")
        name = f"{repo.split('/')[1]}_{role}_{commit[:12]}"
        (out / f"{name}_runs.json").write_text(raw, encoding="utf-8")
        every = gh("run", "list", "-R", repo, "--commit", commit, "-L", "50", "--json",
                   "databaseId,name,headSha,headBranch,event,status,conclusion,url,createdAt,updatedAt")
        (out / f"{name}_runs_all_events.json").write_text(every, encoding="utf-8")
        runs = [r for r in json.loads(raw) if r["headSha"] == commit]
        latest: dict[str, dict] = {}
        for r in sorted(runs, key=lambda r: r["createdAt"]):
            latest[r["name"]] = r
        jobs = {}
        for wf, r in latest.items():
            view = gh("run", "view", str(r["databaseId"]), "-R", repo, "--json", "jobs,conclusion,status,headSha,url")
            (out / f"{name}_{r['databaseId']}_jobs.json").write_text(view, encoding="utf-8")
            jobs[wf] = [{"name": j["name"], "conclusion": j["conclusion"]} for j in json.loads(view)["jobs"]]
        ok = bool(latest) and all(r["status"] == "completed" and r["conclusion"] == "success" for r in latest.values())
        failing = {wf: [j["name"] for j in js if j["conclusion"] not in ("success",)] for wf, js in jobs.items()}
        summary.append({"repo": repo, "commit": commit, "role": role, "ok": ok,
                        "runs": {wf: {"id": r["databaseId"], "url": r["url"], "status": r["status"],
                                      "conclusion": r["conclusion"]} for wf, r in latest.items()},
                        "non_success_jobs": {wf: v for wf, v in failing.items() if v}})
    (out / "HOSTED_CI_SUMMARY.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    for s in summary:
        print(("OK  " if s["ok"] else "FAIL"), s["repo"], s["role"], s["commit"][:12], s["non_success_jobs"] or "")
    return 0 if all(s["ok"] for s in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
