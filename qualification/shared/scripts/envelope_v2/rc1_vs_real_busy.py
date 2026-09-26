import copy, json, sys
from importlib.metadata import version
from research_protocol import v2
busy = json.loads(open(sys.argv[1], encoding="utf-8").read())
sys.path.insert(0, sys.argv[2]); sys.path.insert(0, sys.argv[3])
import fixtures
req = fixtures.request("stocks:REQ-V2RC2-BUSY", "positive")
print("predictor-research-protocol", version("predictor-research-protocol"))
task = v2.build_task("stocks", req, proposal_id="cain:P", created_at="2026-09-26T06:00:00Z")
busy = dict(busy, submission_file="x")
try:
    v2.build_result(task, busy, adapter={"distribution": "x", "version": "0", "module": "m"}, produced_at="2026-09-26T06:00:01Z")
    print("rc1: ACEITO")
except v2.V2Error as exc:
    print("rc1: RECUSADO", exc.code)
