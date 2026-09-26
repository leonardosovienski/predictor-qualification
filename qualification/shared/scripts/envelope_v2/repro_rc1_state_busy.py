"""Reprodução (rc1): outcome STATE_BUSY_RETRYABLE do stocks sem client_ref, como o runner do
stocks-predictor 61fc017 (research_runner.py, submit_request, except sqlite3.OperationalError na
admission) o monta: request_id None, sem client_ref, exit 3."""
import copy, sys
sys.path.insert(0, sys.argv[1])
from vectors import REQUESTS
from research_protocol import v2
from importlib.metadata import version
print("predictor-research-protocol", version("predictor-research-protocol"))
task = v2.build_task("stocks", copy.deepcopy(REQUESTS["stocks"]), proposal_id="cain:P", created_at="2026-09-26T00:00:00Z")
outcome = {"schema": "stocks-research-outcome/1", "submission_file": "adapter", "submission_sha256": "f"*64,
           "at": "2026-09-26T00:00:01Z", "request_id": None, "status": "STATE_BUSY_RETRYABLE",
           "reason": "SQLITE_BUSY", "detail": "database is locked", "exit_code": 3}
try:
    r = v2.build_result(task, outcome, adapter={"distribution": "x", "version": "0", "module": "m"}, produced_at="2026-09-26T00:00:02Z")
    print("ACEITO", r["outcome"])
except v2.V2Error as exc:
    print("RECUSADO", exc.code, str(exc))
