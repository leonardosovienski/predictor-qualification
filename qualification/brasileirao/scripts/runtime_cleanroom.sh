#!/usr/bin/env bash
# brasileirao: runtime suportado (C3.1) — instalação limpa só com wheels publicadas, fora do checkout.
# Fases: cleanroom-final, temporal-suite + idempotency-failure (suíte de conformidade), e2e, soak (perfil V1).
# Uso: runtime_cleanroom.sh <out_dir> <br_commit> <br_wheel_url> <br_wheel_sha256> [soak:0|1]
set -uo pipefail
OUT="$1"; COMMIT="$2"; WHEEL_URL="$3"; WHEEL_SHA="$4"; SOAK="${5:-0}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
EXE=""; [ "${OS:-}" = "Windows_NT" ] && EXE=".exe"
# Windows: raiz curta (o contrato limita a raiz de estado a 120 caracteres por causa do MAX_PATH)
if [ -n "$EXE" ]; then mkdir -p /c/q; export TMPDIR=/c/q; fi
WORK="$(mktemp -d)"
BIN=bin; [ -n "$EXE" ] && BIN=Scripts
fail() { echo "SETUP FAIL: $*" >> "$OUT/env.log"; exit 3; }
{
  echo "commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA date=$(date -u +%FT%TZ) uname=$(uname -a)"
  uv --version
} > "$OUT/env.log" 2>&1

# 1) fonte só para o lock e para a árvore de testes do final_commit (sem o pacote-fonte)
git clone -q https://github.com/leonardosovienski/brasileirao-predictor.git "$WORK/src" >> "$OUT/env.log" 2>&1 || fail clone
git -C "$WORK/src" checkout -q "$COMMIT" >> "$OUT/env.log" 2>&1 || fail checkout
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" ) >> "$OUT/env.log" 2>&1 || fail export
# árvore de testes = o final_commit inteiro MENOS o pacotes-fonte brasileirao_predictor/ e brasileirao_scripts/:
# o código do pacote só pode vir da wheel instalada; scripts/, charters/, docs/ etc. são do repo
mkdir -p "$WORK/tree"
git -C "$WORK/src" archive --format=tar "$COMMIT" | tar -x -C "$WORK/tree"
rm -rf "$WORK/tree/brasileirao_predictor" "$WORK/tree/brasileirao_scripts"
{ [ -e "$WORK/tree/brasileirao_predictor" ] || [ -e "$WORK/tree/brasileirao_scripts" ]; } && fail "package source still in test tree"

# 2) venv limpo: dependências do lock com --require-hashes; wheel do brasileirao-predictor pela URL da release
uv venv "$WORK/venv" --python 3.13 >> "$OUT/env.log" 2>&1 || fail venv
PY="$WORK/venv/$BIN/python$EXE"
"$PY" -m ensurepip >> "$OUT/env.log" 2>&1 || fail ensurepip
"$PY" -m pip install -q --require-hashes -r "$WORK/req.txt" >> "$OUT/env.log" 2>&1 || fail deps
curl -sSfL -o "$WORK/$(basename "$WHEEL_URL")" "$WHEEL_URL" || fail download
( cd "$WORK" && echo "$WHEEL_SHA  $(basename "$WHEEL_URL")" | sha256sum -c - ) >> "$OUT/env.log" 2>&1 || fail "wheel sha256"
"$PY" -m pip install -q --no-deps "$WORK/$(basename "$WHEEL_URL")" >> "$OUT/env.log" 2>&1 || fail install
"$PY" -m pip check >> "$OUT/env.log" 2>&1 || fail "pip check"
"$PY" -m pip freeze > "$OUT/pip_freeze.txt" 2>&1

# 3) identidade (C4) e trace em runtime (C2/C3.1), a partir de um diretório fora de tudo
mkdir -p "$WORK/elsewhere"
( cd "$WORK/elsewhere" && "$PY" -I "$HERE/core_identity.py" --lock "$WORK/src/uv.lock" --pyproject "$WORK/src/pyproject.toml" ) > "$OUT/core_identity.json" 2>&1
for args in "brasileirao-research --help" "brasileirao-predict --help" "brasileirao-shadow --help"; do
  set -- $args
  ( cd "$WORK/elsewhere" && "$PY" -I "$HERE/runtime_modules.py" brasileirao-predictor "$@" ) >> "$OUT/runtime_trace.log" 2>&1
done

# 4) conformidade e suíte completa sobre a wheel instalada (árvore sem os pacotes-fonte)
export BRQ_ROOT="$WORK/cr"; mkdir -p "$BRQ_ROOT/tmp" "$BRQ_ROOT/t"
export TMP="$BRQ_ROOT/tmp" TEMP="$BRQ_ROOT/tmp" TMPDIR="$BRQ_ROOT/tmp" BRASILEIRAO_RESEARCH_TEST_ROOT="$BRQ_ROOT/t"
( cd "$WORK/tree" && "$PY" -c "import brasileirao_predictor,brasileirao_scripts;print(brasileirao_predictor.__file__, brasileirao_scripts.__file__)" ) >> "$OUT/env.log" 2>&1
( cd "$WORK/tree" && "$PY" -m pytest -p no:cacheprovider -q -rA tests/conformance --junitxml="$OUT/conformance.junit.xml" ) > "$OUT/conformance.log" 2>&1
echo "[exit $?]" >> "$OUT/conformance.log"
( cd "$WORK/tree" && "$PY" -m pytest -p no:cacheprovider -q -rfE --continue-on-collection-errors tests --junitxml="$OUT/full_suite.junit.xml" ) > "$OUT/full_suite.log" 2>&1
echo "[exit $?]" >> "$OUT/full_suite.log"

# 5) E2E pelo entrypoint instalado: processo → término → processo novo relê o mesmo resultado
( cd "$WORK/elsewhere" && "$PY" "$HERE/e2e_runtime.py" --tests "$WORK/tree/tests" --work "$WORK/e2e" --out "$OUT/e2e" ) > "$OUT/e2e.log" 2>&1
echo "[exit $?]" >> "$OUT/e2e.log"

# 6) soak (perfil congelado) — com vetores sintéticos é diagnóstico (D-16 pendente)
if [ "$SOAK" = "1" ]; then
  ( cd "$WORK/elsewhere" && "$PY" "$HERE/soak.py" --tests "$WORK/tree/tests" --work "$WORK/soak" --log "$OUT/soak.jsonl" ) > "$OUT/soak.log" 2>&1
  echo "[exit $?]" >> "$OUT/soak.log"
fi
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
