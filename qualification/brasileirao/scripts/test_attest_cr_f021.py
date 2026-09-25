"""CR-F021 (brasileirão): attest.py check confere a C7.1 regra 3 em TODO arquivo de evidência.

Além das evidências dos gates, o check tem de acusar sha256 divergente nas evidências de
`environments`, nos veredictos compartilhados (`verdict_sha256`) e no `findings_file`. Pela C7.1 regra 6 do núcleo
v2.3 (D-22), aceita o núcleo em que a attestation foi emitida, desde que seja uma versão do histórico.

Uso: python -m pytest qualification/brasileirao/scripts/test_attest_cr_f021.py  (precisa de jsonschema)
"""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("brasileirao_attest", Path(__file__).resolve().parent / "attest.py")
attest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(attest)
WRONG = "0" * 64


@pytest.fixture(scope="module")
def doc() -> dict:
    return attest.build("IN_PROGRESS")


def test_fresh_partial_passes(doc: dict) -> None:
    assert attest.check(copy.deepcopy(doc)) == []
    assert doc["common_core_sha256"] == attest.sha(attest.CORE)
    assert doc["common_core_version"] == attest.CORE_VERSIONS[doc["common_core_sha256"]]


def test_environment_evidence_is_checked(doc: dict) -> None:
    tampered = copy.deepcopy(doc)
    tampered["environments"][0]["evidence"][0]["sha256"] = WRONG
    assert any("environment" in p for p in attest.check(tampered))


def test_shared_verdict_is_checked(doc: dict) -> None:
    tampered = copy.deepcopy(doc)
    tampered["shared_dependency_verdicts"][0]["verdict_sha256"] = WRONG
    assert any("verdict_sha256" in p for p in attest.check(tampered))


def test_findings_file_is_checked(doc: dict) -> None:
    tampered = copy.deepcopy(doc)
    tampered["findings_file"]["sha256"] = WRONG
    assert any("findings_file" in p for p in attest.check(tampered))


def test_any_core_of_the_history_is_accepted(doc: dict) -> None:
    for core_sha in attest.CORE_VERSIONS:
        for result in ("IN_PROGRESS", "NOT_QUALIFIED"):
            old = copy.deepcopy(doc)
            old["common_core_sha256"], old["result"] = core_sha, result
            old["domain_contract_sha256"] = attest.sha(attest.QC / "DOMAIN_RESEARCH_CONTRACT.json")
            assert not any("C7.1(6)" in p for p in attest.check(old))


def test_core_outside_the_history_is_rejected(doc: dict) -> None:
    unknown = copy.deepcopy(doc)
    unknown["common_core_sha256"] = "1" * 64
    assert any("C7.1(6)" in p for p in attest.check(unknown))


def test_final_attestation_checks_the_contract_sha256(doc: dict) -> None:
    final = copy.deepcopy(doc)
    final["result"] = "NOT_QUALIFIED"
    final["domain_contract_sha256"] = WRONG
    assert any("C7.1(7)" in p for p in attest.check(final))
