"""integration-crypto, cleanroom-final (C5): requisitos de teste do transporte a partir do uv.lock do pacote no commit da tag.

O lock do transporte 0.1.0rc7 (b0da4fd8) é anterior à R01 e fixa o protocolo pela URL de release do repositório
antigo (404 desde o rename); `uv export` tenta resolver essa URL e falha. Este script lê o lock (tomllib) e emite só o
fecho do grupo `dev` (pytest e dependências), cada pacote com `==versão --hash=sha256:…` de todas as distribuições
listadas no lock, sem o projeto e sem o protocolo (instalado depois, da wheel publicada, --no-deps). Nenhuma versão é
escolhida aqui: tudo vem do lock.
Uso: python transport_dev_requirements.py <uv.lock> <nome do projeto> <saída.txt> [pacotes a omitir...]
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def main() -> int:
    lock_path, project, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    omit = set(sys.argv[4:]) | {project}
    lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    packages = {p["name"]: p for p in lock["package"]}
    root = packages[project]
    todo = [d["name"] for d in root.get("dev-dependencies", {}).get("dev", [])]
    seen: list[str] = []
    while todo:
        name = todo.pop(0)
        if name in seen or name in omit:
            continue
        seen.append(name)
        for d in packages[name].get("dependencies", []):
            todo.append(d["name"])
    lines = []
    for name in sorted(seen):
        p = packages[name]
        hashes = sorted({d["hash"] for d in (p.get("wheels", []) + ([p["sdist"]] if "sdist" in p else [])) if "hash" in d})
        if not hashes:
            raise SystemExit(f"{name}: sem hash no lock")
        lines.append(f"{name}=={p['version']} " + " ".join(f"--hash={h}" for h in hashes))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out}: {len(lines)} pacotes do grupo dev do lock de {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
