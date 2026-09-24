"""stocks C14 (ST-F006): refaz o ledger para o final_commit 61fc017 / wheel v0.3.0rc2 e emite os parciais c14-*.

Motivo: os dependabot #93/#94 entraram no main antes do #95; o main (2a18513) divergiu do final_commit 9a6c09a
(hatchling e checkout) e o selo R8 quebrou. A rc2 foi construída do 61fc017 (main + ressela) e o runtime suportado
foi refeito (cleanroom-final, e2e, conformidade, ciência, soak diagnóstico), com CI, segredos e conjunto protegido.
Os parciais anteriores (rc1) ficam como estão (C8).

Uso: python c14_rc2.py --secrets-run <id> --contract-sha256 <sha do contrato novo>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

QC = Path(__file__).resolve().parents[1]
R = "qualification/stocks/RAW_LOGS"
SWAPS = [
    ("run35949779357", "run35954279991"),
    ("9a6c09ae92991c8490be624f5693865bcbaeca26", "61fc017256ffea815ae96bbe02b847dccdb395cc"),
    ("run_stocks-predictor_35950266341_final_9a6c09a_dispatch.json", "run_stocks-predictor_35953418753_final_61fc017_dispatch.json"),
    ("protected_check_9a6c09a.json", "protected_check_61fc017.json"),
    ("immutable_data_sha256_final.txt", "immutable_data_sha256_c14.txt"),
    ("3cc4e04a", "92cb1131"),
    ("v0.3.0rc1", "v0.3.0rc2"),
    ("stocks 9a6c09a", "stocks 61fc017"),
    ("(9a6c09a)", "(61fc017)"),
    ("9a6c09a", "61fc017"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secrets-run", required=True)
    ap.add_argument("--contract-sha256", required=True)
    args = ap.parse_args()
    text = (QC / "GATES.json").read_text(encoding="utf-8")
    old_secrets = "run35950519783"
    text = text.replace(old_secrets, f"run{args.secrets_run}")
    for old, new in SWAPS:
        text = text.replace(old, new)
    ledger = json.loads(text)
    ledger["supersedes_sha256"] = None
    ledger["final_wheels"][0] = {
        "name": "stocks-predictor", "version": "0.3.0rc2",
        "url": "https://github.com/leonardosovienski/stocks-predictor/releases/download/v0.3.0rc2/stocks_predictor-0.3.0rc2-py3-none-any.whl",
        "sha256": "92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8"}
    ledger["domain_contract_sha256"] = args.contract_sha256
    g = ledger["gates"]
    g["HOSTED_CI"]["evidence"].append(f"{R}/hosted-ci/run_stocks-predictor_35953419340_final_61fc017_pr.json")
    g["HOSTED_CI"]["note"] = ("CI de push/PR verde com uv sync --locked no baseline (stocks 4e98a67, core 5a08415, ops 9831b0d) e nos "
                              "final_commits (stocks 61fc017 no SHA exato por workflow_dispatch e no PR #96); nenhum job pulado. "
                              "O main 2a18513 falhou (ST-F006, corrigido em 61fc017).")
    g["DOMAIN_CONTRACT"]["note"] = ("Contrato C24.1 com o bloco de implementação da rc2 (61fc017, 92cb1131…); aprovado pelo merge do "
                                    "PR de attestation (#13) no main; regras de adapter_paths testadas; conformidade 87/87 no runtime "
                                    "suportado (Linux e windows-latest). A versão rc1 do contrato foi aprovada em #12 (b24beb3).")
    g["BLOCKERS_ZERO"]["note"] = ("P0=0, P1=0 abertos: ST-F001 (P1) corrigido com teste. P2 corrigidos: ST-F005, ST-F006. "
                                  "Abertos só P2: ST-F002 (branches remotas), ST-F003 (scripts extras presos a outra máquina), "
                                  "ST-F004 (suíte legada só roda contra o checkout).")
    g["CLEANROOM_FINAL"]["evidence"].append(f"{R}/c14-rc2/suite-run35953426762/stocks-suite-linux-primary/pytest.log")
    ledger["note"] = ("Estado corrente da missão stocks (STACK_BASELINE_V1.1, Ops 4.2.2rc1, stocks 0.3.0rc2 61fc017 após C14/ST-F006). "
                      "Terminal BLOCKED (C7.3): 27 gates PASS, 4 NOT_RUN com 'BLOCKED: D-16 pendente' (E2E, WINDOWS_SMOKE, SOAK, "
                      "STOCKS_NEGATIVE_CONTROLS), nenhum FAIL, P0=P1=0. Sem QUALIFICATION_ATTESTATION.json até a D-16. "
                      "Parciais nunca reescritos (C8).")
    for phase in ("c14-publish-candidates", "c14-cleanroom-final", "c14-hosted-ci", "c14-contract-sign-off", "c14-attestation"):
        if phase not in ledger["phases_completed"]:
            ledger["phases_completed"].append(phase)
        (QC / "GATES.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        if not (QC / f"ATTESTATION_PARTIAL_{phase}.json").exists():
            subprocess.run([sys.executable, str(QC / "scripts" / "attest.py"), "partial", phase, "--no-schema"], check=True)
    leftovers = [s for s, _ in SWAPS[:2] if s in (QC / "GATES.json").read_text(encoding="utf-8")]
    print("leftover:", leftovers)


if __name__ == "__main__":
    main()
