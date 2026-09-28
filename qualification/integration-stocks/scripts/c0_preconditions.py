"""integration-stocks, C0: pré-voo 4.2 e 4.4–4.7 (e os fatos da decisão 5.1 que atingem o pré-voo).

Chamado por c0_preflight.sh. Só leitura. Imprime uma linha por verificação,
`CHECK <id> <OK|FALHA> <detalhe>`, linhas `OBS <id> <detalhe>` (fato registrado, não é verificação)
e no fim `c0_falhas <n>`.

Uso: python c0_preconditions.py <snapshot do predictor-qualification> <clone do stocks-predictor> <dir dos downloads>
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
stocks = Path(sys.argv[2])
downloads = Path(sys.argv[3])
failures = 0

BASE = "61fc017256ffea815ae96bbe02b847dccdb395cc"
PR96_MERGE = "36081a66004a464d5e9c5ea4bc6e208d0fcb582e"
TREE = "bea6dce6adea5cc2c0d917b5e2265507ec64708d"
WHEEL_SHA = "92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8"
VERSION = "0.3.0rc2"
TAG = "v0.3.0rc2"
STOCKS_REMOTE = "https://github.com/leonardosovienski/stocks-predictor.git"
ECOSYSTEM_REMOTE = "https://github.com/leonardosovienski/ecosystem-predictor.git"


def check(item: str, ok: bool, detail: str) -> None:
    global failures
    failures += not ok
    print(f"CHECK {item} {'OK' if ok else 'FALHA'} {detail}")


def obs(item: str, detail: str) -> None:
    print(f"OBS {item} {detail}")


def load(rel: str):
    path = root / rel
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def run(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def git(*args: str) -> tuple[int, str]:
    return run("git", "-C", str(stocks), *args)


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def ls_remote_peeled(remote: str, tag: str) -> str | None:
    _, out = run("git", "ls-remote", remote, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}")
    refs = dict(reversed(line.split("\t")) for line in out.splitlines() if "\t" in line)
    return refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")


def api_digest(repo: str, tag: str, asset: str) -> str:
    _, out = run("gh", "api", f"repos/{repo}/releases/tags/{tag}", "--jq",
                 f'.assets[] | select(.name=="{asset}") | .digest')
    return out


# ---------------------------------------------------------------- 4.2 decisões
decisions = {d["decision_id"]: d["status"] for d in load("qualification/DECISIONS.json")["decisions"]}
for did in ("D-22", "D-16", "D-21"):
    check(f"4.2/{did}", decisions.get(did) == "APPROVED", f"status={decisions.get(did)}")
obs("4.2/ultima-decisao", f"{list(decisions)[-1]} (próxima livre: D-{max(int(d[2:]) for d in decisions) + 1})")

# ---------------------------------------------------------------- 4.4 artefatos compartilhados
for rel in ("qualification/shared/ENVELOPE_V2_FREEZE.json", "qualification/shared/STACK_BASELINE_V2.0.json"):
    path = root / rel
    check(f"4.4/{path.name}", path.is_file(), f"{rel} sha256={sha256_file(path)}")

# ---------------------------------------------------------------- 4.5 C0.3
check("4.5/C0.3-DECISIONS", (root / "qualification/DECISIONS.json").is_file(), "qualification/DECISIONS.json")
hygiene = load("qualification/HYGIENE.json")
check("4.5/C0.3-HYGIENE-presente", hygiene is not None, "qualification/HYGIENE.json")
items = (hygiene["items"] if isinstance(hygiene, dict) else hygiene) or []
pending = [i.get("id") for i in items if i.get("status") != "DONE"]
check("4.5/C0.3-HYGIENE-DONE", bool(items) and not pending, f"itens={len(items)} fora_de_DONE={pending}")
check("4.5/C0.3-baseline-comum", (root / "qualification/shared/STACK_BASELINE_V1.json").is_file(),
      "qualification/shared/STACK_BASELINE_V1.json")

# ---------------------------------------------------------------- 4.5 §1 do prompt comum
for branch in ("crypto", "brasileirao", "stocks"):
    att = load(f"qualification/{branch}/QUALIFICATION_ATTESTATION.json")
    check(f"4.5/comum1-etapaA-{branch}", bool(att) and att.get("result") == "QUALIFIED",
          f"result={att.get('result') if att else 'ausente'}")
    rel = f"qualification/{branch}/DOMAIN_RESEARCH_CONTRACT.json"
    check(f"4.5/comum1-contrato-{branch}", (root / rel).is_file(), f"{rel} sha256={sha256_file(root / rel)}")

# wheels do stack que esta missão usa: Etapa A do Stocks + cain/ecosystem da integration-crypto
FRAMEWORK_REPOS = ("leonardosovienski/cain/", "leonardosovienski/ecosystem-predictor/")
stocks_att = load("qualification/stocks/QUALIFICATION_ATTESTATION.json") or {}
ic_att = load("qualification/integration-crypto/QUALIFICATION_ATTESTATION.json")
framework_wheels = [w for w in (ic_att or {}).get("final_wheels", []) if any(r in w["url"] for r in FRAMEWORK_REPOS)]
used = {w["sha256"]: f"{w['name']} {w['version']}" for w in stocks_att.get("final_wheels", []) + framework_wheels}
for issue in load("qualification/shared/SHARED_ISSUES.json")["issues"]:
    verdict = issue.get("verdict") or {}
    resolution = issue.get("resolution") or {}
    wheel = issue.get("wheel_sha256", "")
    resolved_for_used = bool(resolution) and resolution.get("wheel_sha256") in used
    affects = wheel in used
    ok = verdict.get("blocking") is False or not affects or resolved_for_used
    check(f"4.5/comum1-{issue['issue_id']}", ok,
          f"status={issue.get('status')} classification={verdict.get('classification')} blocking={verdict.get('blocking')} "
          f"wheel={wheel[:8]} usada_pela_missao={affects} resolucao={resolution.get('wheel_version')}"
          f"({str(resolution.get('wheel_sha256', ''))[:8]}) wheels_da_missao={sorted(v for v in used.values())}")

# ---------------------------------------------------------------- 4.5 §1 do prompt da missão
ic_dir = root / "qualification/integration-crypto"
check("4.5/missao1-integration-crypto-QUALIFIED", bool(ic_att) and ic_att.get("result") == "QUALIFIED",
      f"result={ic_att.get('result')}" if ic_att else
      f"qualification/integration-crypto/QUALIFICATION_ATTESTATION.json ausente (diretório existe: {ic_dir.is_dir()})")

fc = {c["repo"]: c["commit_sha"] for c in (ic_att or {}).get("final_commits", [])}
fw = {w["name"]: w for w in (ic_att or {}).get("final_wheels", [])}
for repo, pkg in (("cain", "cain-research"), ("ecosystem-predictor", None)):
    check(f"4.5/reuso-final_commit-{repo}", repo in fc,
          f"final_commits[{repo}]={fc.get(repo)}" if ic_att else "não verificável: attestation da integration-crypto ausente")
check("4.5/reuso-final_wheels-cain-ecosystem", bool(ic_att) and any("/cain/" in w["url"] for w in framework_wheels)
      and any("/ecosystem-predictor/" in w["url"] for w in framework_wheels),
      f"final_wheels={[w['name'] + ' ' + w['version'] for w in framework_wheels]}" if ic_att
      else "não verificável: attestation da integration-crypto ausente")
for w in framework_wheels:
    dl = downloads / w["url"].rsplit("/", 1)[1]
    dl.unlink(missing_ok=True)
    run("curl", "-fsSL", "--retry", "3", "-o", str(dl), w["url"])
    got = sha256_file(dl)
    check(f"4.5/reuso-wheel-{w['name']}", got == w["sha256"],
          f"{w['version']} url={w['url']} declarado={w['sha256']} download={got}")
rel = "qualification/integration-crypto/DECISION_POLICY_REPORT.md"
check("4.5/reuso-DECISION_POLICY_REPORT", (root / rel).is_file(), f"{rel} {'presente' if (root / rel).is_file() else 'ausente'}")

# ---------------------------------------------------------------- 4.6 base do Stocks
rt = load("qualification/stocks/runtime_target.json")
bt = load("qualification/stocks/build_target.json")
check("4.6a/runtime_target-commit", rt["commit"] == BASE, f"commit={rt['commit']}")
check("4.6a/runtime_target-wheel", rt["wheel_sha256"] == WHEEL_SHA, f"wheel_sha256={rt['wheel_sha256']} url={rt['wheel_url']}")
check("4.6a/build_target-versao", bt.get("version") == VERSION, f"version={bt.get('version')} commit={bt.get('commit')}")
att_fc = {c["repo"]: c["commit_sha"] for c in stocks_att.get("final_commits", [])}
att_fw = {w["name"]: w for w in stocks_att.get("final_wheels", [])}
sw = att_fw.get("stocks-predictor", {})
check("4.6a/attestation-final_commit", att_fc.get("stocks-predictor") == BASE, f"final_commits[stocks-predictor]={att_fc.get('stocks-predictor')}")
check("4.6a/attestation-final_wheel", sw.get("sha256") == WHEEL_SHA and sw.get("version") == VERSION,
      f"final_wheels[stocks-predictor]={sw.get('version')} {sw.get('sha256')}")

bl = load("qualification/shared/STACK_BASELINE_V2.0.json")
entry = next(r for r in bl["repos"] if r["repo"] == "stocks-predictor")
pub = next((w for w in entry.get("published_wheels", []) if w.get("tag") == TAG), {})
fwv = next((w for w in bl.get("final_wheel_verification", []) if w.get("package") == "stocks-predictor"), {})
check("4.6b/baseline-base-commit", entry["base"]["commit"] == BASE, f"base.commit={entry['base']['commit']}")
check("4.6b/baseline-wheel", pub.get("tag_commit") == BASE and pub.get("sha256") == WHEEL_SHA
      and fwv.get("declared_sha256") == WHEEL_SHA and fwv.get("release_asset_sha256") == WHEEL_SHA
      and fwv.get("version") == VERSION,
      f"published_wheels[{TAG}]=({pub.get('tag_commit')}, {pub.get('sha256')}) "
      f"final_wheel_verification=({fwv.get('version')}, {fwv.get('declared_sha256')}, {fwv.get('release_asset_sha256')})")

_, local_tag = git("rev-parse", f"{TAG}^{{commit}}")
remote_tag = ls_remote_peeled(STOCKS_REMOTE, TAG)
check("4.6c/tag-commit", local_tag == BASE and remote_tag == BASE, f"local={local_tag} ls-remote={remote_tag}")
dl_sha = sha256_file(downloads / "stocks_predictor-0.3.0rc2-py3-none-any.whl")
digest = api_digest("leonardosovienski/stocks-predictor", TAG, "stocks_predictor-0.3.0rc2-py3-none-any.whl")
check("4.6c/asset-sha256", dl_sha == WHEEL_SHA and digest == f"sha256:{WHEEL_SHA}",
      f"download={dl_sha} api_digest={digest}")

rc, _ = git("merge-base", "--is-ancestor", BASE, "origin/main")
_, main_sha = git("rev-parse", "origin/main")
check("4.6d/base-ancestral-do-main", rc == 0, f"is-ancestor exit={rc} origin/main={main_sha}")
_, t_base = git("rev-parse", f"{BASE}^{{tree}}")
_, t_pr96 = git("rev-parse", f"{PR96_MERGE}^{{tree}}")
check("4.6d/arvores", t_base == TREE and t_pr96 == TREE, f"{BASE[:7]}^{{tree}}={t_base} {PR96_MERGE[:7]}^{{tree}}={t_pr96}")

# ---------------------------------------------------------------- 5.1 fatos da divergência base × main
rc96, _ = git("merge-base", "--is-ancestor", PR96_MERGE, "origin/main")
obs("5.1/pr96-merge-ancestral-do-main", f"exit={rc96}")
_, count = git("rev-list", "--count", f"{BASE}..origin/main")
_, count96 = git("rev-list", "--count", f"{PR96_MERGE}..origin/main")
obs("5.1/commits-alem-da-base", f"{BASE[:7]}..origin/main={count} {PR96_MERGE[:7]}..origin/main={count96}")
_, merges = git("log", "--merges", "--format=%s", f"{PR96_MERGE}..origin/main")
prs = sorted({int(n) for n in re.findall(r"#(\d+)", merges)})
obs("5.1/prs-apos-pr96", f"{prs}")
_, files = git("diff", "--name-only", BASE, "origin/main")
files = files.splitlines()
adapters = [f for f in files if f.startswith("stocks_predictor/adapters/")]
check("5.1/adapters-intocados-no-main", not adapters, f"arquivos_em_stocks_predictor/adapters/={adapters}")
tops = sorted({f.split("/")[0] + ("/" if "/" in f else "") for f in files})
v2 = sorted({f for f in files if f.startswith("stocks_predictor/")})
obs("5.1/arquivos-alterados", f"total={len(files)} topo={tops}")
obs("5.1/pacote-alterado", f"{v2}")
obs("5.1/pyproject-uvlock-alterados", f"{[f for f in files if f in ('pyproject.toml', 'uv.lock')]}")
_, pyproject_main = git("show", "origin/main:pyproject.toml")
m = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_main, re.M)
obs("5.1/versao-no-main", f"{m.group(1) if m else None}")
rc_ss, _ = git("cat-file", "-e", f"{BASE}:research/scientific_state.json")
obs("5.1/scientific_state-na-base", f"existe={rc_ss == 0}")
_, adapters_base = git("ls-tree", "-r", "--name-only", BASE, "stocks_predictor/adapters/")
obs("5.1/adapters-na-base", f"{adapters_base.splitlines()}")

# ---------------------------------------------------------------- contrato do Stocks (§2 do prompt da missão)
contract = load("qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json")
check("4.5/missao2-contrato-prefixo", contract["domain_prefix"] == "stocks", f"domain_prefix={contract['domain_prefix']}")
check("4.5/missao2-contrato-adapter_paths", contract["adapter_paths"] == ["stocks_predictor/adapters/"],
      f"adapter_paths={contract['adapter_paths']}")
obs("4.5/missao2-contrato-adapter_entrypoints", json.dumps(contract.get("adapter_entrypoints"), ensure_ascii=False))

# ---------------------------------------------------------------- 4.7 protocolo V2 congelado
freeze = load("qualification/shared/ENVELOPE_V2_FREEZE.json")["protocol"]
w = freeze["wheel"]
proto_tag = ls_remote_peeled(ECOSYSTEM_REMOTE, freeze["tag"])
check("4.7/protocolo-tag", proto_tag == freeze["tag_commit"] == freeze["commit"],
      f"tag={freeze['tag']} ls-remote={proto_tag} freeze.tag_commit={freeze['tag_commit']}")
dl_proto = sha256_file(downloads / w["name"])
digest = api_digest(freeze["repo"], freeze["tag"], w["name"])
check("4.7/protocolo-wheel-sha256", dl_proto == w["sha256"] and digest == f"sha256:{w['sha256']}",
      f"{freeze['package']} {freeze['version']} freeze={w['sha256']} download={dl_proto} api_digest={digest}")

print(f"c0_falhas {failures}")
