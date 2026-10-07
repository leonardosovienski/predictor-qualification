#!/usr/bin/env bash
# integration-crypto, fase cleanroom-final (C5, CLEANROOM_FINAL; C24.3 c): só as wheels publicadas, fora dos checkouts.
#
#   1. domínio: a suíte de conformidade da Etapa A (tests/conformance do commit final do cripto, copiada para fora do
#      pacote) contra o cripto-predictor INSTALADO da wheel rc, no venv do consumidor (com o protocolo e o transporte
#      instalados ao lado): C24.3 (c) e as regras de adapter_paths (b);
#   2. transporte: os testes do pacote (árvore do commit da tag) contra a wheel publicada instalada;
#   3. CAIN: os testes da orquestração, do cerco do loop e do SHA completo (árvore do commit final) contra a wheel
#      publicada instalada; pytest do uv.lock do cain (extra dev, --require-hashes; wheels do stack do registro STACK_WHEELS.json, D-32) num venv à parte.
# Em todos: pip check, e o módulo carregado vem de site-packages (nunca do checkout).
#
# Uso (com o env.sh do runtime_env.sh): cleanroom_final.sh <runtime_targets.json> <work> <out>
set -uo pipefail
TARGETS=$1 WORK=$2 OUT=$3
PY=${PYTHON:-python3.13}
mkdir -p "$OUT"
exec > >(tee "$OUT/cleanroom_final.log") 2>&1
field() { "$PY" -c "import json;d=json.load(open('$TARGETS'));print(d$1)"; }
echo "cleanroom-final run_at=$(date -u +%FT%TZ) where=${GITHUB_ACTIONS:+github_actions} python=$("$PY" --version 2>&1)"
status=0
# ---------------------------------------------------------------- 1. domínio
cd "$WORK" && mkdir -p run-domain && cd run-domain
"$CONSUMER_PY" -I -c "import GarimpoInvestimentos, research_transport, research_protocol.v2, importlib.metadata as m
print('cripto', m.version('cripto-predictor'), GarimpoInvestimentos.__file__)
print('transport', m.version('predictor-research-transport'), research_transport.__file__)
print('protocol', m.version('predictor-research-protocol'))
assert all('site-packages' in f for f in (GarimpoInvestimentos.__file__, research_transport.__file__))"
"$CONSUMER_PY" -m pytest -p no:cacheprovider -q -rA "$CRIPTO_TESTS/conformance" --junitxml="$OUT/conformance.junit.xml"
rc=$?; echo "[conformance exit $rc]"; status=$((status | rc))
# ---------------------------------------------------------------- 2. transporte
T_COMMIT=$(field "['transport']['commit']")
git clone -q "https://github.com/$(field "['transport']['repo']").git" "$WORK/eco-src" && git -C "$WORK/eco-src" checkout -q "$T_COMMIT"
mkdir -p "$WORK/transport-tests" && cp -r "$WORK/eco-src/packages/research-transport/tests/." "$WORK/transport-tests/"
( cd "$WORK/eco-src/packages/research-transport" && uv export --locked --only-group dev --no-emit-project --format requirements-txt -o "$WORK/transport-dev.txt" -q )
"$PY" -m venv "$WORK/transport-venv"
"$WORK/transport-venv/bin/python" -m pip install -q --require-hashes -r "$WORK/transport-dev.txt"
for key in transport protocol; do
  f="$WORK/$(basename "$(field "['$key']['url']")")"; "$WORK/transport-venv/bin/python" -m pip install -q --no-deps "$f"
done
"$WORK/transport-venv/bin/python" -m pip check
( cd "$WORK/transport-tests" && "$WORK/transport-venv/bin/python" -m pytest -p no:cacheprovider -q -rA . --junitxml="$OUT/transport.junit.xml" )
rc=$?; echo "[transport exit $rc]"; status=$((status | rc))
# ---------------------------------------------------------------- 3. CAIN
mkdir -p "$WORK/cain-tests/tests/unit" "$WORK/cain-tests/tests/integration"
for t in unit/test_orchestration_policy.py unit/test_loop_fenced.py unit/test_findings_pinned_sha.py integration/test_orchestration.py; do
  cp "$WORK/cain-src/tests/$t" "$WORK/cain-tests/tests/$t"
done
( cd "$WORK/cain-src" && uv export --locked --extra dev --no-emit-project --format requirements-txt -o "$WORK/cain-dev-nostack.txt" -q \
  && "$PY" tools/stack_wheels.py requirements --project . --input "$WORK/cain-dev-nostack.txt" --output "$WORK/cain-dev-req.txt" )
"$PY" -m venv "$WORK/cain-test-venv"
"$WORK/cain-test-venv/bin/python" -m pip install -q --require-hashes --find-links "$WORK/cain-src/.stack-wheels" -r "$WORK/cain-dev-req.txt"
"$WORK/cain-test-venv/bin/python" -m pip install -q --no-deps "$WORK/$(basename "$(field "['cain']['url']")")"
"$WORK/cain-test-venv/bin/python" -m pip check
( cd "$WORK/cain-tests" && "$WORK/cain-test-venv/bin/python" -I -c "import cain, research_transport; print('cain', cain.__version__, cain.__file__); assert 'site-packages' in cain.__file__" \
  && "$WORK/cain-test-venv/bin/python" -m pytest -p no:cacheprovider -q -rA tests --junitxml="$OUT/cain.junit.xml" )
rc=$?; echo "[cain exit $rc]"; status=$((status | rc))
echo "cleanroom-final status=$status done $(date -u +%FT%TZ)"
exit $status
