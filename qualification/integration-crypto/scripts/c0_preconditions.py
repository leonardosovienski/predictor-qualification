"""integration-crypto C0: pré-condições lidas de um snapshot `git archive` do predictor-qualification.

Uso: c0_preconditions.py <snapshot> <dir de wheels> <commit da tag v1.2.0rc2> <commit da tag do protocolo V2>

Imprime uma linha `CHECK <id> OK|FALHA <detalhe>` por item e `RESUMO` no fim. Baixa as wheels por URL
(release do GitHub) e confere o sha256 dos bytes baixados; também lê o digest do asset pela API de releases (gh).
"""

import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

SNAP = Path(sys.argv[1])
WHEELS = Path(sys.argv[2])
TAG_COMMIT = sys.argv[3]
PROTO_TAG_COMMIT = sys.argv[4]

BASE = "341d270e4d709150c581c3cd93f4518d483009eb"
VERSION = "1.2.0rc2"
WHEEL_SHA = "6e62f67f0779aef7e913d34b4d3d3d6ed5f88ad882e8fa8372f54c4ab59bc8ee"

results = []


def check(cid, ok, detail):
    results.append((cid, bool(ok)))
    print(f"CHECK {cid} {'OK' if ok else 'FALHA'} {detail}")


def load(rel):
    return json.loads((SNAP / rel).read_text(encoding="utf-8"))


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def download(url):
    dest = WHEELS / url.rsplit("/", 1)[1]
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())
    return dest


def asset_digest(repo, tag, name):
    out = subprocess.run(
        ["gh", "release", "view", tag, "-R", repo, "--json", "assets,isPrerelease"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return None, None
    data = json.loads(out.stdout)
    for a in data["assets"]:
        if a["name"] == name:
            return (a.get("digest") or "").removeprefix("sha256:"), data["isPrerelease"]
    return None, data["isPrerelease"]


# 4.2 decisões
dec = {d["decision_id"]: d for d in load("qualification/DECISIONS.json")["decisions"]}
for did in ("D-16", "D-22"):
    check(f"4.2/{did}", dec.get(did, {}).get("status") == "APPROVED", dec.get(did, {}).get("status"))
print(f"INFO 4.2/D-23 presente={'D-23' in dec}")

# 4.4 artefatos compartilhados
for rel in ("qualification/shared/ENVELOPE_V2_FREEZE.json", "qualification/shared/STACK_BASELINE_V2.0.json"):
    p = SNAP / rel
    check(f"4.4/{p.name}", p.is_file(), sha_file(p) if p.is_file() else "ausente")

# 4.5 C0.3
check("4.5/C0.3-DECISIONS", (SNAP / "qualification/DECISIONS.json").is_file(), "no ref")
hyg = load("qualification/HYGIENE.json")["items"]
not_done = [i.get("id") or i.get("hygiene_id") for i in hyg if i.get("status") != "DONE"]
check("4.5/C0.3-HYGIENE", not not_done, f"{len(hyg) - len(not_done)}/{len(hyg)} DONE; pendentes={not_done}")
check("4.5/C0.3-baseline-comum", (SNAP / "qualification/shared/STACK_BASELINE_V1.json").is_file(), "STACK_BASELINE_V1.json")

# 4.5 §1 do prompt comum: attestations e contratos da Etapa A
for d in ("crypto", "brasileirao", "stocks"):
    a = load(f"qualification/{d}/QUALIFICATION_ATTESTATION.json")
    check(f"4.5/etapaA-{d}", a.get("result") == "QUALIFIED" and a.get("stage") == "A",
          f"result={a.get('result')} sha256={sha_file(SNAP / f'qualification/{d}/QUALIFICATION_ATTESTATION.json')}")
    cp = SNAP / f"qualification/{d}/DOMAIN_RESEARCH_CONTRACT.json"
    c = json.loads(cp.read_text(encoding="utf-8"))
    check(f"4.5/contrato-{d}", c.get("domain_prefix") == d, f"prefixo={c.get('domain_prefix')} sha256={sha_file(cp)}")

# 4.5 §1: SHARED_ISSUES para as wheels usadas pela pilha do cripto
rt = load("qualification/crypto/runtime_target.json")
used = {rt["wheel_sha256"]} | {v["sha256"] for v in rt["stack"].values()}
issues = load("qualification/shared/SHARED_ISSUES.json")["issues"]
blocking = []
for i in issues:
    vp = SNAP / f"qualification/shared/{i['issue_id']}/SHARED_DEPENDENCY_VERDICT.json"
    verdict = json.loads(vp.read_text(encoding="utf-8")) if vp.is_file() else {}
    affects = i["wheel_sha256"] in used
    blk = verdict.get("blocking", True) if verdict else True
    print(f"INFO 4.5/{i['issue_id']} dep={i['dependency']} wheel={i['wheel_sha256'][:12]} status={i['status']} "
          f"classificacao={verdict.get('classification')} blocking={blk} afeta_wheel_usada={affects}")
    if affects and blk:
        blocking.append(i["issue_id"])
check("4.5/SHARED_ISSUES-wheels-usadas", not blocking, f"bloqueantes={blocking} wheels_usadas={sorted(w[:12] for w in used)}")

# 4.5 §1 do prompt da missão: nenhuma integração anterior
qdir = SNAP / "qualification"
prior = sorted(p.relative_to(SNAP).as_posix() for p in qdir.glob("integration*/QUALIFICATION_ATTESTATION*.json"))
partials = sorted(p.relative_to(SNAP).as_posix() for p in qdir.glob("integration*/ATTESTATION_PARTIAL_*.json"))
print(f"INFO 4.5/diretorios-integration {sorted(p.name for p in qdir.glob('integration*'))}")
check("4.5/missao-sem-integracao-anterior", not prior and not partials and not (qdir / "integration-crypto").exists(),
      f"attestations={prior} parciais={partials} integration-crypto_existe={(qdir / 'integration-crypto').exists()}")

# 4.6 base do cripto
check("4.6a/runtime_target", rt["commit"] == BASE and rt["version"] == VERSION and rt["wheel_sha256"] == WHEEL_SHA,
      f"commit={rt['commit']} version={rt['version']} wheel={rt['wheel_sha256']}")
bl = load("qualification/shared/STACK_BASELINE_V2.0.json")
crow = next(r for r in bl["repos"] if r["repo"] == "cripto-predictor")
fw = [w for w in bl["final_wheel_verification"] if w["package"] == "cripto-predictor"]
check("4.6b/STACK_BASELINE_V2.0", crow["base"]["commit"] == BASE and len(fw) == 1
      and fw[0]["declared_sha256"] == WHEEL_SHA and fw[0]["version"] == VERSION,
      f"base={crow['base']['commit']} wheel={[w['declared_sha256'] for w in fw]} versao={[w['version'] for w in fw]}")
wheel = download(rt["wheel_url"])
got = sha_file(wheel)
dig, pre = asset_digest("leonardosovienski/cripto-predictor", "v1.2.0rc2", wheel.name)
check("4.6c/asset-wheel", got == WHEEL_SHA and dig == WHEEL_SHA and TAG_COMMIT == BASE,
      f"baixado={got} digest_api={dig} prerelease={pre} tag={TAG_COMMIT}")

# 4.7 protocolo V2 congelado
fr = load("qualification/shared/ENVELOPE_V2_FREEZE.json")
pw = fr["protocol"]["wheel"]
pwheel = download(pw["url"])
pgot = sha_file(pwheel)
pdig, ppre = asset_digest("leonardosovienski/ecosystem-predictor", fr["protocol"]["tag"], pw["name"])
check("4.7/protocolo-V2", pgot == pw["sha256"] and pdig == pw["sha256"] and PROTO_TAG_COMMIT == fr["protocol"]["tag_commit"],
      f"versao={fr['protocol']['version']} url={pw['url']} baixado={pgot} esperado={pw['sha256']} digest_api={pdig} "
      f"prerelease={ppre} tag_commit={PROTO_TAG_COMMIT}")
check("4.7/freeze-aponta-baseline", fr["stack_baseline"]["sha256"] == sha_file(SNAP / fr["stack_baseline"]["path"]),
      f"{fr['stack_baseline']['sha256']}")
cc = next(c for c in fr["domain_contracts"] if c["domain"] == "crypto")
check("4.7/freeze-contrato-crypto", cc["sha256"] == sha_file(SNAP / cc["path"]), cc["sha256"])

fails = [c for c, ok in results if not ok]
print(f"RESUMO checks={len(results)} ok={len(results) - len(fails)} falhas={fails}")
sys.exit(1 if fails else 0)
