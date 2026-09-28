"""integration-stocks, ciclo 2: estados dos achados que o ciclo 2 fecha com evidência (C6).

A attestation do ciclo 1 fixava as wheels v0.3.0rc3 (stocks) e v0.4.13rc7 (cain), onde IS-F002 e IS-F003 eram
verdadeiros; por isso o FINDINGS.json da reemissão 1 os manteve abertos (o arquivo é evidência dela). O ciclo 2 roda
na cain 0.4.13rc12, e cada status abaixo sai de um arquivo de RAW_LOGS conferido aqui (nada é afirmado sem a checagem):
  * IS-F001 → FIXED: o main do stocks-predictor declara 0.3.0rc4 e não existe release v0.3.0rc4 (stocks-predictor#108,
    mergeado pelo dono); a wheel qualificada continua v0.3.0rc3 = 6f857b2;
  * IS-F002 → FIXED: cain#62 (d8b8061) na release; no N+1 do run, 17-collection é ALLOW;
  * IS-F003 → FIXED: cain#62; no soak do run, as propostas de LLM passam pela política sem SCHEMA_INVALID e sem
    placebo_seed;
  * IS-F007 → FIXED: o main do cain declara a versão da última pré-release publicada e é o commit dela (cain#61 e os
    bumps da release única, mergeados pelo dono).
Idempotente: só muda achados ainda abertos. Falha fechado se a evidência não confirmar.
Uso: python cycle2_findings.py <raiz do predictor-qualification> <run do runtime do ciclo 2>
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT, RUN = Path(sys.argv[1]), sys.argv[2]
M = ROOT / "qualification/integration-stocks"
R = M / "RAW_LOGS/runtime" / RUN


def ref(path: Path) -> dict:
    return {"file": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main() -> int:
    versions = M / "RAW_LOGS/findings-c2/versions.log"
    text = versions.read_text(encoding="utf-8")
    stocks_ok = ('version = "0.3.0rc4"' in text and "stocks-predictor release v0.3.0rc4: release not found" in text
                 and "tag v0.3.0rc3 -> 6f857b232eaa63f3fccda6a16f92dbfc8983ab3b" in text)
    cain_main = re.search(r"^cain origin/main (\w+) version = \"([^\"]+)\"", text, re.M)
    cain_tag = re.search(rf"^cain tag v{re.escape(cain_main.group(2))} -> (\w+)", text, re.M) if cain_main else None
    cain_ok = bool(cain_main and cain_tag and cain_tag.group(1) == cain_main.group(1))
    n1 = json.loads((R / "n-plus-1/frozen/SUMMARY.json").read_text(encoding="utf-8"))
    collection = next(r for r in n1["receipts"] if r["candidate"] == "17-collection")
    f002_ok = collection["decision"] == "ALLOW" and n1["failed"] == 0
    soak = json.loads((R / "soak/SUMMARY.json").read_text(encoding="utf-8"))
    llm = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((R / "soak").glob("llm-*.json"))
           if not p.name.endswith(".audit.json")]
    log = (R / "soak/commands.log").read_text(encoding="utf-8")
    decided = [json.loads(out) for out in re.findall(r'"label": "propose llm \d+".*\n--- stdout\n(\{.*\})\n--- stderr', log)]
    f003_ok = (bool(llm) and all("placebo_seed" not in p["request"]["parameters"] for p in llm)
               and bool(decided) and all(d.get("reason_code") != "SCHEMA_INVALID" for d in decided)
               and soak["failed"] == 0)
    checks = {"IS-F001": stocks_ok, "IS-F002": f002_ok, "IS-F003": f003_ok, "IS-F007": cain_ok}
    if not all(checks.values()):
        raise SystemExit(f"evidência não confirma: {checks}")
    fixes = {
        "IS-F001": ("stocks-predictor#108 (7ea3657), mergeado pelo dono: o main declara 0.3.0rc4 (não publicada) e a "
                    "wheel qualificada continua v0.3.0rc3 = 6f857b2; não há mais duas árvores com a mesma versão",
                    [versions]),
        "IS-F002": ("cain#62 (d8b8061), na release única (rc10 em diante; o ciclo 2 roda na rc12): a R06 compara custos só "
                    "quando a variante do request_schema os declara; no N+1 do ciclo 2, 17-collection é "
                    f"{collection['decision']} ({collection['rule']})", [R / "n-plus-1/frozen/SUMMARY.json"]),
        "IS-F003": ("cain#62 (d8b8061): a semente placebo só entra onde a variante do contrato a declara; no soak do "
                    f"ciclo 2, {len(llm)} propostas de LLM sem placebo_seed, decididas pela política "
                    f"({', '.join(sorted({d.get('decision', '?') for d in decided}))})",
                    [R / "soak/SUMMARY.json", R / "soak/commands.log"]),
        "IS-F007": (f"cain#61 (versão rc8 não publicada) e os bumps da release única, mergeados pelo dono; o main "
                    f"({cain_main.group(1)[:7]}) declara {cain_main.group(2)} e é o commit da tag v{cain_main.group(2)}",
                    [versions]),
    }
    path = M / "FINDINGS.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    changed = []
    for finding in doc["findings"]:
        if finding["id"] in fixes and finding["status"] in ("OPEN", "OPEN_AWAITING_OWNER"):
            text, evidence = fixes[finding["id"]]
            finding["status"] = "FIXED"
            finding["fix_cycle2"] = {"date": "2026-09-28", "fix": text, "evidence": [ref(e) for e in evidence]}
            changed.append(finding["id"])
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"fixed": changed, "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
