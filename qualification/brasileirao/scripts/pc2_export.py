"""brasileirao: separa a saída do run D-16 do PC 2 entre evidência (sem registros do dado) e privado.

PRIV guarda tudo que o circuito imprime com o dado real (resultados `show` com previsões por jogo,
commands.log do real_env.py). Daqui vão para OUT só arquivos que não carregam registros:
  real.log, real/runs.json, real/dataset_capture.json, real/policy.json,
  real/outcome_*.jsonl e e2e_real/process_1.stdout.jsonl (linhas de outcome: ids, estados, caminhos;
  recusadas se tiverem result/predictions/domain_facts), e2e_real/E2E_SUMMARY.json,
  e2e_real/process_1.stderr.log (logs do Ops), e os artefatos do Ops do pedido do E2E (jobs file,
  events.jsonl, heartbeat.json, idempotency_record.json).
O resto fica em PRIV; OUT/private_manifest.sha256 lista o sha256 de cada arquivo de PRIV (caminho relativo).

Uso: python pc2_export.py --priv <dir> --out <dir> --state <estado do real_env>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

FORBIDDEN_KEYS = {"result", "predictions", "domain_facts"}


def outcome_lines_ok(path: Path) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and FORBIDDEN_KEYS & set(json.loads(line)):
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--state", type=Path, required=True)
    args = ap.parse_args()
    copied, refused = [], []

    def put(src: Path, rel: str, *, outcome: bool = False) -> None:
        if not src.is_file():
            refused.append({"file": rel, "why": "ausente"})
            return
        if outcome and not outcome_lines_ok(src):
            refused.append({"file": rel, "why": "linha de outcome com resultado completo"})
            return
        dst = args.out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append(rel)

    put(args.priv / "real.log", "real/real.log")
    for name in ("runs.json", "dataset_capture.json", "policy.json"):
        put(args.priv / "real" / name, f"real/{name}")
    for path in sorted((args.priv / "real").glob("outcome_*.jsonl")):
        put(path, f"real/{path.name}", outcome=True)
    put(args.priv / "e2e_real" / "E2E_SUMMARY.json", "e2e_real/E2E_SUMMARY.json")
    put(args.priv / "e2e_real" / "process_1.stdout.jsonl", "e2e_real/process_1.stdout.jsonl", outcome=True)
    put(args.priv / "e2e_real" / "process_1.stderr.log", "e2e_real/process_1.stderr.log")
    first = json.loads((args.priv / "e2e_real" / "process_1.stdout.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    exp = first["experiment_id"].split("-", 1)[1]
    for path in sorted((args.state / "x" / "e" / exp[:16]).glob("ops-job.*.json")):
        put(path, f"e2e_real/ops/{path.name}")
    job = args.state / "x" / "o" / f"brasileirao-research-{exp[:24]}"
    for name in ("events.jsonl", "heartbeat.json"):
        put(job / name, f"e2e_real/ops/{name}")
    # o registro de idempotência do Ops fica em x/o/idempotency/<economic_lock_id>.json, com o job_id dentro
    records = [p for p in sorted((args.state / "x" / "o" / "idempotency").glob("*.json"))
               if json.loads(p.read_text(encoding="utf-8")).get("job_id") == job.name]
    if len(records) == 1:
        put(records[0], "e2e_real/ops/idempotency_record.json")
    else:
        refused.append({"file": "e2e_real/ops/idempotency_record.json", "why": f"{len(records)} registros para {job.name}"})
    manifest = []
    for path in sorted(p for p in args.priv.rglob("*") if p.is_file()):
        manifest.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(args.priv).as_posix()}")
    (args.out / "private_manifest.sha256").write_text("\n".join(manifest) + "\n", encoding="utf-8", newline="\n")
    (args.out / "export.json").write_text(json.dumps({"copied": copied, "refused": refused, "private_files": len(manifest)},
                                                     indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"copied": len(copied), "refused": refused, "private_files": len(manifest)}, ensure_ascii=False))
    return 0 if not refused else 1


if __name__ == "__main__":
    raise SystemExit(main())
