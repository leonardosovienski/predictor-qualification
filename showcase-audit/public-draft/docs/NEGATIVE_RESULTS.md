# Negative Results and Retractions

Negative results are treated as evidence. Each line states what was expected, what was found, and what changed afterwards. Causality is not asserted beyond what the records say.

## Falsified or closed hypotheses

| Domain | Expected | Found | Changed afterwards |
|---|---|---|---|
| football | A +44% ROI backtest indicated edge | Variance from two long-odds hits; favourites under-rated | Rating compression diagnosed; betting trigger retired |
| football | Richer attack/defence model beats single strength | Estimator confound; control model wins | Document retracted and replaced |
| football | Edge transfers between competitions | Confidence interval crossed zero | Hypothesis refuted; prospective replication inconclusive |
| football | More frequent refits help | Favourable point estimate, interval crossed zero | Refuted; corrected successor pre-registered |
| football | Serving beats climatology | Baseline contaminated by its own cohort | Never judged; bug fixed first |
| football | Historical point-in-time evaluation is reconstructible | Timestamps absent on both market and feature sides | Declared not viable; prospective-only path |
| football | Live forecasting is feasible at personal cost | Data not provable, cost above ceiling | Hold |
| crypto | Derivatives regime signals predict returns | Net of costs: negative | Family frozen |
| crypto | A pre-cost parameter sweep with excellent score | Artefact of searching without costs | Discarded |
| crypto | LLM score predicts 7-day returns | Significant correlation in the opposite direction | Family refuted (four incarnations) |
| crypto | Simple trend rules work | Gross positive, net negative or gate not met | No-go |
| equities | Six classical factor families generate signal | None supported; deflated Sharpe below threshold | Closed |
| equities | Pre-registered new-source hypotheses ready to run | Data-quality problem | Paused |
| equities | Rally-in-restructuring hypothesis | Zero real observations collected; structural power too low | Archived |
| governance | A central aggregator (gateway, database, scheduler) was needed | No domain used it; zero coverage | Removed from the codebase |
| commercial | An independent-review service has demand | Zero conversations, zero payments | Hypothesis explicitly unvalidated |

## Methodological findings against ourselves

| Finding | Where | Response |
|---|---|---|
| All registered trials lacked third-party-reproducible provenance | adversarial audit, 2026-09-05 | Provenance made mandatory in the trial registry |
| Multiplicity discount nearly inoperative in practice | same audit | Attempt counts recorded as audit facts; attestation required to update verdicts |
| Governance gate could be bypassed by overwriting a verdict | same audit | Contract change: attestation also required on update |
| A published runner wheel had not passed release gates | same audit | Release pipeline fixed |
| Fixing in the repository is not fixing in production | audit addendum | Stated as a standing risk |
| A positive-control attestation was invalidated by a core upgrade, and the registry initially said "no reissue needed" | equities, September 2026 | Registry corrected; a test now forbids that combination |
| Three qualification attestations stopped re-validating when later artefacts were rewritten in place | qualification, 2026-09-30 | Open P1; reissue or isolation pending |
| An operational seal is broken on the equities main branch | 2026-09-30 | Left broken on purpose: resealing with today's data would weaken the seal |
| Free-form synthesis by local models produced false conclusions with exact quotes | agent evaluation, 2026-09-11 | Synthesis marked "not certified"; literal retrieval only |
| Two concurrent consumers produced false reconciliation states | joint test, 2026-09-28 | Exclusive lock per domain; 20/20 afterwards |
| Same requests produced different numbers on different operating systems | football qualification | Fixed; 20/20 identical across OS afterwards |
