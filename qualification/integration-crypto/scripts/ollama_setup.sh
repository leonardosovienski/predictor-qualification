#!/usr/bin/env bash
# integration-crypto, soak: modelo local para as propostas de LLM (auditadas; não são gate, C9).
# Instala o Ollama pelo instalador oficial no runner efêmero do GitHub Actions, sobe o servidor em loopback e baixa
# o modelo; registra versão, modelo e digest. Não roda fora do Actions (o PC do dono não é tocado).
# Uso: ollama_setup.sh <out>
set -uo pipefail
OUT=$1; mkdir -p "$OUT"
exec > >(tee "$OUT/ollama_setup.log") 2>&1
[ -n "${GITHUB_ACTIONS:-}" ] || { echo "ollama_setup só roda no GitHub Actions"; exit 2; }
curl -fsSL https://ollama.com/install.sh -o "$OUT/install.sh"
sha256sum "$OUT/install.sh"
sh "$OUT/install.sh" > "$OUT/install.log" 2>&1 || { echo "OLLAMA_INSTALL_FAILED"; exit 3; }
(OLLAMA_HOST=127.0.0.1:11434 nohup ollama serve > "$OUT/serve.log" 2>&1 &)
for _ in $(seq 1 60); do curl -sf http://127.0.0.1:11434/api/tags > /dev/null && break; sleep 2; done
ollama --version
ollama pull qwen2.5:0.5b > "$OUT/pull.log" 2>&1 || { echo "OLLAMA_PULL_FAILED"; exit 3; }
curl -s http://127.0.0.1:11434/api/tags
