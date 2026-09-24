"""brasileirao: gate → testes da suíte de conformidade, com o resultado lido do junit bruto (C20).

Uso: python gate_tests.py --junit <label>=<conformance.junit.xml> ... --out <json>
Cada gate lista os testes (prefixo de nome) que o provam; o script conta, por ambiente, quantos
casos rodaram, passaram, falharam, deram erro ou foram pulados. Gate com qualquer caso não
passado em qualquer ambiente = não verde.
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

GATES = {
    "E2E": ["test_e2e_file_request_to_result_and_reread_after_restart", "test_forecast_only_for_future_events_makes_no_scientific_claim",
            "test_entrypoint_needs_no_checkout_or_project_root", "test_ou25_is_evaluated_against_the_canonical_closing_line"],
    "PROVENANCE": ["test_e2e_file_request_to_result_and_reread_after_restart"],
    "ADMISSION": ["test_admission_rejects_before_any_execution", "test_invalid_json_duplicate_keys_nan_and_oversize_are_rejected"],
    "IDEMPOTENCY": ["test_idempotency_duplicate_conflict_and_single_effect", "test_duplicate_after_policy_change_returns_the_stored_result",
                    "test_concurrent_submissions_of_the_same_request_produce_one_effect", "test_out_of_order_requests_are_independent_and_deterministic"],
    "RESTART_RECOVERY": ["test_process_death_at_each_point_recovers_exactly_once", "test_backup_and_restore_into_a_new_root_reread_the_same_result"],
    "FAILURE_INJECTION": ["test_process_death_at_each_point_recovers_exactly_once", "test_ops_worker_crash_is_not_a_result_and_retry_succeeds",
                          "test_ops_timeout_kills_the_worker_and_is_not_a_result", "test_slow_worker_still_produces_exactly_one_result",
                          "test_retry_budget_exhaustion_is_a_terminal_operational_failure", "test_ops_lock_held_by_another_run_is_retryable_never_a_second_effect",
                          "test_database_lock_waits_and_then_completes_once", "test_db_says_result_exists_but_file_is_gone",
                          "test_file_exists_but_index_lost_the_result", "test_modified_result_and_modified_effect_fail_closed",
                          "test_corrupted_dataset_snapshot_in_the_object_store_fails_before_ops", "test_missing_reference_object_is_not_ready",
                          "test_reference_changed_after_materialization_fails_closed", "test_fault_points_are_the_frozen_matrix"],
    "AUTHORITY_SEPARATION": ["test_authority_separation_invariants_are_enforced_by_the_contract", "test_ops_worker_crash_is_not_a_result_and_retry_succeeds",
                             "test_retry_budget_exhaustion_is_a_terminal_operational_failure"],
    "CAPITAL_FORBIDDEN": ["test_capital_is_forbidden_everywhere", "test_economic_decision_code_is_not_reachable_from_the_research_entrypoint"],
    "FUTURE_CANARY": ["test_future_canary_never_reaches_any_artifact"],
    "TEMPORAL_INTEGRITY": ["test_every_prediction_uses_only_information_available_before_its_cutoff",
                           "test_handler_reads_only_the_captured_snapshot_not_the_live_database", "test_data_cutoff_after_the_snapshot_as_of_is_refused"],
    "BR_KICKOFF_ORDERING": ["test_postponed_and_rescheduled_match_is_ordered_by_its_real_kickoff", "test_duplicate_fixture_fails_closed",
                            "test_metamorphic_row_order_permutations_do_not_change_results", "test_match_still_in_progress_is_not_information_for_the_next_kickoff"],
    "BR_TIMEZONE_INTEGRITY": ["test_venue_offsets_normalize_to_the_same_instants", "test_naive_kickoff_in_the_dataset_fails_closed",
                              "test_explicit_offsets_are_normalized_never_guessed", "test_ambiguous_nonexistent_or_naive_local_times_are_rejected"],
    "BR_METAMORPHIC": ["test_metamorphic_row_order_permutations_do_not_change_results"],
    "BR_SAME_KICKOFF_ISOLATION": ["test_result_of_game_a_does_not_affect_game_b_with_the_same_kickoff",
                                  "test_match_still_in_progress_is_not_information_for_the_next_kickoff"],
    "BR_CACHE_STATE": ["test_capture_time_caches_are_never_read", "test_historical_prediction_is_the_same_after_running_a_future_date",
                       "test_same_process_memo_does_not_leak_a_future_refit"],
    "BR_FUTURE_INJECTION": ["test_result_that_could_not_exist_at_capture_fails_closed", "test_data_cutoff_after_the_snapshot_as_of_is_refused"],
    "DOMAIN_CONTRACT (adapter_paths)": ["test_entrypoints_include_the_research_circuit", "test_no_entrypoint_reaches_envelope_cain_or_adapter_paths",
                                        "test_nothing_outside_adapter_paths_imports_them", "test_research_circuit_components_are_reachable_from_the_entrypoint",
                                        "test_runtime_import_of_the_circuit_loads_no_forbidden_module"],
}


def cases(path: Path) -> dict[str, str]:
    out = {}
    for tc in ET.parse(path).getroot().iter("testcase"):
        state = "passed"
        if tc.find("failure") is not None:
            state = "failed"
        elif tc.find("error") is not None:
            state = "error"
        elif tc.find("skipped") is not None:
            state = "skipped"
        out[tc.get("name")] = state
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", action="append", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    envs = {label: (Path(path), cases(Path(path))) for label, path in (item.split("=", 1) for item in args.junit)}
    report = {"sources": {label: path.as_posix() for label, (path, _c) in envs.items()}, "gates": {}}
    for gate, prefixes in GATES.items():
        entry = {}
        for label, (_path, results) in envs.items():
            matched = {name: state for name, state in results.items() if any(name == p or name.startswith(p + "[") for p in prefixes)}
            counts = {s: sum(1 for v in matched.values() if v == s) for s in ("passed", "failed", "error", "skipped")}
            missing = [p for p in prefixes if not any(n == p or n.startswith(p + "[") for n in matched)]
            entry[label] = {"cases": len(matched), **counts, "missing_tests": missing,
                            "green": bool(matched) and counts["passed"] == len(matched) and not missing}
        report["gates"][gate] = entry
    report["all_green"] = all(e["green"] for g in report["gates"].values() for e in g.values())
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for gate, entry in report["gates"].items():
        print(gate, {k: f"{v['passed']}/{v['cases']}" + ("" if v["green"] else " NOT GREEN") for k, v in entry.items()})


if __name__ == "__main__":
    main()
