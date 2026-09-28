"""integration-brasileirao (5.2 do prompt da sessão): as fontes do Brasileirão em tools/hypothesis_sources.json do CAIN
são byte a byte iguais entre o pino declarado (reviewed_commit) e a base 25cdf4d?

Só leitura: `git cat-file` num clone bare do brasileirao-predictor. Imprime, por fonte, blob no pino, blob na base, se
são iguais e se o sha256 declarado confere com os bytes da base. Os arquivos são registros versionados públicos do
repositório (trials, docs e protocolos), não o dado privado; o script não imprime conteúdo.

Uso: python hypothesis_sources_pin_check.py <hypothesis_sources.json> <clone bare do brasileirao-predictor> <base>
"""

import hashlib
import json
import subprocess
import sys

sources_path, repo, base = sys.argv[1:4]
doc = json.load(open(sources_path, encoding="utf-8"))
project = next(p for p in doc["projects"] if p["domain"] == "brasileirao")
pin = project["reviewed_commit"]


def blob(commit: str, path: str) -> str | None:
    r = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "-q", f"{commit}:{path}"], capture_output=True, text=True)
    return r.stdout.strip() or None


def content(obj: str) -> bytes:
    return subprocess.run(["git", "-C", repo, "cat-file", "blob", obj], capture_output=True, check=True).stdout


print(f"pin {pin}")
print(f"base {base}")
print(f"sources {len(project['sources'])}")
equal = sha_ok = 0
for s in project["sources"]:
    b_pin, b_base = blob(pin, s["path"]), blob(base, s["path"])
    same = b_pin is not None and b_pin == b_base
    ok = b_base is not None and hashlib.sha256(content(b_base)).hexdigest() == s["sha256"]
    equal += same
    sha_ok += ok
    print(f"SOURCE {'IGUAL' if same else 'DIFERENTE'} sha256_declarado_na_base={'OK' if ok else 'FALHA'} "
          f"pin_blob={b_pin} base_blob={b_base} {s['path']}")
print(f"iguais {equal}/{len(project['sources'])} sha256_ok {sha_ok}/{len(project['sources'])}")
print("decisao " + ("pino equivalente: todas as fontes byte a byte iguais na base"
                    if equal == sha_ok == len(project["sources"]) else "reler na base 25cdf4d"))
