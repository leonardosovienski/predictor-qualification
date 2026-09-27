#!/usr/bin/env bash
# integration-crypto, fase cleanroom-baseline (C5): DIAGNÓSTICO do estado inicial, sem valor de gate.
#
# Lado do domínio: venv limpo com as dependências exportadas do uv.lock do cripto no commit base (341d270, SHA
# completo, --require-hashes) + a wheel publicada v1.2.0rc2 conferida pelo sha256 + a wheel congelada do protocolo V2;
# roda a suíte de conformidade da Etapa A (árvore tests/ do mesmo commit, fora do checkout do pacote) contra o pacote
# INSTALADO. Lado do CAIN: confere se existe wheel publicada para o commit base do cain (release/tag).
#
# Uso: cleanroom_baseline.sh <out_dir> <work_dir> <clone cripto-predictor> <clone cain> <python gerenciado 3.13>
set -uo pipefail
OUT="$1"; WORK="$2"; CRIPTO="$3"; CAIN="$4"; PY="$5"
BASE=341d270e4d709150c581c3cd93f4518d483009eb
CAIN_BASE=f343701937a7a798d66e11d2d8aa18e24395e215
WHEEL_URL=https://github.com/leonardosovienski/cripto-predictor/releases/download/v1.2.0rc2/cripto_predictor-1.2.0rc2-py3-none-any.whl
WHEEL_SHA=6e62f67f0779aef7e913d34b4d3d3d6ed5f88ad882e8fa8372f54c4ab59bc8ee
PROTO_URL=https://github.com/leonardosovienski/ecosystem-predictor/releases/download/predictor-research-protocol-v2.0.0rc2/predictor_research_protocol-2.0.0rc2-py3-none-any.whl
PROTO_SHA=34a1e4121e4085b901e3bd96552e2f5b4067c5e6af5e99dc1c26d6276fc7c820
mkdir -p "$OUT" "$WORK"
exec > >(tee "$OUT/cleanroom_baseline.log") 2>&1
echo "run_at $(date -u +%FT%TZ) host $(hostname) (PC 2, WSL — DIAGNÓSTICO) uv $(uv --version) python $("$PY" --version)"
rm -rf "$WORK/src" "$WORK/tests" "$WORK/venv" "$WORK/run"; mkdir -p "$WORK/src" "$WORK/tests" "$WORK/run"
git -C "$CRIPTO" archive "$BASE" | tar -x -C "$WORK/src"
cp -r "$WORK/src/tests/." "$WORK/tests/"
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" ) || exit 3
"$PY" -m venv "$WORK/venv" || exit 3
V="$WORK/venv/bin/python"
"$V" -m pip install -q --require-hashes -r "$WORK/req.txt" || exit 3
for spec in "$WHEEL_URL $WHEEL_SHA" "$PROTO_URL $PROTO_SHA"; do
  set -- $spec; name=$(basename "$1")
  curl -sSfL -o "$WORK/$name" "$1" || exit 3
  echo "$2  $WORK/$name" | sha256sum -c - || exit 3
done
"$V" -m pip install -q --no-deps "$WORK/cripto_predictor-1.2.0rc2-py3-none-any.whl" "$WORK/predictor_research_protocol-2.0.0rc2-py3-none-any.whl" || exit 3
"$V" -m pip check
"$V" -m pip freeze > "$OUT/pip_freeze.txt"
cd "$WORK/run"
"$V" -I -c "import GarimpoInvestimentos, research_protocol.v2, importlib.metadata as m; print('cripto', m.version('cripto-predictor'), GarimpoInvestimentos.__file__); print('protocol', m.version('predictor-research-protocol'), research_protocol.v2.REGISTRY_SHA256)"
echo "--- suíte de conformidade da Etapa A contra o pacote instalado"
"$V" -m pytest -p no:cacheprovider -q -rA "$WORK/tests/conformance" --junitxml="$OUT/conformance.junit.xml"
echo "[conformance exit $?]"
echo "--- cain: wheel publicada no commit base?"
git -C "$CAIN" fetch -q origin --tags
echo "tags no commit base: [$(git -C "$CAIN" tag --points-at "$CAIN_BASE" | tr '\n' ' ')]"
echo "versão no pyproject da base: $(git -C "$CAIN" show "$CAIN_BASE:pyproject.toml" | grep -m1 '^version')"
gh release list -R leonardosovienski/cain -L 20
echo "done $(date -u +%FT%TZ)"
