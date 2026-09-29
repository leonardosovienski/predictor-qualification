#!/usr/bin/env bash
# Substituto mínimo de `gh api <path>` para hosts sem o gh CLI (reabertura V1.2, 2026-09-29):
# GET anônimo em https://api.github.com/<path> por curl, mesma saída JSON. Só leitura; repos públicos.
set -euo pipefail
[ "${1:-}" = "api" ] || { echo "gh_api_shim: só 'gh api <path>' é suportado" >&2; exit 2; }
exec curl -sS --fail -H "Accept: application/vnd.github+json" "https://api.github.com/${2#/}"
