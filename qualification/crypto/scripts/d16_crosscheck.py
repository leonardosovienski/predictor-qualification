"""Missão crypto, D-16: conferências da "Etapa A se sustenta?" e cruzamento dos dados, saída JSON bruta.

  attestations                      cada ATTESTATION_PARTIAL_*.json e QUALIFICATION_ATTESTATION*.json conferido no
                                    commit em que foi gravado pela última vez: evidências dos gates, environments,
                                    vereditos compartilhados, findings_file e hashes de topo (C7.1 regra 3). O
                                    `attest.py check` só confere os gates, e só na árvore atual.
  wheels <dir> [--src <árvore>]     sha256 dos arquivos baixados das final_wheels (e do sdist do runtime_target)
                                    contra o registrado; RECORD da wheel do Cripto; com --src (git archive do
                                    commit do runtime_target), cada arquivo da wheel contra o source
  data <data_MANIFEST.json> <dir>   MANIFEST de um run da D-16 × .CHECKSUM publicado × cópia local já conferida
                                    (ex.: dados do pendrive), arquivo a arquivo, mais os datasets derivados

Uso: python d16_crosscheck.py attestations | wheels <dir> [--src <dir>] | data <manifest> <dir>
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "crypto"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)


def attestations() -> dict:
    files = git("ls-files", "qualification/crypto/ATTESTATION_PARTIAL_*.json",
                "qualification/crypto/QUALIFICATION_ATTESTATION*.json").stdout.decode().split()
    out = []
    for path in sorted(files):
        commit = git("log", "-1", "--format=%H", "--", path).stdout.decode().strip()

        def blob(p: str) -> bytes | None:
            r = git("show", f"{commit}:{p}")
            return r.stdout if r.returncode == 0 else None

        doc = json.loads(blob(path))
        checks: list[tuple[str, str, str]] = []
        for gate, state in doc["gates"].items():
            checks += [(f"gate {gate}", e["file"], e["sha256"]) for e in state["evidence"]]
        for env in doc.get("environments", []):
            checks += [(f"env {env['role']}", e["file"], e["sha256"]) for e in env["evidence"]]
        for v in doc.get("shared_dependency_verdicts", []):
            checks.append((f"verdict {v['issue_id']}", v["verdict_file"], v["verdict_sha256"]))
        checks.append(("findings_file", doc["findings_file"]["file"], doc["findings_file"]["sha256"]))
        top = {"frozen_parameters_sha256": "qualification/crypto/FROZEN_PARAMETERS.json",
               "protected_set_sha256": "qualification/crypto/PROTECTED_SET.json",
               "frozen_vectors_sha256": "qualification/crypto/FROZEN_VECTORS.json",
               "soak_profile_sha256": "qualification/crypto/QUALIFICATION_PROFILE_CRYPTO_V1.json",
               "common_core_sha256": "qualification/COMMON_QUALIFICATION_CORE.md",
               "common_baseline_sha256": f"qualification/shared/{doc['common_baseline_id']}.json",
               "domain_contract_sha256": "qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json"}
        checks += [(k, p, doc[k]) for k, p in top.items() if doc.get(k)]
        problems = []
        for where, file, expected in checks:
            data = blob(file)
            if data is None:
                problems.append({"where": where, "file": file, "problem": "ausente"})
            elif sha(data) != expected:
                problems.append({"where": where, "file": file, "problem": "sha256 divergente",
                                 "expected": expected, "got": sha(data)})
        statuses: dict[str, int] = {}
        for state in doc["gates"].values():
            statuses[state["status"]] = statuses.get(state["status"], 0) + 1
        out.append({"file": path, "commit": commit, "result": doc["result"], "gates": statuses,
                    "counts": doc["counts"], "checked": len(checks), "problems": problems})
    return {"attestations": out, "with_problems": [a["file"] for a in out if a["problems"]]}


def wheels(folder: Path, src: Path | None) -> dict:
    gates = json.loads((QC / "GATES.json").read_text(encoding="utf-8"))
    target = json.loads((QC / "runtime_target.json").read_text(encoding="utf-8"))
    expected = {w["url"].rsplit("/", 1)[1]: w["sha256"] for w in gates["final_wheels"]}
    expected[target["wheel_url"].rsplit("/", 1)[1].replace("-py3-none-any.whl", ".tar.gz")] = target["sdist_sha256"]
    files = {name: {"expected": value, "got": sha((folder / name).read_bytes()) if (folder / name).is_file() else None}
             for name, value in expected.items()}
    for item in files.values():
        item["ok"] = item["expected"] == item["got"]
    out: dict = {"files": files}
    wheel = folder / target["wheel_url"].rsplit("/", 1)[1]
    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        record = next(n for n in names if n.endswith(".dist-info/RECORD"))
        ok = bad = 0
        for row in csv.reader(archive.read(record).decode().splitlines()):
            if row and row[1]:
                algo, digest = row[1].split("=", 1)
                got = base64.urlsafe_b64encode(hashlib.new(algo, archive.read(row[0])).digest()).rstrip(b"=").decode()
                ok, bad = ok + (got == digest), bad + (got != digest)
        out["record"] = {"ok": ok, "bad": bad}
        if src is not None:
            forced = {"GarimpoInvestimentos/charters/": "charters/",
                      "GarimpoInvestimentos/observation_plans/": "observation_plans/"}
            same, differ, unpaired = 0, [], []
            for name in names:
                if ".dist-info/" in name:
                    continue
                relative = next((v + name[len(k):] for k, v in forced.items() if name.startswith(k)), name)
                source = src / relative
                if not source.is_file():
                    unpaired.append(name)
                elif source.read_bytes() == archive.read(name):
                    same += 1
                else:
                    differ.append(name)
            out["against_source"] = {"commit": target["commit"], "identical": same, "different": differ,
                                     "without_source": unpaired}
    out["all_ok"] = (all(f["ok"] for f in files.values()) and out["record"]["bad"] == 0
                     and (src is None or (not out["against_source"]["different"]
                                          and not out["against_source"]["without_source"])))
    return out


def data(manifest_path: Path, folder: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    local_manifest = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
    local_published = {f["url"]: f.get("published_sha256") for f in local_manifest["files"] if "url" in f}
    rows = []
    for f in manifest["files"]:
        if "copy_sha256" not in f:
            rows.append({"url": f.get("url"), "unavailable_in_run": f.get("unavailable"),
                         "unavailable_locally": "unavailable" in next(
                             (x for x in local_manifest["files"] if x.get("url") == f.get("url")), {})})
            continue
        name = f["url"].rsplit("/", 1)[1]
        local = folder / "raw" / name
        got = sha(local.read_bytes()) if local.is_file() else None
        rows.append({"file": name, "published": f["published_sha256"], "run_copy": f["copy_sha256"], "local": got,
                     "local_manifest_published": local_published.get(f["url"]),
                     "ok": f["published_sha256"] == f["copy_sha256"] == got == local_published.get(f["url"])})
    objects = {}
    for name, info in manifest["objects"].items():
        local = folder / name
        got = sha(local.read_bytes()) if local.is_file() else None
        objects[name] = {"run": info["sha256"], "rows": info["rows"], "local": got, "ok": got == info["sha256"]}
    files = [r for r in rows if "ok" in r]
    return {"files": rows, "objects": objects, "files_ok": sum(r["ok"] for r in files), "files_total": len(files),
            "all_ok": all(r["ok"] for r in files) and all(o["ok"] for o in objects.values())}


def main() -> None:
    mode = sys.argv[1]
    if mode == "attestations":
        result = attestations()
    elif mode == "wheels":
        src = Path(sys.argv[sys.argv.index("--src") + 1]) if "--src" in sys.argv else None
        result = wheels(Path(sys.argv[2]), src)
    elif mode == "data":
        result = data(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        raise SystemExit(__doc__)
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
