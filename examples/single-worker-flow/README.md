# Single Worker Flow Example

This is the smallest fully validated coordination path: source pack, task card, authority charter, worker handoff, reviewer report, and final-authority-ready status.

Run:

```bash
python tools/openacp_validate.py --artifact examples/single-worker-flow/source-pack.json --ruleset source-pack --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/authority-charter.json --ruleset authority-charter --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/task-card.json --ruleset task-card --source-pack examples/single-worker-flow/source-pack.json --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/handoff.json --ruleset handoff --task-card examples/single-worker-flow/task-card.json --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/review-report.json --ruleset review-report --strict
python tools/openacp_validate.py --artifact examples/single-worker-flow/status-report.json --ruleset status-report --strict
```
