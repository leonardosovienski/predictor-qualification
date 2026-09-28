#!/usr/bin/env bash
# integration-brasileirao, fase cleanroom-final (C5, CLEANROOM_FINAL; C24.3 b/c): só as wheels publicadas, fora dos
# checkouts, no owner_linux (PC 2). Adaptado de qualification/integration-stocks/scripts/cleanroom_final.sh (mesma
# estrutura; domínio brasileirao; uv e Python 3.13 gerenciados; árvores por git archive dos clones).
#
#   1. domínio: a suíte de conformidade da Etapa A (tests/conformance do commit final do Brasileirão, na árvore sem o
#      pacote) contra o brasileirao-predictor INSTALADO da wheel rc4, num venv de teste (uv.lock do commit final,
#      --all-extras, --require-hashes, como pc2_d16_runtime.sh) com o protocolo e o transporte instalados ao lado:
#      C24.3 (c) e as regras de adapter_paths (b, test_import_closure). O Brasileirão não tem teste de adapter no
#      próprio repositório (prompt da sessão 10.1); o adapter é provado por C24.3 (d) e pelo E2E;
#   2. transporte: os testes do pacote (árvore do commit da tag) contra a wheel publicada instalada;
#   3. CAIN: os testes da orquestração (política, configurações de cripto/stocks/brasileirao), do cerco do loop e do
#      SHA completo (árvore do commit final) contra a wheel publicada instalada; pytest do uv.lock do cain (extra dev,
#      --require-hashes) num venv à parte.
# Em todos: pip check, e o módulo carregado vem de site-packages (nunca do checkout). Nenhum dado real.
#
# Uso (com o env.sh do runtime_env.sh): cleanroom_final.sh <runtime_targets.json> <work privado> <out>
set -uo pipefail
TARGETS=$1 WORK=$2 OUT=$3
P="$HOME/predictors"
export PATH="$P/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$P/tools/python" UV_CACHE_DIR="$P/tools/uv-cache" \
  UV_PYTHON_PREFERENCE=only-managed
PY="$P/tools/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13"
REPOS="$P/repos"
mkdir -p "$OUT" "$WORK"
exec > >(tee "$OUT/cleanroom_final.log") 2>&1
field() { "$PY" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d$1)" "$TARGETS"; }
whl() { echo "$(dirname "$CAIN_PY")/../../wheels/$(basename "$(field "['$1']['url']")")"; }
echo "cleanroom-final run_at=$(date -u +%FT%TZ) where=owner_linux (PC 2) uv=$(uv --version)"
status=0
export TMPDIR="$WORK/tmp" BRASILEIRAO_RESEARCH_TEST_ROOT="$WORK/tc" PYTHONIOENCODING=utf-8
mkdir -p "$TMPDIR" "$BRASILEIRAO_RESEARCH_TEST_ROOT" "$WORK/run-domain"
# ---------------------------------------------------------------- 1. domínio
B_COMMIT=$(field "['brasileirao']['commit']")
mkdir -p "$WORK/br-src" && git -C "$REPOS/brasileirao-predictor" -c core.autocrlf=false archive "$B_COMMIT" | tar -x -C "$WORK/br-src"
( cd "$WORK/br-src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/br-conf.txt" -q )
uv venv -q "$WORK/conf-venv" --python 3.13
V="$WORK/conf-venv/bin/python"
uv pip install -q --python "$V" --require-hashes --no-deps -r "$WORK/br-conf.txt"
for key in brasileirao transport protocol; do
  f="$(whl $key)"; echo "$(field "['$key']['sha256']")  $f" | sha256sum -c -; uv pip install -q --python "$V" --no-deps "$f"
done
uv pip check --python "$V"
( cd "$WORK/run-domain" && "$V" -I -c "import brasileirao_predictor, brasileirao_predictor.adapters.research_v2 as a, research_transport, research_protocol.v2, importlib.metadata as m
print('brasileirao', m.version('brasileirao-predictor'), brasileirao_predictor.__file__)
print('adapter', a.__file__)
print('transport', m.version('predictor-research-transport'), research_transport.__file__)
print('protocol', m.version('predictor-research-protocol'))
assert all('site-packages' in f for f in (brasileirao_predictor.__file__, a.__file__, research_transport.__file__))" )
( cd "$BR_TREE" && "$V" -m pytest -p no:cacheprovider -q -rfE tests/conformance --junitxml="$OUT/conformance.junit.xml" )
rc=$?; echo "[conformance exit $rc]"; status=$((status | rc))
# ---------------------------------------------------------------- 2. transporte
T_COMMIT=$(field "['transport']['commit']")
mkdir -p "$WORK/eco-src" && git -C "$REPOS/ecosystem-predictor" -c core.autocrlf=false archive "$T_COMMIT" packages/research-transport | tar -x -C "$WORK/eco-src"
mkdir -p "$WORK/transport-tests" && cp -r "$WORK/eco-src/packages/research-transport/tests/." "$WORK/transport-tests/"
( cd "$WORK/eco-src/packages/research-transport" && uv export --locked --only-group dev --no-emit-project --format requirements-txt -o "$WORK/transport-dev.txt" -q )
uv venv -q "$WORK/transport-venv" --python 3.13
TV="$WORK/transport-venv/bin/python"
uv pip install -q --python "$TV" --require-hashes --no-deps -r "$WORK/transport-dev.txt"
for key in transport protocol; do uv pip install -q --python "$TV" --no-deps "$(whl $key)"; done
uv pip check --python "$TV"
( cd "$WORK/transport-tests" && "$TV" -I -c "import research_transport, research_transport.adapters as t; print('transport', research_transport.__file__, sorted(t.ADAPTERS)); assert 'site-packages' in research_transport.__file__" \
  && "$TV" -m pytest -p no:cacheprovider -q -rA . --junitxml="$OUT/transport.junit.xml" )
rc=$?; echo "[transport exit $rc]"; status=$((status | rc))
# ---------------------------------------------------------------- 3. CAIN
C_COMMIT=$(field "['cain']['commit']")
mkdir -p "$WORK/cain-src" && git -C "$REPOS/cain" -c core.autocrlf=false archive "$C_COMMIT" | tar -x -C "$WORK/cain-src"
mkdir -p "$WORK/cain-tests/tests/unit" "$WORK/cain-tests/tests/integration"
for t in unit/test_orchestration_policy.py unit/test_orchestration_stocks_config.py unit/test_orchestration_brasileirao_config.py \
         unit/test_loop_fenced.py unit/test_findings_pinned_sha.py integration/test_orchestration.py; do
  cp "$WORK/cain-src/tests/$t" "$WORK/cain-tests/tests/$t"
done
( cd "$WORK/cain-src" && uv export --locked --extra dev --no-emit-project --format requirements-txt -o "$WORK/cain-dev-req.txt" -q )
uv venv -q "$WORK/cain-test-venv" --python 3.13
CV="$WORK/cain-test-venv/bin/python"
uv pip install -q --python "$CV" --require-hashes --no-deps -r "$WORK/cain-dev-req.txt"
uv pip install -q --python "$CV" --no-deps "$(whl cain)"
uv pip check --python "$CV"
( cd "$WORK/cain-tests" && "$CV" -I -c "import cain, research_transport.adapters as t; print('cain', cain.__version__, cain.__file__, sorted(t.ADAPTERS)); assert 'site-packages' in cain.__file__" \
  && "$CV" -m pytest -p no:cacheprovider -q -rA tests --junitxml="$OUT/cain.junit.xml" )
rc=$?; echo "[cain exit $rc]"; status=$((status | rc))
echo "cleanroom-final status=$status done $(date -u +%FT%TZ)"
exit $status
