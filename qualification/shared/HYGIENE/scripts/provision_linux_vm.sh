#!/usr/bin/env bash
# D-9 / HYG-012: provisionamento reproduzível do host Linux de qualificação.
#
# Alvo: Ubuntu x86_64 descartável (VM na nuvem sob demanda, GitHub Codespaces ou
# runner ubuntu-latest do GitHub Actions). O host é destruído ao fim do uso; nada
# aqui é instalação operacional. Não lê nem grava segredos: só repositórios
# públicos, uv por sha256 e Python gerenciado pelo uv.
#
# Uso: provision_linux_vm.sh [raiz] [ref]
#   raiz  diretório de qualificação (padrão: $HOME/qualificacao)
#   ref   ref dos 7 repositórios (padrão: main); o SHA efetivo vai para o recibo
#
# Saída: <raiz>/PROVISION_RECEIPT.json (SO, kernel, uv, Python, HEAD de cada repo)
set -euo pipefail

ROOT=${1:-"$HOME/qualificacao"}
REF=${2:-main}
UV_VERSION=0.12.18
UV_ASSET=uv-x86_64-unknown-linux-gnu.tar.gz
UV_SHA256=89eadd7c76fc063887959510d5ba0ab1264dfd5f1143b925ddb73021a40acf16
PYTHON_VERSION=3.13
OWNER=https://github.com/leonardosovienski
REPOS="cain ecosystem-predictor core-predictor predictor-ops brasileirao-predictor cripto-predictor stocks-predictor"

[ "$(uname -s)" = Linux ] || { echo "Linux obrigatório" >&2; exit 2; }
[ "$(uname -m)" = x86_64 ] || { echo "x86_64 obrigatório" >&2; exit 2; }
. /etc/os-release
[ "$ID" = ubuntu ] || { echo "Ubuntu obrigatório (encontrado: $ID)" >&2; exit 2; }
for tool in git curl tar sha256sum; do command -v "$tool" >/dev/null || { echo "falta $tool" >&2; exit 2; }; done

mkdir -p "$ROOT"/{tools,repos,runtime,logs}
export UV_CACHE_DIR="$ROOT/tools/uv-cache" UV_PYTHON_INSTALL_DIR="$ROOT/tools/python"
export UV_PYTHON_PREFERENCE=only-managed UV_NO_CONFIG=1

# uv fixado por versão e sha256 (asset da release oficial)
if [ ! -x "$ROOT/tools/uv/uv" ]; then
  tmp=$(mktemp -d)
  curl -sSfL -o "$tmp/$UV_ASSET" "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$UV_ASSET"
  echo "$UV_SHA256  $tmp/$UV_ASSET" | sha256sum -c -
  mkdir -p "$ROOT/tools/uv"
  tar -xzf "$tmp/$UV_ASSET" -C "$ROOT/tools/uv" --strip-components=1
  rm -rf "$tmp"
fi
UV="$ROOT/tools/uv/uv"
"$UV" --version | grep -q "^uv $UV_VERSION "
"$UV" python install "$PYTHON_VERSION"
PY=$("$UV" python find "$PYTHON_VERSION")

# Clones limpos (só leitura pública), sem credenciais
for repo in $REPOS; do
  dest="$ROOT/repos/$repo"
  if [ ! -d "$dest/.git" ]; then
    git -c advice.detachedHead=false clone --quiet --branch "$REF" "$OWNER/$repo.git" "$dest"
  fi
  test -z "$(git -C "$dest" status --porcelain)" || { echo "$repo sujo" >&2; exit 3; }
done

# Recibo do host (sem segredos)
{
  printf '{\n  "schema": "provision-receipt/1",\n'
  printf '  "generated_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "os": "%s",\n  "kernel": "%s",\n' "$PRETTY_NAME" "$(uname -r)"
  printf '  "uv": "%s",\n  "uv_asset_sha256": "%s",\n' "$("$UV" --version)" "$UV_SHA256"
  printf '  "python": "%s",\n  "python_path": "%s",\n' "$("$PY" -c 'import platform; print(platform.python_version())')" "$PY"
  printf '  "ref": "%s",\n  "repos": {\n' "$REF"
  first=1
  for repo in $REPOS; do
    [ $first = 1 ] || printf ',\n'; first=0
    printf '    "%s": "%s"' "$repo" "$(git -C "$ROOT/repos/$repo" rev-parse HEAD)"
  done
  printf '\n  }\n}\n'
} > "$ROOT/PROVISION_RECEIPT.json"
cat "$ROOT/PROVISION_RECEIPT.json"
echo "PROVISION_OK"
