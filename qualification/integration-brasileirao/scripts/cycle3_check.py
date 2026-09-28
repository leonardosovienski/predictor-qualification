"""integration-brasileirao, ciclo 3 da freeze-parameters: conferência mecânica do que mudou e do que não pode mudar.

O ciclo 3 (R17 e R04 por hipótese na release única, publicada como cain v0.4.13rc10) não pode mudar nada que o
cain lê: decision_policy.brasileirao_config tem de ser igual ao do commit 417024e (o que o brasileirao.json da release
pina). Confere:
  1. brasileirao_config (ciclo 3) == brasileirao_config em `git show 417024e:FROZEN_PARAMETERS.json` == no arquivo
     preservado do ciclo 2 (sha256 do arquivo preservado == sha256 pinado no brasileirao.json da wheel);
  2. FROZEN_PARAMETERS: só decision_policy.framework, decision_policy.rule_order e cycle mudam em relação ao ciclo 2;
     a rule_order nova = a antiga + R17 entre R11 e R12 (R04 só com texto a mais);
  3. FROZEN_VECTORS: só os vetores declarados mudam (n1/01-next, contradiction/02-refuted e as tasks/resultados da
     contradição encadeados por previous_task_id) e só o n1/24-equivalent-request entra; e2e, holdout, soak e perfil
     sem mudança; cada arquivo listado bate com o sha256 do manifesto;
  4. o brasileirao.json dentro da wheel da release (sha256 conferido) pina frozen_parameters 417024e com o sha256 do
     arquivo do ciclo 2 e é, byte a byte, o que o tools/build_domain_config.py do commit da release gera a partir de
     417024e (<regenerado>, gerado antes por esse script e registrado no log da fase).
Uso: python cycle3_check.py <predictor-qualification> <wheel do cain> <sha256 da wheel> <regenerado.json> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

M = "qualification/integration-brasileirao"
PIN = "417024ec25c678cad276dde648179caaed985648"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    root, wheel, wheel_sha = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    regenerated, out = Path(sys.argv[4]), Path(sys.argv[5])
    mission = root / M
    checks = []

    def check(name, ok, **detail):
        checks.append({"check": name, "ok": bool(ok), **detail})

    new = json.loads((mission / "FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))
    c2_path = mission / "FROZEN_PARAMETERS_cycle2_1c9e11bd702b.json"
    c2_raw = c2_path.read_bytes()
    c2 = json.loads(c2_raw)
    pinned_raw = subprocess.run(["git", "-C", str(root), "show", f"{PIN}:{M}/FROZEN_PARAMETERS.json"],
                                capture_output=True, check=True).stdout
    pinned = json.loads(pinned_raw)
    check("cycle-2 file preserved byte for byte (== FROZEN_PARAMETERS.json at 417024e)", c2_raw == pinned_raw,
          sha256=sha(c2_raw))
    bc = new["decision_policy"]["brasileirao_config"]
    check("brasileirao_config unchanged (cycle 3 == 417024e)", bc == pinned["decision_policy"]["brasileirao_config"])
    changed = sorted({k for k in set(new) | set(c2) if new.get(k) != c2.get(k)})
    dp_changed = sorted({k for k in set(new["decision_policy"]) | set(c2["decision_policy"])
                         if new["decision_policy"].get(k) != c2["decision_policy"].get(k)})
    vectors_sha = sha((mission / "FROZEN_VECTORS.json").read_bytes())
    protected_new = {e["path"]: e["sha256"] for e in new["protected_set_initial"]["mission"]}
    protected_old = {e["path"]: e["sha256"] for e in c2["protected_set_initial"]["mission"]}
    protected_diff = sorted(p for p in set(protected_new) | set(protected_old)
                            if protected_new.get(p) != protected_old.get(p))
    rest_new = {k: v for k, v in new["protected_set_initial"].items() if k != "mission"}
    rest_old = {k: v for k, v in c2["protected_set_initial"].items() if k != "mission"}
    check("FROZEN_PARAMETERS: only decision_policy (framework, rule_order), cycle and the pointers to the new "
          "FROZEN_VECTORS changed",
          changed == ["cycle", "decision_policy", "frozen_vectors", "protected_set_initial"]
          and dp_changed == ["framework", "rule_order"]
          and {k: v for k, v in new["frozen_vectors"].items() if k != "sha256"}
          == {k: v for k, v in c2["frozen_vectors"].items() if k != "sha256"}
          and new["frozen_vectors"]["sha256"] == vectors_sha
          and protected_diff == [f"{M}/FROZEN_VECTORS.json"] and protected_new[f"{M}/FROZEN_VECTORS.json"] == vectors_sha
          and rest_new == rest_old,
          top=changed, decision_policy=dp_changed, protected_changed=protected_diff)
    ids_new = [r.split()[0] for r in new["decision_policy"]["rule_order"]]
    ids_old = [r.split()[0] for r in c2["decision_policy"]["rule_order"]]
    expected = ids_old[:ids_old.index("R12")] + ["R17"] + ids_old[ids_old.index("R12"):]
    check("rule_order = cycle 2 + R17 between R11 and R12", ids_new == expected, rule_ids=ids_new)
    v_new = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    v_old = json.loads((mission / "FROZEN_VECTORS_cycle2_bb210f62a840.json").read_text(encoding="utf-8"))
    files_changed = sorted(k for k in set(v_new["files"]) | set(v_old["files"])
                           if v_new["files"].get(k) != v_old["files"].get(k))
    allowed = sorted([
        "fixtures/proposals/n1/01-next.json", "fixtures/proposals/n1/24-equivalent-request.json",
        "fixtures/proposals/contradiction/02-refuted.json",
        "fixtures/v2/brasileirao/contradiction-refuted-task.json",
        "fixtures/v2/brasileirao/contradiction-refuted-result.json",
        "fixtures/v2/brasileirao/contradiction-refuted-again-task.json"])
    check("FROZEN_VECTORS: only the declared vector files changed or were added", files_changed == allowed,
          changed=files_changed)
    sections = sorted(k for k in set(v_new) | set(v_old) if k not in ("files", "cycle") and v_new.get(k) != v_old.get(k))
    # the contradiction plan lists paths (its changed bytes are in `files`); the N+1 plan gains a candidate
    check("FROZEN_VECTORS: only the n_plus_1 (and contradiction) sections changed; e2e, holdout, soak unchanged",
          "n_plus_1" in sections and set(sections) <= {"contradiction", "n_plus_1"}, sections=sections)
    added = [c for c in v_new["n_plus_1"]["candidates"] if c not in v_old["n_plus_1"]["candidates"]]
    check("N+1: 01-next changed to another experiment and 24-equivalent-request expects DUPLICATE EQUIVALENT_REQUEST",
          added == [{"proposal": "fixtures/proposals/n1/24-equivalent-request.json", "expected_decision": "DUPLICATE",
                     "expected_reason": "EQUIVALENT_REQUEST"}]
          and len(v_new["n_plus_1"]["candidates"]) == len(v_old["n_plus_1"]["candidates"]) + 1, added=added)
    bad = [rel for rel, e in v_new["files"].items()
           if sha((mission / rel).resolve().read_bytes()) != e["sha256"]]
    check("every vector file matches its manifest sha256", not bad, mismatched=bad, files=len(v_new["files"]))
    raw_wheel = wheel.read_bytes()
    check("cain wheel sha256 == published release asset", sha(raw_wheel) == wheel_sha, sha256=sha(raw_wheel))
    with zipfile.ZipFile(wheel) as z:
        wheel_config = z.read("cain/orchestration/data/brasileirao.json")
    config = json.loads(wheel_config)
    fp = config["frozen_parameters"]
    check("brasileirao.json in the wheel pins FROZEN_PARAMETERS at 417024e with the cycle-2 file sha256",
          fp["commit"] == PIN and fp["sha256"] == sha(c2_raw) and fp["path"] == f"{M}/FROZEN_PARAMETERS.json",
          frozen_parameters=fp)
    check("brasileirao.json in the wheel == regenerated by tools/build_domain_config.py of the release commit from "
          "417024e (bytes)", wheel_config == regenerated.read_bytes(),
          wheel_sha256=sha(wheel_config), regenerated_sha256=sha(regenerated.read_bytes()))
    check("sealed_scopes in the wheel (R16 holdout)", len(config.get("sealed_scopes", [])) == 3)
    check("proposable_request_types: every proposable hypothesis -> the single allowed type",
          config.get("proposable_request_types") == {h: bc["allowed_request_types"][0]
                                                     for h in bc["proposable_hypotheses"]})
    doc = {"schema": "integration-brasileirao/CYCLE3_CHECK/1", "checks": checks,
           "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("passed", "failed")}))
    for c in checks:
        if not c["ok"]:
            print("FAILED", json.dumps(c, ensure_ascii=False))
    return 0 if doc["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
