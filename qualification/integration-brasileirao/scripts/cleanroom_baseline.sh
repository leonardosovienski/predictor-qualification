#!/usr/bin/env bash
# integration-brasileirao, fase cleanroom-baseline (C5): DIAGNÓSTICO do estado inicial, sem valor de gate.
#
# Lado do domínio: venv limpo com as dependências exportadas do uv.lock do brasileirao-predictor no commit base
# (25cdf4d, SHA completo, --locked, --all-extras, --require-hashes; como qualification/brasileirao/scripts/
# pc2_d16_runtime.sh) + a wheel publicada v0.3.0rc3 conferida pelo sha256 + as wheels do protocolo V2 congelado e do
# transporte da integration-stocks (0.1.0rc4), --no-deps; roda a suíte de conformidade da Etapa A (árvore do mesmo
# commit sem o pacote, fora do checkout) contra o pacote INSTALADO.
# Lado do CAIN: venv limpo com as dependências do uv.lock do cain no final_commit da integration-stocks (deccaaa) + a
# wheel publicada 0.4.13rc7; `cain research propose --domain brasileirao` e `predictor-research-consumer --domain
# brasileirao` mostram o que falta (configuração e allowlist do Brasileirão).
# uv e Python 3.13 gerenciados de ~/predictors/tools; nada de checkout, editable ou PYTHONPATH no runtime.
# Nenhum dado real: a conformidade usa só os datasets sintéticos da suíte.
#
# Uso: cleanroom_baseline.sh <out_dir> <work_dir> <clone brasileirao-predictor> <clone cain>
set -uo pipefail
OUT="$1"; WORK="$2"; BR="$3"; CAIN="$4"
BASE=25cdf4d9bb309d33f066fbc6a379f5d98c69f08a
CAIN_BASE=deccaaa0a0e2cb2b5f292614659eb4bf2e943e50
REL=https://github.com/leonardosovienski
BR_URL=$REL/brasileirao-predictor/releases/download/v0.3.0rc3/brasileirao_predictor-0.3.0rc3-py3-none-any.whl
BR_SHA=403e6a022b10e2b6d05ef1828894bf3ad0b1d049301e3dfce9cf79dc262000ea
PROTO_URL=$REL/ecosystem-predictor/releases/download/predictor-research-protocol-v2.0.0rc2/predictor_research_protocol-2.0.0rc2-py3-none-any.whl
PROTO_SHA=34a1e4121e4085b901e3bd96552e2f5b4067c5e6af5e99dc1c26d6276fc7c820
TRANSPORT_URL=$REL/ecosystem-predictor/releases/download/predictor-research-transport-v0.1.0rc4/predictor_research_transport-0.1.0rc4-py3-none-any.whl
TRANSPORT_SHA=7a71ccd14934252c1b11801d1efb31c7f05fc6eda6104413ab148a81c66ab805
CAIN_URL=$REL/cain/releases/download/v0.4.13rc7/cain_research-0.4.13rc7-py3-none-any.whl
CAIN_SHA=5560bc813189b6087e197c606502ebc7a1b920d4a6efbcc1b33cd3975a03e98d
export PATH="$HOME/predictors/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$HOME/predictors/tools/python" \
  UV_CACHE_DIR="$HOME/predictors/tools/uv-cache" UV_PYTHON_PREFERENCE=only-managed
mkdir -p "$OUT" "$WORK"
exec > >(tee "$OUT/cleanroom_baseline.log") 2>&1
echo "run_at $(date -u +%FT%TZ) host $(hostname) (PC 2, WSL = owner_linux; fase de DIAGNÓSTICO) uv $(uv --version)"
rm -rf "$WORK/src" "$WORK/tree" "$WORK/venv" "$WORK/cain-src" "$WORK/cain-venv" "$WORK/run" "$WORK"/*.whl
mkdir -p "$WORK/src" "$WORK/tree" "$WORK/run" "$WORK/cain-src" "$WORK/tmp" "$WORK/tc"
export TMPDIR="$WORK/tmp" BRASILEIRAO_RESEARCH_TEST_ROOT="$WORK/tc" PYTHONIOENCODING=utf-8
fetch() { curl -sSfL -o "$WORK/$(basename "$1")" "$1" && echo "$2  $WORK/$(basename "$1")" | sha256sum -c -; }
# ---------------------------------------------------------------- domínio
git -C "$BR" archive "$BASE" | tar -x -C "$WORK/src"
git -C "$BR" archive "$BASE" | tar -x -C "$WORK/tree"
rm -rf "$WORK/tree/brasileirao_predictor" "$WORK/tree/brasileirao_scripts"
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" -q ) || exit 3
uv venv -q "$WORK/venv" --python 3.13 || exit 3
V="$WORK/venv/bin/python"
echo "python $("$V" --version)"
uv pip install -q --python "$V" --require-hashes --no-deps -r "$WORK/req.txt" || exit 3
fetch "$BR_URL" "$BR_SHA" || exit 3
fetch "$PROTO_URL" "$PROTO_SHA" || exit 3
fetch "$TRANSPORT_URL" "$TRANSPORT_SHA" || exit 3
uv pip install -q --python "$V" --no-deps "$WORK/$(basename "$BR_URL")" "$WORK/$(basename "$PROTO_URL")" "$WORK/$(basename "$TRANSPORT_URL")" || exit 3
uv pip check --python "$V"
uv pip freeze --python "$V" > "$OUT/pip_freeze_domain.txt"
cd "$WORK/run"
"$V" -I -c "import brasileirao_predictor, research_protocol.v2, research_transport.adapters as t, importlib.metadata as m; print('brasileirao', m.version('brasileirao-predictor'), brasileirao_predictor.__file__); print('protocol', m.version('predictor-research-protocol'), research_protocol.v2.REGISTRY_SHA256); print('transport', m.version('predictor-research-transport'), sorted(t.ADAPTERS))"
echo "--- suíte de conformidade da Etapa A contra o pacote instalado"
( cd "$WORK/tree" && "$V" -m pytest -p no:cacheprovider -q -rfE tests/conformance --junitxml="$OUT/conformance.junit.xml" )
echo "[conformance exit $?]"
echo "--- consumidor do transporte para o domínio brasileirao (allowlist fixa)"
"$WORK/venv/bin/predictor-research-consumer" --domain brasileirao --spool "$WORK/run/spool" --ledger "$WORK/run/ledger.sqlite" \
  --state "$WORK/run/st" --policy "$WORK/run/p.json" --objects "$WORK/run/o"
echo "[consumer exit $?]"
# ---------------------------------------------------------------- CAIN
git -C "$CAIN" archive "$CAIN_BASE" | tar -x -C "$WORK/cain-src"
( cd "$WORK/cain-src" && uv export --locked --no-dev --no-emit-project --format requirements-txt -o "$WORK/cain-req.txt" -q ) || exit 3
uv venv -q "$WORK/cain-venv" --python 3.13 || exit 3
C="$WORK/cain-venv/bin/python"
uv pip install -q --python "$C" --require-hashes --no-deps -r "$WORK/cain-req.txt" || exit 3
fetch "$CAIN_URL" "$CAIN_SHA" || exit 3
uv pip install -q --python "$C" --no-deps "$WORK/$(basename "$CAIN_URL")" || exit 3
uv pip check --python "$C"
uv pip freeze --python "$C" > "$OUT/pip_freeze_cain.txt"
for pkg in brasileirao_predictor stocks_predictor GarimpoInvestimentos; do
  "$C" -I -c "import $pkg" 2>/dev/null && echo "CAIN venv tem $pkg instalado" || echo "CAIN venv sem $pkg (ok)"
done
echo '{"schema":"cain-proposal/1","proposal_id":"cain:CLEANROOM-BASELINE","domain":"brasileirao","request":{}}' > "$WORK/run/p.json"
"$WORK/cain-venv/bin/cain" research propose --domain brasileirao --state "$WORK/run/cain-state" --proposal "$WORK/run/p.json" --as-of 2026-09-27T00:00:00Z
echo "[cain propose brasileirao exit $?] state_created=$([ -e "$WORK/run/cain-state" ] && echo yes || echo no)"
"$C" -I -c "from importlib.resources import files; print('configs', sorted(p.name for p in files('cain.orchestration').joinpath('data').iterdir()))"
echo "done $(date -u +%FT%TZ)"
