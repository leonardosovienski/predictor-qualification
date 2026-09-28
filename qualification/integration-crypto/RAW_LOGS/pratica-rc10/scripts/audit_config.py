"""Auditoria da configuração do CAIN para o cripto (crypto.json da wheel rc10) contra as fontes pinadas."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
P = Path(sys.argv[1]); W = P / "rt"
QUAL = "/home/superleo13/predictors/work/integration-crypto-predictor-qualification"
cfg_path = next((W / "cain-venv/lib").glob("python3.*/site-packages/cain/orchestration/data/crypto.json"))
cfg = json.loads(cfg_path.read_text())
B = cfg["source"]["commit"]
def show(repo, commit, path):
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, check=True).stdout
state = json.loads(show(W / "cripto-src", B, "charters/scientific_state.json"))
costs_src = show(W / "cripto-src", B, "GarimpoInvestimentos/v3/costs.py").decode()
fee = float(re.search(r"taker_fee_bps: float = ([0-9.]+)", costs_src).group(1))
slip = float(re.search(r"slippage_bps: float = ([0-9.]+)", costs_src).group(1))
contract_raw = show(QUAL, cfg["contract"]["commit"], cfg["contract"]["path"])
contract = json.loads(contract_raw)
op = json.loads((W / "op/policy.json").read_text())
registry = {f"{r['name']} {r['version']}" for r in op["registry"]}
reg_by_kind = {}
for r in op["registry"]:
    reg_by_kind.setdefault(r["kind"], set()).add(f"{r['name']} {r['version']}")
checks = []
def check(name, ok, **detail):
    checks.append({"check": name, "ok": bool(ok), **detail})
check("hipóteses fechadas = estado científico em 341d270 (H1..H9, com o estado de cada uma)",
      cfg["closed_hypotheses"] == {f"crypto:{h}": s for h, s in state["hypotheses"].items()})
check("família congelada = frozen_families do estado", cfg["frozen_families"] == state["frozen_families"])
check("custos = padrões de v3/costs.py (taxa e slippage por perna)",
      cfg["costs"] == {"fee_bps": fee, "slippage_bps": slip}, config=cfg["costs"], source={"fee": fee, "slip": slip})
for f in cfg["source"]["files"]:
    check(f"fonte {f['path']}: sha256 igual ao git show no commit pinado",
          hashlib.sha256(show(W / "cripto-src", B, f["path"])).hexdigest() == f["sha256"])
check("contrato: sha256 igual ao do predictor-qualification no commit registrado",
      hashlib.sha256(contract_raw).hexdigest() == cfg["contract"]["sha256"])
allow = contract.get("handler_allowlist") or contract.get("request", {}).get("handler_allowlist") or {}
check("tipos de pedido = chaves da handler_allowlist do contrato", sorted(cfg["allowed_request_types"]) == sorted(allow),
      contract=sorted(allow))
check("tipos de pedido = handlers da admissão do domínio", sorted(cfg["allowed_request_types"]) == sorted(op["handlers"]))
check("símbolos = allowed_symbols da admissão do domínio", cfg["allowed_symbols"] == op["allowed_symbols"])
not_admitted = sorted(set(cfg["proposable_hypotheses"]) - set(op["hypotheses"]))
check("toda hipótese propunhável do CAIN é admitida pelo domínio", not not_admitted, not_admitted=not_admitted,
      admitted=sorted(op["hypotheses"]))
missing_refs = sorted(f"{k}: {v}" for k, vs in cfg["allowed_references"].items() for v in vs
                      if v not in reg_by_kind.get(k, set()))
check("toda referência permitida no CAIN existe no registro do domínio", not missing_refs, missing=missing_refs)
check("capital: o estado científico não autoriza capital nem alavancagem",
      state["capital_authorized"] is False and state["leverage_authorized"] is False)
frozen_main = json.loads(show(QUAL, "origin/main", "qualification/integration-crypto/FROZEN_PARAMETERS.json"))
check("proveniência: o crypto.json aponta para o FROZEN_PARAMETERS vigente no main",
      hashlib.sha256(show(QUAL, "origin/main", "qualification/integration-crypto/FROZEN_PARAMETERS.json")).hexdigest()
      == cfg["frozen_parameters"]["sha256"],
      config_points_to=cfg["frozen_parameters"]["sha256"][:12],
      main_cycle=frozen_main.get("cycle", {}).get("number", 1))
out = {"config": str(cfg_path), "source_commit": B, "passed": sum(c["ok"] for c in checks),
       "failed": sum(not c["ok"] for c in checks), "checks": checks}
(P / "out/A1").mkdir(parents=True, exist_ok=True)
(P / "out/A1/audit_config.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for c in checks:
    print("OK  " if c["ok"] else "FALHA", c["check"], {k: v for k, v in c.items() if k not in ("check", "ok")} or "")
print(out["passed"], "OK /", out["failed"], "falhas")
