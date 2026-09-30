#!/usr/bin/env python3
"""Substituto mínimo do `gh` para hosts sem o gh CLI (sessão de 2026-09-30): só leitura anônima da API pública do GitHub.
Subcomandos atendidos, com a MESMA forma de saída que os scripts das missões esperam:
  gh api <path>
  gh run list -R <owner/repo> --commit <sha> [--event push] [-L n] --json <campos>
  gh run view <id> -R <owner/repo> --json jobs,conclusion,status,headSha,url
  gh release download <tag> -R <owner/repo> -p <asset> -D <dir>
Qualquer outra forma falha fechado (exit 2). Nenhum token; repositórios públicos.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

API = "https://api.github.com"


def get(path: str, raw: bool = False):
    out = subprocess.run(["curl", "-sS", "--fail", "-L", "-H", "Accept: application/vnd.github+json", f"{API}/{path.lstrip('/')}"],
                         capture_output=True, check=True).stdout
    return out if raw else json.loads(out)


def opt(args: list[str], name: str, default=None):
    return args[args.index(name) + 1] if name in args else default


def run_row(r: dict) -> dict:
    return {"databaseId": r["id"], "name": r["name"], "headSha": r["head_sha"], "headBranch": r["head_branch"],
            "event": r["event"], "status": r["status"], "conclusion": r["conclusion"], "url": r["html_url"],
            "createdAt": r["created_at"], "updatedAt": r["updated_at"], "workflowName": r["name"], "number": r["run_number"]}


def main(argv: list[str]) -> int:
    if argv[:1] == ["api"]:
        sys.stdout.write(get(argv[1], raw=True).decode("utf-8"))
        return 0
    if argv[:2] == ["run", "list"]:
        repo = opt(argv, "-R"); commit = opt(argv, "--commit"); event = opt(argv, "--event"); limit = int(opt(argv, "-L", opt(argv, "--limit", "30")))
        fields = opt(argv, "--json", "").split(",")
        q = {"per_page": min(limit, 100)}
        if commit:
            q["head_sha"] = commit
        if event:
            q["event"] = event
        rows = [run_row(r) for r in get(f"repos/{repo}/actions/runs?{urllib.parse.urlencode(q)}")["workflow_runs"]][:limit]
        print(json.dumps([{k: r.get(k) for k in fields} if fields != [""] else r for r in rows]))
        return 0
    if argv[:2] == ["run", "view"]:
        run_id = argv[2]; repo = opt(argv, "-R")
        run = get(f"repos/{repo}/actions/runs/{run_id}")
        jobs = get(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100")["jobs"]
        doc = {"jobs": [{"name": j["name"], "conclusion": j["conclusion"], "status": j["status"], "databaseId": j["id"],
                         "url": j["html_url"], "startedAt": j["started_at"], "completedAt": j["completed_at"]} for j in jobs],
               "conclusion": run["conclusion"], "status": run["status"], "headSha": run["head_sha"], "url": run["html_url"],
               "databaseId": run["id"], "name": run["name"], "event": run["event"]}
        fields = opt(argv, "--json", "").split(",")
        print(json.dumps({k: doc.get(k) for k in fields} if fields != [""] else doc))
        return 0
    if argv[:2] == ["release", "download"]:
        tag = argv[2]; repo = opt(argv, "-R"); pattern = opt(argv, "-p"); dest = Path(opt(argv, "-D", "."))
        dest.mkdir(parents=True, exist_ok=True)
        try:
            rel = get(f"repos/{repo}/releases/tags/{tag}")
            names = [a["name"] for a in rel["assets"] if pattern is None or a["name"] == pattern]
        except subprocess.CalledProcessError:
            # API de releases fechada para leitura anônima (ex.: stocks-predictor): o asset público ainda baixa pela URL direta
            if pattern is None:
                raise
            names = [pattern]
        for name in names:
            subprocess.run(["curl", "-sS", "--fail", "-L", "-o", str(dest / name),
                            f"https://github.com/{repo}/releases/download/{tag}/{name}"], check=True)
        return 0
    print(f"gh_shim: forma não suportada: {' '.join(argv)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
