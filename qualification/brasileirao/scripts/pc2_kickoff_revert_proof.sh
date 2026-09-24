#!/usr/bin/env bash
# brasileirao / temporal-suite (BR_KICKOFF_ORDERING), no PC 2: prova de que o teste pega o bug.
# Num worktree DESCARTÁVEL do final_commit, reverte só o trecho de ordenação de backtest_walkforward.py do a51a68d
# (mantendo o teste) -> o teste falha; restaura -> passa; apaga o worktree; confere que a wheel publicada não mudou.
# Uso: pc2_kickoff_revert_proof.sh <clone> <final_commit> <python com as dependências do lock> <wheel_url> <wheel_sha256>
set -uo pipefail
CLONE="$1"; COMMIT="$2"; PY="$3"; WHEEL_URL="$4"; WHEEL_SHA="$5"
WT="$HOME/predictors/work/brasileirao2-kickoff-proof"
TEST=tests/test_walkforward_row_contract.py
echo "# $(date -u +%FT%TZ) prova do revert (BR_KICKOFF_ORDERING): só o trecho de ordenação do a51a68d"
# só o PRIMEIRO trecho (@@) do diff do a51a68d: o segundo não aplica mais desde o BR-F004 (contexto mudado)
git -C "$CLONE" show --format= a51a68dd5d23734d6ac882cbcf95bc4d5c15b7a6 -- brasileirao_scripts/backtest_walkforward.py \
  | awk '/^@@/{n++} n<2' > "$WT.patch"
cat "$WT.patch"
git -C "$CLONE" worktree add --detach "$WT" "$COMMIT" 2>&1 | tail -1
echo "worktree HEAD $(git -C "$WT" rev-parse HEAD)"
git -C "$WT" apply -R --verbose "$WT.patch" 2>&1; echo "revert apply exit=$?"
git -C "$WT" diff
echo "== teste com o revert (deve FALHAR)"
( cd "$WT" && "$PY" -m pytest -p no:cacheprovider -q -o addopts="" "$TEST" 2>&1 | tail -8 )
git -C "$WT" checkout -- brasileirao_scripts/backtest_walkforward.py
echo "== restaurado"; echo "status: [$(git -C "$WT" status --porcelain | tr '\n' ' ')]"
( cd "$WT" && "$PY" -m pytest -p no:cacheprovider -q -o addopts="" "$TEST" 2>&1 | tail -2 )
git -C "$CLONE" worktree remove "$WT" && rm -f "$WT.patch" && echo "worktree removido: sim"
git -C "$CLONE" worktree list
echo "== wheel publicada:"
curl -sSfL "$WHEEL_URL" | sha256sum | awk -v e="$WHEEL_SHA" '{print $1, ($1==e ? "(= sha256 registrado)" : "(DIFERENTE do registrado)")}'
