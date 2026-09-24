"""brasileirao: varredura de segredos (gate SECRETS_CLEAN) na evidência e no diff da missão.

Padrões: blocos de chave privada, tokens do GitHub (ghp_/gho_/ghs_/github_pat_), chaves AWS (AKIA…),
tokens Slack, `Authorization: Bearer`, e atribuições de credencial por nome (api_key, apikey, secret,
token, password, passwd, ODDS_API_KEY, THE_ODDS_API_KEY, SPORTMONKS…, API_FOOTBALL…) com valor
literal de 12+ caracteres. Hex de hash (sha256, ids) não é segredo e não é marcado sozinho.

Uso: python scan_secrets.py --paths <dir|arquivo>... [--git-diff <repo> <base> <head>] --out <json>
Exit 1 se houver achado.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = {
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "slack_token": re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b"),
    "bearer": re.compile(r"(?i)authorization\s*[:=]\s*['\"]?bearer\s+[A-Za-z0-9._~+/-]{16,}"),
    "credential_assignment": re.compile(
        r"(?i)\b(?:[A-Z0-9_]*(?:API[_-]?KEY|APIKEY|SECRET|TOKEN|PASSWORD|PASSWD)|ODDS_API_KEY|X-RapidAPI-Key)\b"
        r"['\"]?\s*[:=]\s*['\"]([A-Za-z0-9_\-/+]{12,})['\"]"
    ),
}
SKIP_SUFFIX = {".sqlite", ".sqlite3", ".whl", ".gz", ".zip", ".png", ".xml"}


def scan_text(text: str, where: str, out: list) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS.items():
            if pattern.search(line):
                out.append({"path": where, "line": number, "kind": kind})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--git-diff", nargs=3, metavar=("REPO", "BASE", "HEAD"))
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    findings: list[dict] = []
    scanned = 0
    for root in args.paths:
        root = Path(root)
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in files:
            if path.suffix.lower() in SKIP_SUFFIX:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            scanned += 1
            scan_text(text, path.as_posix(), findings)
    diff_info = None
    if args.git_diff:
        repo, base, head = args.git_diff
        diff = subprocess.run(["git", "-C", repo, "diff", f"{base}..{head}"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", check=True).stdout
        added = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
        log = subprocess.run(["git", "-C", repo, "log", "--format=%B", f"{base}..{head}"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=True).stdout
        scan_text(added, f"git-diff {base}..{head} (linhas adicionadas)", findings)
        scan_text(log, f"git-log {base}..{head} (mensagens)", findings)
        diff_info = {"repo": repo, "base": base, "head": head, "added_lines": added.count("\n") + 1}
    doc = {"schema": "brasileirao/SECRETS_SCAN/1", "files_scanned": scanned, "git_diff": diff_info,
           "patterns": sorted(PATTERNS), "finding_count": len(findings), "findings": findings}
    args.out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"files_scanned": scanned, "finding_count": len(findings)}))
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
