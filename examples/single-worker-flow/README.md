# Single Worker Flow Example

This is the minimum OpenACCP package for one bounded worker task. It contains nine artifacts: source pack, task card, authority charter, worker handoff, review report, consume result, status report, machine summary, and formal report.

Run:

```bash
python tools/openaccp_validate.py --artifact examples/single-worker-flow/source-pack.json --ruleset source-pack --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/authority-charter.json --ruleset authority-charter --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/task-card.json --ruleset task-card --source-pack examples/single-worker-flow/source-pack.json --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/handoff.json --ruleset handoff --task-card examples/single-worker-flow/task-card.json --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/review-report.json --ruleset review-report --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/consume-result.json --ruleset consume-result --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/status-report.json --ruleset status-report --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/machine-summary.json --ruleset machine-summary --strict
python tools/openaccp_validate.py --artifact examples/single-worker-flow/formal-report-example.md --ruleset formal-report --strict
```
