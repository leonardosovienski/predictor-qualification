# Evidence Pack

Everything below can be checked mechanically by anyone who later gains access to the private artefacts, and can be anchored externally (timestamping service) without revealing content. Labels are generic on purpose. All timestamps are internal (Git and JSON) unless stated otherwise.

## 1. Qualification attestations (current)

| Artefact | Result | Gates passed | Findings (P0/P1/P2) | Issued (UTC, from the artefact) | Size (bytes) | SHA-256 |
|---|---|---|---|---|---|---|
| Crypto domain — stage A | QUALIFIED | 31/31 | 0 / 0 / 7 | 2026-09-24T13:53Z | 34087 | `2b1491a03a6b757071d184128ebb13cc30eaaa0cb301427373ea7d4f678da406` |
| Equities domain — stage A | QUALIFIED | 31/31 | 0 / 0 / 3 | 2026-09-25T16:20Z | 45921 | `e0f2e28ddd0c1887faaba3f409dacc3c49de9854eed38ba286ed3cc501f99c2e` |
| Football domain — stage A | QUALIFIED | 32/32 | 0 / 0 / 5 | 2026-09-25T16:07Z | 56268 | `a4fa2fee25b65c39888d90cd947fc36ba63076eae536e5b676052470ed7521e4` |
| Crypto domain — stage B (integration with the agent) | QUALIFIED | 30/30 | 0 / 0 / 4 | 2026-09-28T18:10Z | 32725 | `69fa0393a24ca727da7dc0131aa5b25935810d64e72095febddd65541aff88e7` |
| Equities domain — stage B | QUALIFIED | 30/30 | 0 / 0 / 0 | 2026-09-28T18:27Z | 38148 | `60b75594a229b0bffb9078302e791fc1cf7b7a6f332a2b7f8c36e18fb521846c` |
| Football domain — stage B | QUALIFIED | 30/30 | 0 / 0 / 1 | 2026-09-28T18:54Z | 34693 | `99dd94bdac947860293325e21053dbb6caa941dacb035facd2e57a523e8534d8` |

Every attestation records `capital_permission = false` and `training_started = false`. Nineteen superseded attestations are preserved, each referenced by the hash of the one it replaced; the three immediately preceding stage-B attestations are:

| Superseded artefact | Issued (UTC) | SHA-256 |
|---|---|---|
| Crypto — stage B, previous stack | 2026-09-28T15:38Z | `a071fe2ca22e4f301f8ba426ff772a20c506942561276739ad519f61c36831f6` |
| Equities — stage B, previous stack | 2026-09-28T15:32Z | `9979d19be7fc22f4731878d77496b91489b60fdf0bf350ff3336e81986791eae` |
| Football — stage B, previous stack | 2026-09-28T15:25Z | `8aef11046708d53504da06c3796af1d5f14b024524c64290e7792527b517e29e` |

**Known limitation:** as of 2026-09-30, three of the six current attestations (crypto stage A, crypto stage B, equities stage B) validate only against the commit at which they were issued, because artefacts they reference were later rewritten in place. This is recorded as an open P1 finding in the private repository.

## 2. Joint test of the three real domains driven by the research agent (2026-09-28)

| Stack | Artefact | Result | Finished (UTC) | Size | SHA-256 |
|---|---|---|---|---|---|
| final | summary | 58 passed / 0 failed | 2026-09-28T18:54 | 27796 | `964f014d413ed6ed4db246d2ec9e97097776f3014afcf0e10f91a3abcc5e6e5a` |
| final | command log | — | — | 75670 | `338fad3c321399d3f287edf86512540c7a0dd5490277c92f8225e1551d2ed01b` |
| final | lock-contention log | 20/20 per domain | — | 331755 | `77eb7ee70906ba1a235525fd7a24239bd613935c43f6424e2b4f1be8a270e3b3` |
| final | data-integrity check | clean | — | 267 | `f0a2ad5d1e3c8362a58b698392643e058723f5af45c93c5c601b5415376fb339` |
| previous | summary | 57 passed / 1 failed | 2026-09-28T15:56 | 30402 | `39adaafe13cfe6c5e163d5371a2529ba71149e5b7a0c48d57eeef4deae627002` |
| previous | command log | — | — | 75142 | `d30c0a86c3534ddcc3b82068a3b36ef978990f328b0cedf46eb5e10e205a04ec` |
| previous | lock-contention log | one domain failed 2/20 | — | 345460 | `fba4944d4b43777528697af196a285b9ecb817d798a069b019e843e926ede32b` |

Earlier, unpublished attempts on the same day scored 47/57 and 56/58; the failures were in the test script and in a concurrency defect later fixed in the transport layer.

## 3. Positive-control (judge power) attestations, crypto domain

Synthetic controls only: they certify that the statistical judges respond correctly to planted signal and noise. They are **not** market evidence.

| Executed | Status at audit (2026-10-06) | Metric family | Core version | SHA-256 |
|---|---|---|---|---|
| 2026-09-07 | recorded historical source | A | 3.2.0 | `97ceb19036967be7519b633c1087140237630d920a094894e762cbef346f10b1` |
| 2026-09-07 | recorded historical source | B | 3.2.0 | `3656accf2eec642812bc5f09fdc2c3abb094fdd2d32f8572300143496a345d15` |
| 2026-09-12 | expired | A | 3.2.1 | `6e3018ed635fb64dee9dfb621bae811b553012a63cf107b09c66f6d2868cde7b` |
| 2026-09-12 | expired | B | 3.2.1 | `141b11fd863a5fcd2f2d55ae2c60c2af66df90a13b81c3cef6f23c15ef4a6033` |
| 2026-09-20 | expired | A | 3.2.1 | `faec0fcce0ae6d842dbb9ce204b661e4088ca7d31eb8a0e97912c86c5b713aae` |
| 2026-09-20 | expired | B | 3.2.1 | `6a61bdf061a38fe2a62f6e54f02cc86d9bbdaa485f6f9a337b116f1357c50c6b` |
| 2026-09-27 | superseded | A | 3.2.1 | `c57f5005b8771f9e8e193fa609079289762bd128c02102cf5e0527da30b3ff87` |
| 2026-09-27 | superseded | B | 3.2.1 | `5c8bb71906ca0b74c67746df331156096e1c803bea0e55b8c2f316071da790ad` |
| 2026-10-02 | aligned (renewed automatically by scheduled workflow) | A | 3.2.1 | `095afecddf30f11407aeb3111cc900e00c3597f2cf8ff45692c62c0618f3115c` |
| 2026-10-02 | aligned | B | 3.2.1 | `f12da16f2e2a2cb2788d04f8ca51d4d3c280e73c388bf9f5e979a543f9748ce4` |

Attestations expire after seven days by design; expiry is recorded, never silently extended.

## 4. Published package wheels (hash-pinned by every consumer)

| Package role | Version | SHA-256 |
|---|---|---|
| scientific core | 3.2.1 | `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` |
| operations runner | 4.2.2rc1 | `0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3` |
| governance/contracts | 0.2.1 | `69374cf0eca60301724f07153b8a815c4807f808ace98d0188807e890ae6a80c` |
| research agent | 0.4.13rc15 | `ff642b7271a7fcad18723b12bc7ebe29f0c2550ecfe178777b5c1481882aacf9` |
| crypto domain | 1.2.0rc4 | `32a4bd6d86719070e1a5d1e418c46034cfbf4ee292da11f17af2f60081fa9bf6` |
| equities domain | 0.3.0rc3 | `902f0d34efe7aef02c084e7886ef997c9b3f9bfe28e0e923c9c178361131ea00` |
| football domain | 0.3.0rc5 | `be3bc5127ef64f1a3265b2e97384db3f4883d7d404030bed85aaa9fef1a078a6` |

## 5. Counts verified during the independent audit of 2026-10-06

| Item | Count |
|---|---|
| Transport-layer tests reproduced offline on the governance repository head | 310 passed (7 not collected: native dependency unavailable offline) |
| Registry invariant checks reproduced | 2/2 |
| Harness attestation files whose hash matches the registry | 10/10 |
| Qualification manifest entries verified | 13/13 |
| Joint-test artefacts whose hash matches the governance record | 7/7 |
| Registered football trials in the repository head | 29 (1 confirmed, 6 refuted, 6 inconclusive, 8 pre-registered awaiting data, 3 superseded, 3 informative, 2 exploratory) |
| Adversarial point-in-time cases, equities circuit | 15/15 passed, Linux and Windows |
| Negative-control executions on real equities panel | 81, all within frozen criteria |

## 6. What this pack does and does not prove

- **Content integrity:** a SHA-256 digest identifies the bytes of an artefact; anyone holding the artefact can confirm it is the one referred to here.
- **Internal timestamps only:** all dates above come from fields inside the artefacts and from commits in private repositories. They are not independent evidence of when something was created.
- **No temporal precommitment:** this pack has not been anchored by an external timestamping service. Nothing here establishes priority or anteriority to a third party; the hashes are integrity evidence only.
- **No semantic validity:** a correct hash says nothing about whether the content is right, and nothing here is evidence of predictive or economic validity.

Earlier attestations were superseded after subsequent verification. Only current attestations should be treated as active evidence.
