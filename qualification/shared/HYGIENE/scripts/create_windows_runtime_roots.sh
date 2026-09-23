#!/usr/bin/env bash
# D-3 / HYG-012: raízes de runtime de qualificação no Windows (idempotente).
# Só cria diretórios vazios nos caminhos aprovados; nunca toca instalação
# operacional. Stocks não tem runtime no Windows (D-1).
set -euo pipefail
ROOTS=(
  "C:/Cripto/qualificacao/runtime"              # crypto
  "C:/QUALIFICACAO/runtime/brasileirao"         # brasileirao
  "C:/QUALIFICACAO/runtime/integration"         # integration: CAIN e Brasileirão
  "C:/Cripto/qualificacao/runtime/integration"  # integration: parte Cripto
)
for root in "${ROOTS[@]}"; do
  case "$root" in
    C:/CAIN*|C:/Cripto/operacao*|C:/Cripto/pesquisa-*|C:/Cripto/restaurado-*|C:/STOCKS/data*)
      echo "recusado (instalação operacional): $root" >&2; exit 2 ;;
  esac
  if [ -d "$root" ]; then state=EXISTS; else mkdir -p "$root"; state=CREATED; fi
  echo "$state $root entries=$(ls -A "$root" | wc -l)"
done
