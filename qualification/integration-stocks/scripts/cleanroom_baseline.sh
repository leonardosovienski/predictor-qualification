#!/usr/bin/env bash
# integration-stocks, fase cleanroom-baseline (C5): DIAGNÓSTICO do estado inicial, sem valor de gate.
#
# Lado do domínio: venv limpo com as dependências exportadas do uv.lock do stocks-predictor no commit base (61fc017,
# SHA completo, --all-extras, --require-hashes) + a wheel publicada v0.3.0rc2 conferida pelo sha256 + as wheels do
# protocolo V2 congelado e do transporte da integration-crypto (0.1.0rc3), --no-deps; roda a suíte de conformidade da
# Etapa A (árvore do mesmo commit sem o pacote, fora do checkout) contra o pacote INSTALADO.
# Lado do CAIN: venv limpo com as dependências do uv.lock do cain no final_commit da integration-crypto (10744a9) + a
# wheel publicada 0.4.13rc6; `cain research propose --domain stocks` e `predictor-research-consumer --domain stocks`
# mostram o que falta (configuração e allowlist do Stocks).
#
# Uso: cleanroom_baseline.sh <out_dir> <work_dir> <clone stocks-predictor> <clone cain> <python gerenciado 3.13>
set -uo pipefail
OUT="$1"; WORK="$2"; STOCKS="$3"; CAIN="$4"; PY="$5"
BASE=61fc017256ffea815ae96bbe02b847dccdb395cc
CAIN_BASE=10744a9f149610d7741431c28c1e78c681c41165
REL=https://github.com/leonardosovienski
STOCKS_URL=$REL/stocks-predictor/releases/download/v0.3.0rc2/stocks_predictor-0.3.0rc2-py3-none-any.whl
STOCKS_SHA=92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8
PROTO_URL=$REL/ecosystem-predictor/releases/download/predictor-research-protocol-v2.0.0rc2/predictor_research_protocol-2.0.0rc2-py3-none-any.whl
PROTO_SHA=34a1e4121e4085b901e3bd96552e2f5b4067c5e6af5e99dc1c26d6276fc7c820
TRANSPORT_URL=$REL/ecosystem-predictor/releases/download/predictor-research-transport-v0.1.0rc3/predictor_research_transport-0.1.0rc3-py3-none-any.whl
TRANSPORT_SHA=ee1f550de36b28ee9ec559f1649e5eb7635849c6247adb8610605047e802701f
CAIN_URL=$REL/cain/releases/download/v0.4.13rc6/cain_research-0.4.13rc6-py3-none-any.whl
CAIN_SHA=16510acdafb0141f7452c9f4ff372d7bfa2b0086b5354710c300e008f3f92aa4
mkdir -p "$OUT" "$WORK"
exec > >(tee "$OUT/cleanroom_baseline.log") 2>&1
echo "run_at $(date -u +%FT%TZ) host $(hostname) (PC 2, WSL — DIAGNÓSTICO) uv $(uv --version) python $("$PY" --version)"
rm -rf "$WORK/src" "$WORK/tree" "$WORK/venv" "$WORK/cain-src" "$WORK/cain-venv" "$WORK/run" "$WORK"/*.whl
mkdir -p "$WORK/src" "$WORK/tree" "$WORK/run" "$WORK/cain-src"
fetch() { curl -sSfL -o "$WORK/$(basename "$1")" "$1" && echo "$2  $WORK/$(basename "$1")" | sha256sum -c -; }
# ---------------------------------------------------------------- domínio
git -C "$STOCKS" archive "$BASE" | tar -x -C "$WORK/src"
git -C "$STOCKS" archive "$BASE" | tar -x -C "$WORK/tree"
rm -rf "$WORK/tree/stocks_predictor"
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" -q ) || exit 3
"$PY" -m venv "$WORK/venv" || exit 3
V="$WORK/venv/bin/python"
"$V" -m pip install -q --require-hashes -r "$WORK/req.txt" || exit 3
fetch "$STOCKS_URL" "$STOCKS_SHA" || exit 3
fetch "$PROTO_URL" "$PROTO_SHA" || exit 3
fetch "$TRANSPORT_URL" "$TRANSPORT_SHA" || exit 3
"$V" -m pip install -q --no-deps "$WORK/$(basename "$STOCKS_URL")" "$WORK/$(basename "$PROTO_URL")" "$WORK/$(basename "$TRANSPORT_URL")" || exit 3
"$V" -m pip check
"$V" -m pip freeze > "$OUT/pip_freeze_domain.txt"
cd "$WORK/run"
"$V" -I -c "import stocks_predictor, research_protocol.v2, research_transport, importlib.metadata as m; print('stocks', m.version('stocks-predictor'), stocks_predictor.__file__); print('protocol', m.version('predictor-research-protocol'), research_protocol.v2.REGISTRY_SHA256); print('transport', m.version('predictor-research-transport'))"
echo "--- suíte de conformidade da Etapa A contra o pacote instalado"
( cd "$WORK/tree" && "$V" -m pytest -p no:cacheprovider -q -rA tests/conformance --junitxml="$OUT/conformance.junit.xml" )
echo "[conformance exit $?]"
echo "--- consumidor do transporte para o domínio stocks (allowlist fixa)"
"$WORK/venv/bin/predictor-research-consumer" --domain stocks --spool "$WORK/run/spool" --ledger "$WORK/run/ledger.sqlite" \
  --state "$WORK/run/st" --policy "$WORK/run/p.json" --objects "$WORK/run/o"
echo "[consumer exit $?]"
# ---------------------------------------------------------------- CAIN
git -C "$CAIN" archive "$CAIN_BASE" | tar -x -C "$WORK/cain-src"
( cd "$WORK/cain-src" && uv export --locked --no-dev --no-emit-project --format requirements-txt -o "$WORK/cain-req.txt" -q ) || exit 3
"$PY" -m venv "$WORK/cain-venv" || exit 3
C="$WORK/cain-venv/bin/python"
"$C" -m pip install -q --require-hashes -r "$WORK/cain-req.txt" || exit 3
fetch "$CAIN_URL" "$CAIN_SHA" || exit 3
"$C" -m pip install -q --no-deps "$WORK/$(basename "$CAIN_URL")" || exit 3
"$C" -m pip check
"$C" -m pip freeze > "$OUT/pip_freeze_cain.txt"
echo '{"schema":"cain-proposal/1","proposal_id":"cain:CLEANROOM-BASELINE","domain":"stocks","request":{}}' > "$WORK/run/p.json"
"$WORK/cain-venv/bin/cain" research propose --domain stocks --state "$WORK/run/cain-state" --proposal "$WORK/run/p.json" --as-of 2026-09-27T00:00:00Z
echo "[cain propose stocks exit $?] state_created=$([ -e "$WORK/run/cain-state" ] && echo yes || echo no)"
"$C" -I -c "from importlib.resources import files; print('configs', sorted(p.name for p in files('cain.orchestration').joinpath('data').iterdir()))"
echo "done $(date -u +%FT%TZ)"
