"""brasileirao / truth-map: inventário de TODO ponto que lê ou cria data/hora (BR_TIMEZONE_INTEGRITY).

Só leitura (git show no commit). AST de todo .py de brasileirao_predictor/ e brasileirao_scripts/.
Chamadas inventariadas: fromisoformat, strptime, date.today, datetime.now, utcnow, fromtimestamp,
utcfromtimestamp, replace(tzinfo=...), astimezone, ZoneInfo. Para cada uma: arquivo, linha,
função, trecho e classificação automática:
  AWARE_CHECKED  — a mesma função exige tzinfo/utcoffset ou normaliza com astimezone
  UTC_EXPLICIT   — cria/converte com UTC explícito (now(UTC), fromtimestamp(ts, UTC))
  LOCAL_CLOCK    — relógio/calendário local (date.today(), now() sem fuso)
  NAIVE_PARSE    — fromisoformat/strptime sem checagem de fuso na mesma função
  ASSUMED_UTC    — replace(tzinfo=UTC) sobre valor sem fuso (regra declarada ou palpite)

Uso: python date_sites.py --repo <clone> --commit <sha> --out <json>
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from collections import Counter

PKGS = ("brasileirao_predictor/", "brasileirao_scripts/")
NAMES = {"fromisoformat", "strptime", "today", "now", "utcnow", "fromtimestamp", "utcfromtimestamp", "astimezone", "ZoneInfo"}


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def classify(call: ast.Call, func_src: str) -> str:
    name = call.func.attr if isinstance(call.func, ast.Attribute) else getattr(call.func, "id", "")
    args_src = [ast.unparse(a) for a in call.args] + [ast.unparse(k) for k in call.keywords]
    if name in {"now", "fromtimestamp"}:
        return "UTC_EXPLICIT" if any("UTC" in a or "timezone" in a for a in args_src) else "LOCAL_CLOCK"
    if name in {"today", "utcnow", "utcfromtimestamp"}:
        return "LOCAL_CLOCK" if name == "today" else "NAIVE_UTC_CLOCK"
    if name == "replace":
        return "ASSUMED_UTC"
    if name in {"astimezone", "ZoneInfo"}:
        return "AWARE_CHECKED"
    if "tzinfo" in func_src or "utcoffset" in func_src or "astimezone" in func_src:
        return "AWARE_CHECKED"
    return "NAIVE_PARSE"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    files = [p for p in git(args.repo, "ls-tree", "-r", "--name-only", args.commit).splitlines()
             if p.startswith(PKGS) and p.endswith(".py")]
    sites = []
    for path in files:
        src = git(args.repo, "show", f"{args.commit}:{path}")
        tree = ast.parse(src, filename=path)
        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        lines = src.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            name = node.func.attr
            is_tz_replace = name == "replace" and any(k.arg == "tzinfo" for k in node.keywords)
            if name not in NAMES and not is_tz_replace:
                continue
            if name == "now" and not ast.unparse(node.func.value).endswith("datetime"):
                continue
            if name == "today" and ast.unparse(node.func.value) not in {"date", "datetime.date", "datetime"}:
                continue
            owner = next((f for f in functions if f.lineno <= node.lineno <= (f.end_lineno or f.lineno)), None)
            func_src = "\n".join(lines[owner.lineno - 1 : owner.end_lineno]) if owner else ""
            sites.append({
                "file": path,
                "line": node.lineno,
                "function": owner.name if owner else "<module>",
                "call": name if not is_tz_replace else "replace(tzinfo=)",
                "snippet": lines[node.lineno - 1].strip()[:200],
                "class": classify(node, func_src),
                "research_package": path.startswith("brasileirao_predictor/research/"),
            })
    doc = {
        "schema": "brasileirao/DATE_SITES/1",
        "repo": "brasileirao-predictor",
        "commit": args.commit,
        "method": __doc__.splitlines()[0],
        "count": len(sites),
        "by_class": dict(Counter(s["class"] for s in sites)),
        "sites": sites,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(args.out, doc["count"], doc["by_class"])


if __name__ == "__main__":
    main()
