# ecosystem-predictor

**Research showcase and public evidence pack** for a one-person research programme (2026) that built prediction systems in three domains, found that its real problems were problems of *evaluation*, and responded by building evidence discipline: pre-registration, verifiable temporal integrity, protocol-based qualification with hash-identified attestations, and a research agent that proposes experiments but never gains authority.

> This repository contains **evidence, not implementation**. Code, parameters, prompts, schemas, data and logs remain private. Everything here is either an aggregate result with a traceable source, a dated negative result, a hash you can check, or a limitation we state ourselves.

---

## 15 seconds

- Three prediction domains (football, equities, crypto); dozens of hypotheses judged against pre-registered criteria; **zero** approved for capital.
- The interesting output is not a model. It is a **discipline**: retractions, falsified hypotheses, adversarial audits, qualification attestations, and a containment design for AI research agents.
- Open question we want funded: *can a research agent use evidence to change what it investigates without that evidence becoming a route to more authority?* Status: **proposed, not tested**.

## 2 minutes

**What was built.** A shared scientific library (temporal contracts, anti-lookahead replay, trial provenance, positive-control attestations); a generic job runner; three domain research systems; an evidence-transport layer; a qualification protocol with frozen gates and raw logs; and a research agent that admits evidence into an append-only memory and issues proposals through a deterministic, versioned decision policy. Every component declares *capital forbidden*. All counts below are dated; see the Evidence Pack.

**Main projects.** Scientific core · operations runner · football domain · equities domain · crypto domain · governance/contracts · research agent · qualification protocol. Ten published packages pinned by hash in a single joint lock.

**Trajectory (June → October 2026).** Prediction systems → evaluation failures and false positives (a +44% backtest ROI explained as variance; an LLM-derived signal whose recorded verdict showed correlation in the *opposite* direction; a baseline contaminated by its own cohort) → reproducibility and governance in the core library (pre-registration, trial provenance, attestations; an internal adversarial audit that broke the "a third party can verify this" thesis and was answered in the next release) → formal qualification (six attestations, a 58/58 joint test of the three real domains with the agent) → a research agent whose containment is built and tested, and whose scientific question remains open.

**Key evidence.** See [`docs/EVIDENCE_PACK.md`](docs/EVIDENCE_PACK.md): SHA-256 of every attestation, of the joint-test artefacts and of the harness attestations, with dates. See [`docs/NEGATIVE_RESULTS.md`](docs/NEGATIVE_RESULTS.md) for what did not work and what changed afterwards.

**Relation to the research agent (CAIN).** The agent *proposes*; a deterministic policy *decides*; the domain *admits and executes*; nothing in the chain can grant capital, budget or evaluator access. This containment is **built and tested**. Whether it changes how agents behave under incentive is **not yet measured**.

## 10 minutes

| Section | What you will find |
|---|---|
| [Evidence Pack](docs/EVIDENCE_PACK.md) | Hashes, dates, counts. Mechanically verifiable. |
| [Research Cards](docs/RESEARCH_CARDS.md) | 15 research lines: question, method at concept level, result, status. |
| [Negative Results](docs/NEGATIVE_RESULTS.md) | Falsified hypotheses, retractions, removed architecture. |
| [Lineage](docs/LINEAGE.md) | Dated chronology of the intellectual path, including dead ends. |
| [Illustrative Architecture](docs/ARCHITECTURE_ILLUSTRATIVE.md) | Conceptual model only. Does not describe the private implementation. |
| [Limitations](docs/LIMITATIONS.md) | What we do not claim, and what is currently broken or unverified. |
| [Next Experiments](docs/NEXT_EXPERIMENTS.md) | Proposed, not implemented. |
| [Funding](docs/FUNDING.md) | What funding unlocks, specifically. |

### Results in one paragraph

No economic edge was demonstrated in any domain; every economic state is *no edge* or *inconclusive*, and capital is forbidden by contract and configuration everywhere. What was demonstrated, in narrow and dated scopes: fifteen adversarial point-in-time attacks repelled with zero leakage in the equities circuit, and future-information canaries failing closed in all three domains; 81 negative-control executions behaving as required; six qualification attestations with zero critical findings; a joint test of the three real domains driven by the agent passing 58/58 after three documented iterations (47/57, 56/58, 57/58); and 29 registered football trials of which one was confirmed (in forecast quality, not profit), six refuted and six inconclusive.

### Limitations in one paragraph

Three of the six attestations no longer re-validate against the current state of the qualification repository because later artefacts were rewritten in place; an operational seal in the equities domain is broken on its main branch by a documented decision; the agent's free-form synthesis with local models produced false conclusions even with exact quotes; the agent's evaluation corpus is small and not held-out; and this is a one-person programme in which AI agents acted as executors and internal reviewers. All of this is stated in [Limitations](docs/LIMITATIONS.md).

### Funding need in one paragraph

Funding would pay for the pre-registered A/B/C experiment on evidence-versus-authority with a held-out corpus and an independent human judge; licensed point-in-time market data to decide two blocked research lines; external human review of the attestations; and the machine time and secondary environments needed to close currently blocked qualification gates.

---

*Nothing here is a product, a recommendation, or an authorisation of capital. All code remains proprietary and private. Hashes in the Evidence Pack are evidence of content integrity only; they have not been externally timestamped and make no claim of anteriority. Text and tables: [CC BY 4.0](LICENSE). Contact: the owner's public GitHub profile, [leonardosovienski](https://github.com/leonardosovienski).*
