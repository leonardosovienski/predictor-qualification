#!/usr/bin/env bash
# brasileirao: D-16 no PC 2 (Ubuntu 24.04 / WSL2) — E2E (parte Linux) e SOAK com o dado real privado.
# Análogo Linux do windows_runtime.sh (dado real) + runtime_cleanroom.sh (Linux primário), sem mudar perfil nem vetores.
#
# Runtime suportado (C3.1): venv limpo, só dependências de RUNTIME exportadas do uv.lock do final_commit com
# --require-hashes (Core e Ops pela URL da release) + a wheel publicada do brasileirao-predictor com sha256 conferido;
# nada de checkout, editable ou PYTHONPATH. A conformidade roda num venv de teste separado (mesmas pinagens + extras).
# Dado (D-11/D-16): ~/predictors/data/d16/brasileirao/matches_source_copy.sqlite3 (só leitura) copiado byte a byte
# para ~/predictors/runtime/brasileirao/data/, sha256 conferido antes e depois (fonte e cópia).
# Saída: OUT = só o que pode entrar na evidência (sem registros do dado); PRIV = saídas com registros (resultados
# `show`, commands.log do real_env), nunca versionadas: só o sha256 delas vai para OUT (pc2_export.py).
# Uso: pc2_d16_runtime.sh <br_commit> <br_wheel_url> <br_wheel_sha256> <out> <priv> <work vazio>
# Ambiente opcional: BRQ_RUNTIME=<raiz do runtime da missão> (padrão ~/predictors/runtime/brasileirao);
#                    BRQ_ONLY_REAL=1 roda só instalação, identidade, conformidade e os 20 pedidos reais (sem E2E e SOAK).
set -uo pipefail
COMMIT="$1"; WHEEL_URL="$2"; WHEEL_SHA="$3"; OUT="$4"; PRIV="$5"; W="$6"
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$HOME/predictors"
R="${BRQ_RUNTIME:-$P/runtime/brasileirao}"
ONLY_REAL="${BRQ_ONLY_REAL:-0}"
SRC_DATA="$P/data/d16/brasileirao/matches_source_copy.sqlite3"
DATA_SHA=31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43
AS_OF=2026-09-08T19:31:32Z
COPY="$R/data/matches_source_copy.sqlite3"
REPO="$P/repos/brasileirao-predictor"
export PATH="$P/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$P/tools/python" UV_CACHE_DIR="$P/tools/uv-cache" UV_PYTHON_PREFERENCE=only-managed
mkdir -p "$OUT" "$PRIV" "$W"
[ -z "$(ls -A "$W")" ] || { echo "work dir não vazio: $W" >&2; exit 2; }
export TMPDIR="$W/tmp" TMP="$W/tmp" TEMP="$W/tmp" BRASILEIRAO_RESEARCH_TEST_ROOT="$W/t" PYTHONIOENCODING=utf-8
mkdir -p "$TMPDIR" "$BRASILEIRAO_RESEARCH_TEST_ROOT" "$W/tc" "$W/elsewhere"
ENV="$OUT/env.log"
fail() { echo "SETUP FAIL: $*" >> "$ENV"; exit 3; }
{
  echo "commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA date=$(date -u +%FT%TZ)"
  echo "host: $(uname -srm) | $(. /etc/os-release && echo "$PRETTY_NAME") | $(grep -qi microsoft /proc/version && echo WSL2) | nproc=$(nproc) | mem_total_kb=$(awk '/MemTotal/{print $2}' /proc/meminfo)"
  uv --version
  echo "scripts: $(cd "$HERE" && sha256sum pc2_d16_runtime.sh soak.py e2e_runtime.py real_env.py core_identity.py runtime_modules.py | tr '\n' ';')"
} > "$ENV" 2>&1

# 0) dado real: fonte só leitura; cópia byte a byte com sha256 conferido (antes)
DATA="$OUT/dataset_sha256.log"
{ echo "# antes $(date -u +%FT%TZ) (esperado $DATA_SHA)"; stat -c '%A %s %n' "$SRC_DATA"; sha256sum "$SRC_DATA"; } > "$DATA" 2>&1
[ "$(sha256sum "$SRC_DATA" | cut -d' ' -f1)" = "$DATA_SHA" ] || fail "fonte com sha256 diferente"
mkdir -p "$R/data"
[ -e "$COPY" ] || { cp "$SRC_DATA" "$COPY" && chmod a-w "$COPY"; }
{ stat -c '%A %s %n' "$COPY"; sha256sum "$COPY"; } >> "$DATA" 2>&1
[ "$(sha256sum "$COPY" | cut -d' ' -f1)" = "$DATA_SHA" ] || fail "cópia com sha256 diferente"

# 1) árvore do final_commit (git archive do clone local, só leitura) e árvore de testes sem os pacotes-fonte
SRC="$W/src"; TREE="$W/tree"; mkdir -p "$SRC" "$TREE"
git -C "$REPO" cat-file -e "$COMMIT^{commit}" 2>> "$ENV" || fail "commit ausente"
git -C "$REPO" archive --format=tar "$COMMIT" | tar -x -C "$SRC" || fail archive
git -C "$REPO" archive --format=tar "$COMMIT" | tar -x -C "$TREE" || fail archive
rm -rf "$TREE/brasileirao_predictor" "$TREE/brasileirao_scripts"
{ [ -e "$TREE/brasileirao_predictor" ] || [ -e "$TREE/brasileirao_scripts" ]; } && fail "pacote-fonte na árvore de testes"

# 2) runtime suportado
RT="$W/rt"; PY="$RT/bin/python"; SCRIPT="$RT/bin/brasileirao-research"; WHL="$W/$(basename "$WHEEL_URL")"
INSTALL="$OUT/install.log"
{
  ( cd "$SRC" && uv export --locked --no-emit-project --format requirements-txt -o "$W/req-runtime.txt" ); echo "uv export exit=$?"
  uv venv "$RT" --python 3.13; echo "uv venv exit=$?"
  uv pip install --python "$PY" --require-hashes --no-deps -r "$W/req-runtime.txt"; echo "deps exit=$?"
  curl -sSfL -o "$WHL" "$WHEEL_URL"; echo "download exit=$?"
  ( cd "$W" && echo "$WHEEL_SHA  $(basename "$WHL")" | sha256sum -c - ); echo "wheel sha256 exit=$?"
  uv pip install --python "$PY" --no-deps "$WHL"; echo "wheel install exit=$?"
  uv pip check --python "$PY"; echo "pip check exit=$?"
} > "$INSTALL" 2>&1
for step in "uv export" deps "wheel sha256" "wheel install" "pip check"; do grep -q "^$step exit=0" "$INSTALL" || fail "install: $step"; done
cp "$W/req-runtime.txt" "$OUT/requirements-runtime.txt"
uv pip freeze --python "$PY" > "$OUT/pip_freeze.txt" 2>&1

# 3) identidade (C4) e trace em runtime, de um diretório fora de tudo
( cd "$W/elsewhere" && "$PY" -I "$HERE/core_identity.py" --lock "$SRC/uv.lock" --pyproject "$SRC/pyproject.toml" ) > "$OUT/core_identity.json" 2>&1
for args in "brasileirao-research --help" "brasileirao-predict --help" "brasileirao-shadow --help"; do
  set -- $args
  ( cd "$W/elsewhere" && "$PY" -I "$HERE/runtime_modules.py" brasileirao-predictor "$@" ) >> "$OUT/runtime_trace.log" 2>&1
done

# 4) conformidade contra a mesma wheel, num venv de teste separado (mesmas pinagens do lock + extras, --require-hashes)
CV="$W/venv-conf"; CPY="$CV/bin/python"
{
  ( cd "$SRC" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$W/req-conf.txt" ); echo "uv export exit=$?"
  uv venv "$CV" --python 3.13; echo "uv venv exit=$?"
  uv pip install --python "$CPY" --require-hashes --no-deps -r "$W/req-conf.txt"; echo "deps exit=$?"
  uv pip install --python "$CPY" --no-deps "$WHL"; echo "wheel install exit=$?"
  ( cd "$TREE" && "$CPY" -c "import brasileirao_predictor;print('package from', brasileirao_predictor.__file__)" )
} > "$OUT/conformance_install.log" 2>&1
( cd "$TREE" && BRASILEIRAO_RESEARCH_TEST_ROOT="$W/tc" "$CPY" -m pytest -p no:cacheprovider -q -rfE tests/conformance \
    --junitxml="$OUT/conformance.junit.xml" ) > "$OUT/conformance.log" 2>&1
echo "[exit $?]" >> "$OUT/conformance.log"

# 5) dado real pelo entrypoint instalado: 20 pedidos (temporada x alvo x baseline), como no windows-smoke
( cd "$W/elsewhere" && "$PY" "$HERE/real_env.py" --script "$SCRIPT" --repo "$REPO" --commit "$COMMIT" --dataset "$COPY" \
    --dataset-sha256 "$DATA_SHA" --as-of "$AS_OF" --work "$W/r2" --out "$PRIV/real" ) > "$PRIV/real.log" 2>&1
echo "[exit $?]" >> "$PRIV/real.log"

if [ "$ONLY_REAL" != "1" ]; then
# 6) E2E real: processo -> término -> processo novo relê o mesmo resultado; cadeia de provenance
#    (pedido idêntico ao do windows-smoke: 2024 OU25 mercado, com client_ref)
mkdir -p "$W/r2/req"
cat > "$W/r2/req/e2e.json" <<'JSON'
{"schema_version": "brasileirao-research-request/1", "request_id": "brasileirao:REQ-E2E-REAL-001",
 "request_type": "WALKFORWARD_FORECAST_EVALUATION", "research_id": "brasileirao:R-REAL-20260924",
 "hypothesis_id": "brasileirao:HQ-SERVING-BASELINE", "competition": "Brasileirão Série A", "season": 2024, "target": "OU25",
 "events": {"kickoff_from": "2024-07-01T00:00:00Z", "kickoff_to": "2024-10-01T00:00:00Z"},
 "data_cutoff": "2026-09-08T19:31:32Z", "decision_lead_minutes": 60,
 "references": {"dataset": {"name": "real-20260908", "version": "1"}, "model": {"name": "serving-baseline", "version": "1"},
   "features": {"name": "elo-home-advantage", "version": "1"}, "baseline": {"name": "market", "version": "1"},
   "cost_model": {"name": "close-slippage-tax", "version": "1"}, "odds": {"name": "sofascore-close", "version": "1"}},
 "priority_hint": "NORMAL", "client_ref": {"e2e": "real"}}
JSON
( cd "$W/elsewhere" && "$PY" "$HERE/e2e_runtime.py" --tests "$TREE/tests" --work "$W/r2/e2e" --out "$PRIV/e2e_real" \
    --real-state "$W/r2/s" --real-policy "$W/r2/policy.json" --real-objects "$W/r2/obj" --real-request "$W/r2/req/e2e.json" ) > "$OUT/e2e_real.log" 2>&1
echo "[exit $?]" >> "$OUT/e2e_real.log"

# 7) SOAK: perfil congelado QUALIFICATION_PROFILE_BR_V1 com o dado real (soak.py --real-dataset)
( cd "$W/elsewhere" && "$PY" "$HERE/soak.py" --tests "$TREE/tests" --work "$W/soak" --log "$OUT/soak.jsonl" \
    --real-dataset "$COPY" --real-dataset-sha256 "$DATA_SHA" --real-as-of "$AS_OF" ) > "$OUT/soak.log" 2>&1
echo "[exit $?]" >> "$OUT/soak.log"
else
  echo "BRQ_ONLY_REAL=1: E2E e SOAK não rodados nesta execução" >> "$ENV"
fi

# 8) dado real depois: fonte e cópia com o mesmo sha256
{ echo "# depois $(date -u +%FT%TZ)"; stat -c '%A %s %n' "$SRC_DATA" "$COPY"; sha256sum "$SRC_DATA" "$COPY"; } >> "$DATA" 2>&1

# 9) separação evidência x privado; números (C20) por script versionado; varreduras
"$PY" "$HERE/pc2_export.py" --priv "$PRIV" --out "$OUT" --state "$W/r2/s" > "$OUT/export.log" 2>&1
echo "[exit $?]" >> "$OUT/export.log"
N="$OUT/evidence_numbers_pc2.json"
{
  "$PY" "$HERE/evidence_numbers.py" junit "$OUT/conformance.junit.xml" --key pc2_conformance --out "$N"; echo "[exit $?]"
  if [ "$ONLY_REAL" != "1" ]; then
    "$PY" "$HERE/evidence_numbers.py" e2e "$OUT/e2e_real/E2E_SUMMARY.json" --key pc2_real --out "$N"; echo "[exit $?]"
    "$PY" "$HERE/evidence_numbers.py" soak "$OUT/soak.jsonl" --key pc2_real --out "$N"; echo "[exit $?]"
  fi
  "$PY" "$HERE/evidence_numbers.py" metrics --results "$PRIV/real" --dataset "$COPY" --clv-diagnostic --key pc2_real --out "$N"; echo "[exit $?]"
} > "$OUT/evidence_numbers.log" 2>&1
"$PY" "$HERE/no_data_rows_check.py" --dataset "$COPY" --paths "$OUT" --out "$OUT/no_data_rows_check.json" > "$OUT/no_data_rows_check.log" 2>&1
echo "[exit $?]" >> "$OUT/no_data_rows_check.log"
"$PY" "$HERE/scan_secrets.py" --paths "$OUT" --out "$OUT/secrets_scan.json" > "$OUT/secrets_scan.log" 2>&1
echo "[exit $?]" >> "$OUT/secrets_scan.log"
echo "done $(date -u +%FT%TZ)" >> "$ENV"
