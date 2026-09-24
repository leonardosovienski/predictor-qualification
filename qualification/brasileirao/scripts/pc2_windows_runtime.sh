#!/usr/bin/env bash
# brasileirao: runtime Windows do PC 2 (Git Bash), para a prova com dado real entre sistemas operacionais (BR-F018)
# e o windows-smoke da rc nova. Análogo do windows_runtime.sh (PC 1), com raiz autorizada pela missão brasileirao2:
# C:\QUALIFICACAO\runtime\brasileirao2\ (uv e Python 3.13 gerenciados em tools\; nada no Python do sistema).
#
# Dado: a cópia conferida do WSL (~/predictors/runtime/brasileirao2/data, lida por \\wsl.localhost) é copiada byte a
# byte para <raiz>\data (o SQLite não abre URI de outro host); sha256 conferido antes e depois. O dado não sai do PC 2.
# Runtime suportado: venv limpo com as dependências de runtime do uv.lock do commit (--require-hashes) + a wheel
# publicada (sha256 conferido). Conformidade num venv de teste separado. Fonte: clone --bare (sem árvore de trabalho:
# docs/ tem caminhos > 260 caracteres) e git archive só de pyproject.toml, uv.lock, README.md, pytest.ini e tests/.
# Saída: OUT = evidência sem registros do dado; PRIV = resultados com o dado (no WSL, nunca versionados).
# Uso (Git Bash): pc2_windows_runtime.sh <commit> <wheel_url> <wheel_sha256> <label> <out> <priv>
set -uo pipefail
COMMIT="$1"; WHEEL_URL="$2"; WHEEL_SHA="$3"; LABEL="$4"; OUT="$5"; PRIV="$6"
HERE="$(cd "$(dirname "$0")" && pwd)"
R=/c/QUALIFICACAO/runtime/brasileirao2
W="$R/w/$LABEL"
UV="$R/tools/uv/uv.exe"
export UV_PYTHON_INSTALL_DIR="$(cygpath -w "$R/tools/python")" UV_CACHE_DIR="$(cygpath -w "$R/tools/uv-cache")"
export UV_PYTHON_PREFERENCE=only-managed PYTHONIOENCODING=utf-8
SRC_DATA="//wsl.localhost/Ubuntu-24.04/home/superleo13/predictors/runtime/brasileirao2/data/matches_source_copy.sqlite3"
DATA_SHA=31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43
AS_OF=2026-09-08T19:31:32Z
COPY="$R/data/matches_source_copy.sqlite3"
mkdir -p "$R/data"
# OUT e PRIV ficam no WSL (\\wsl.localhost): o Git Bash não faz mkdir -p em caminho UNC; o chamador cria pelo WSL
{ [ -d "$OUT" ] && [ -d "$PRIV" ]; } || { echo "OUT e PRIV precisam existir (crie pelo WSL): $OUT $PRIV" >&2; exit 2; }
[ -e "$W" ] && { echo "work dir já existe: $W" >&2; exit 2; }
mkdir -p "$W/tmp" "$W/elsewhere" "$W/t" "$W/tc"
export TMP="$(cygpath -w "$W/tmp")" TEMP="$(cygpath -w "$W/tmp")" BRASILEIRAO_RESEARCH_TEST_ROOT="$(cygpath -w "$W/t")"
ENV="$OUT/env.log"
fail() { echo "SETUP FAIL: $*" >> "$ENV"; exit 3; }
{
  echo "commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA label=$LABEL date=$(date -u +%FT%TZ)"
  echo "host: $(cmd //c ver | tr -d '\r' | grep -v '^$') | $(uname -srm) | PROCESSOR_ARCHITECTURE=${PROCESSOR_ARCHITECTURE:-?}"
  "$UV" --version
  echo "scripts: $(cd "$HERE" && sha256sum pc2_windows_runtime.sh real_env.py e2e_runtime.py core_identity.py runtime_modules.py pc2_export.py | tr '\n' ';')"
} > "$ENV" 2>&1

# 0) dado: cópia byte a byte com sha256 conferido (antes)
DATA="$OUT/dataset_sha256.log"
{ echo "# antes $(date -u +%FT%TZ) (esperado $DATA_SHA)"; ls -l "$SRC_DATA" | awk '{print $1, $5}'; sha256sum "$SRC_DATA"; } > "$DATA" 2>&1
[ "$(sha256sum "$SRC_DATA" | cut -d' ' -f1)" = "$DATA_SHA" ] || fail "fonte com sha256 diferente"
[ -e "$COPY" ] || { cp "$SRC_DATA" "$COPY" && chmod a-w "$COPY"; }
{ ls -l "$COPY" | awk '{print $1, $5}'; sha256sum "$COPY"; } >> "$DATA" 2>&1
[ "$(sha256sum "$COPY" | cut -d' ' -f1)" = "$DATA_SHA" ] || fail "cópia com sha256 diferente"

# 1) fonte do commit: clone --bare (público) e git archive só do necessário
REPO="$R/repo.git"
[ -d "$REPO" ] || git clone -q --bare https://github.com/leonardosovienski/brasileirao-predictor.git "$REPO" >> "$ENV" 2>&1 || fail clone
git -C "$REPO" fetch -q origin "+refs/heads/*:refs/heads/*" "+refs/tags/*:refs/tags/*" >> "$ENV" 2>&1
git -C "$REPO" cat-file -e "$COMMIT^{commit}" 2>> "$ENV" || fail "commit ausente"
SRC="$W/src"; TREE="$W/tree"; mkdir -p "$SRC" "$TREE"
git -C "$REPO" -c core.autocrlf=false archive --format=tar "$COMMIT" pyproject.toml uv.lock README.md pytest.ini tests | tar -x -C "$SRC" || fail archive
cp -r "$SRC/tests" "$SRC/pytest.ini" "$TREE/" || fail tree

# 2) runtime suportado
RT="$W/rt"; PY="$RT/Scripts/python.exe"; SCRIPT="$RT/Scripts/brasileirao-research.exe"; WHL="$W/$(basename "$WHEEL_URL")"
INSTALL="$OUT/install.log"
{
  ( cd "$SRC" && "$UV" export --locked --no-emit-project --format requirements-txt -o req-runtime.txt ); echo "uv export exit=$?"
  "$UV" venv "$(cygpath -w "$RT")" --python 3.13.15; echo "uv venv exit=$?"
  "$UV" pip install --python "$(cygpath -w "$PY")" --require-hashes --no-deps -r "$(cygpath -w "$SRC/req-runtime.txt")"; echo "deps exit=$?"
  curl -sSfL -o "$WHL" "$WHEEL_URL"; echo "download exit=$?"
  ( cd "$W" && echo "$WHEEL_SHA  $(basename "$WHL")" | sha256sum -c - ); echo "wheel sha256 exit=$?"
  "$UV" pip install --python "$(cygpath -w "$PY")" --no-deps "$(cygpath -w "$WHL")"; echo "wheel install exit=$?"
  "$UV" pip check --python "$(cygpath -w "$PY")"; echo "pip check exit=$?"
} > "$INSTALL" 2>&1
for step in "uv export" deps "wheel sha256" "wheel install" "pip check"; do grep -q "^$step exit=0" "$INSTALL" || fail "install: $step"; done
cp "$SRC/req-runtime.txt" "$OUT/requirements-runtime.txt"
"$UV" pip freeze --python "$(cygpath -w "$PY")" > "$OUT/pip_freeze.txt" 2>&1

# 3) identidade (C4) e trace em runtime
( cd "$W/elsewhere" && "$PY" -I "$(cygpath -w "$HERE/core_identity.py")" --lock "$(cygpath -w "$SRC/uv.lock")" --pyproject "$(cygpath -w "$SRC/pyproject.toml")" ) > "$OUT/core_identity.json" 2>&1
for args in "brasileirao-research --help" "brasileirao-predict --help"; do
  set -- $args
  ( cd "$W/elsewhere" && "$PY" -I "$(cygpath -w "$HERE/runtime_modules.py")" brasileirao-predictor "$@" ) >> "$OUT/runtime_trace.log" 2>&1
done

# 4) conformidade contra a mesma wheel, num venv de teste separado (mesmas pinagens do lock + extras, --require-hashes)
CV="$W/venv-conf"; CPY="$CV/Scripts/python.exe"
{
  ( cd "$SRC" && "$UV" export --locked --all-extras --no-emit-project --format requirements-txt -o req-conf.txt ); echo "uv export exit=$?"
  "$UV" venv "$(cygpath -w "$CV")" --python 3.13.15; echo "uv venv exit=$?"
  "$UV" pip install --python "$(cygpath -w "$CPY")" --require-hashes --no-deps -r "$(cygpath -w "$SRC/req-conf.txt")"; echo "deps exit=$?"
  "$UV" pip install --python "$(cygpath -w "$CPY")" --no-deps "$(cygpath -w "$WHL")"; echo "wheel install exit=$?"
  ( cd "$TREE" && "$CPY" -c "import brasileirao_predictor;print('package from', brasileirao_predictor.__file__)" )
} > "$OUT/conformance_install.log" 2>&1
( cd "$TREE" && BRASILEIRAO_RESEARCH_TEST_ROOT="$(cygpath -w "$W/tc")" "$CPY" -m pytest -p no:cacheprovider -q -rfE tests/conformance \
    --junitxml="$(cygpath -w "$OUT/conformance.junit.xml")" ) > "$OUT/conformance.log" 2>&1
echo "[exit $?]" >> "$OUT/conformance.log"

# 5) dado real pelo entrypoint instalado: 20 pedidos (temporada x alvo x baseline), como no windows-smoke
PW="$W/priv"; mkdir -p "$PW"
( cd "$W/elsewhere" && "$PY" "$(cygpath -w "$HERE/real_env.py")" --script "$(cygpath -w "$SCRIPT")" --repo "$(cygpath -w "$REPO")" \
    --commit "$COMMIT" --dataset "$(cygpath -w "$COPY")" --dataset-sha256 "$DATA_SHA" --as-of "$AS_OF" \
    --work "$(cygpath -w "$W/r2")" --out "$(cygpath -w "$PW/real")" ) > "$PW/real.log" 2>&1
echo "[exit $?]" >> "$PW/real.log"

# 6) E2E real (windows-smoke): processo -> término -> processo novo relê o mesmo resultado (pedido do windows-smoke)
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
( cd "$W/elsewhere" && "$PY" "$(cygpath -w "$HERE/e2e_runtime.py")" --tests "$(cygpath -w "$TREE/tests")" --work "$(cygpath -w "$W/r2/e2e")" \
    --out "$(cygpath -w "$PW/e2e_real")" --real-state "$(cygpath -w "$W/r2/s")" --real-policy "$(cygpath -w "$W/r2/policy.json")" \
    --real-objects "$(cygpath -w "$W/r2/obj")" --real-request "$(cygpath -w "$W/r2/req/e2e.json")" ) > "$OUT/e2e_real.log" 2>&1
echo "[exit $?]" >> "$OUT/e2e_real.log"

# 7) dado depois: fonte e cópia com o mesmo sha256
{ echo "# depois $(date -u +%FT%TZ)"; sha256sum "$SRC_DATA" "$COPY"; } >> "$DATA" 2>&1

# 8) separação evidência x privado (o privado vai para o WSL), números e varreduras
"$PY" "$(cygpath -w "$HERE/pc2_export.py")" --priv "$(cygpath -w "$PW")" --out "$(cygpath -w "$OUT")" --state "$(cygpath -w "$W/r2/s")" > "$OUT/export.log" 2>&1
echo "[exit $?]" >> "$OUT/export.log"
cp -r "$PW/." "$PRIV/" || fail "cópia do privado para o WSL"
N="$OUT/evidence_numbers_win.json"
{
  "$PY" "$(cygpath -w "$HERE/evidence_numbers.py")" junit "$(cygpath -w "$OUT/conformance.junit.xml")" --key win_conformance --out "$(cygpath -w "$N")"; echo "[exit $?]"
  "$PY" "$(cygpath -w "$HERE/evidence_numbers.py")" e2e "$(cygpath -w "$OUT/e2e_real/E2E_SUMMARY.json")" --key win_real --out "$(cygpath -w "$N")"; echo "[exit $?]"
  "$PY" "$(cygpath -w "$HERE/evidence_numbers.py")" metrics --results "$(cygpath -w "$PW/real")" --dataset "$(cygpath -w "$COPY")" --clv-diagnostic --key win_real --out "$(cygpath -w "$N")"; echo "[exit $?]"
} > "$OUT/evidence_numbers.log" 2>&1
"$PY" "$(cygpath -w "$HERE/no_data_rows_check.py")" --dataset "$(cygpath -w "$COPY")" --paths "$(cygpath -w "$OUT")" --out "$(cygpath -w "$OUT/no_data_rows_check.json")" > "$OUT/no_data_rows_check.log" 2>&1
echo "[exit $?]" >> "$OUT/no_data_rows_check.log"
"$PY" "$(cygpath -w "$HERE/scan_secrets.py")" --paths "$(cygpath -w "$OUT")" --out "$(cygpath -w "$OUT/secrets_scan.json")" > "$OUT/secrets_scan.log" 2>&1
echo "[exit $?]" >> "$OUT/secrets_scan.log"
echo "done $(date -u +%FT%TZ)" >> "$ENV"
