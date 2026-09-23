"""Extrai dos logs brutos (collect_run.sh) os fatos usados na evidência.

Para cada <repo>_run<id>.json/.log: commit, evento, conclusão do run e de cada job,
comandos `uv sync/lock/export` executados por job e linhas-resumo do pytest.
Uso: python extract_ci_facts.py <dir>
"""

import json
import re
import sys
from pathlib import Path

STEP = re.compile(r"##\[group\]Run (uv (?:sync|lock|export)[^\n]*)")
PYTEST = re.compile(r"(\d+ passed[^\n=]*)")


def main(folder: str) -> None:
    for meta_path in sorted(Path(folder).glob("*_run*.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"=== {meta_path.stem}  {meta['workflowName']} [{meta['event']}] "
              f"{meta['headSha']} -> {meta['conclusion']}  {meta['url']}")
        for job in meta["jobs"]:
            print(f"  job {job['name']}: {job['conclusion']}")
        installs: dict[str, set[str]] = {}
        tests: dict[str, list[str]] = {}
        log = meta_path.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
        for line in log.splitlines():
            parts = line.split("\t", 2)
            if len(parts) < 3:
                continue
            job, text = parts[0], parts[2]
            if m := STEP.search(text):
                installs.setdefault(job, set()).add(m.group(1).strip())
            elif m := PYTEST.search(text):
                tests.setdefault(job, []).append(m.group(1).strip())
        for job in sorted(installs):
            for command in sorted(installs[job]):
                print(f"  install {job}: {command}")
        for job in sorted(tests):
            for summary in tests[job]:
                print(f"  pytest {job}: {summary}")


if __name__ == "__main__":
    main(sys.argv[1])
