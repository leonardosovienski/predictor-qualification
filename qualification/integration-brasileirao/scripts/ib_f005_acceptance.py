"""integration-brasileirao: aplica a decisão do dono sobre o CI do brasileirao-predictor (IB-F005) à C24.3 (f) e à C21.

Decisão do dono no chat da sessão (2026-09-28, pergunta com opções): "Aceitar precedente (Recommended)". Só para o
brasileirao-predictor, o run de pull_request do CI Pipeline com head = final_commit e o run de push do
publication-validation no SHA exato, ambos verdes, valem como o CI de C21 / prompt 10.3 / C24.3 (f), como na Etapa A
(o ci.yml do domínio só dispara push em main). Adaptado da ideia de qualification/integration-stocks/scripts/
hosted_ci_owner_acceptance.py. Este script não relaxa nada sozinho: confere, com dados coletados agora pelo gh, que
  * a decisão está registrada no FINDINGS.json (IB-F005 ACCEPTED_LIMITATION, com as palavras do dono);
  * existe um run do CI Pipeline, evento pull_request, headSha == final_commit, concluído com success, todos os jobs
    success ou skipped;
  * existe um run do "Scoped synthetic publication validation", evento push, headSha == final_commit, concluído com
    success, todos os jobs success;
e grava o resultado (accepted só é true se tudo isso vale).
Uso: python ib_f005_acceptance.py <qualification/integration-brasileirao> <final_commit> <out.json>
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = "leonardosovienski/brasileirao-predictor"
WORDS = "Aceitar precedente (Recommended)"


def gh(*args: str):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout)


def main() -> int:
    q, final, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    checks = []

    def ok(name, cond, **detail):
        checks.append({"check": name, "ok": bool(cond), **detail})

    f5 = next(f for f in json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))["findings"] if f["id"] == "IB-F005")
    ok("IB-F005 ACCEPTED_LIMITATION with the owner's words", f5["status"] == "ACCEPTED_LIMITATION"
       and f5.get("owner_decision_taken", {}).get("words") == WORDS, status=f5["status"])
    runs = gh("run", "list", "-R", REPO, "--commit", final, "--limit", "50", "--json",
              "databaseId,name,event,headSha,headBranch,status,conclusion,url,createdAt")
    picked = {}
    for name, event, allowed in (("CI Pipeline", "pull_request", {"success", "skipped"}),
                                 ("Scoped synthetic publication validation", "push", {"success"})):
        found = [r for r in runs if r["name"] == name and r["event"] == event and r["headSha"] == final]
        latest = max(found, key=lambda r: r["createdAt"]) if found else None
        jobs = {}
        if latest:
            jobs = {j["name"]: j["conclusion"] for j in
                    gh("run", "view", str(latest["databaseId"]), "-R", REPO, "--json", "jobs")["jobs"]}
        good = bool(latest) and latest["status"] == "completed" and latest["conclusion"] == "success" and bool(jobs) \
            and set(jobs.values()) <= allowed and "success" in jobs.values()
        ok(f"{name} ({event}) on the exact final_commit, green", good, run=latest, jobs=jobs)
        picked[name] = latest
    doc = {"schema": "integration-brasileirao/IB_F005_ACCEPTANCE/1", "final_commit": final, "decision_words": WORDS,
           "checks": checks, "accepted": all(c["ok"] for c in checks),
           "runs": {k: (v or {}).get("url") for k, v in picked.items()}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": doc["accepted"], "runs": doc["runs"]}))
    return 0 if doc["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
