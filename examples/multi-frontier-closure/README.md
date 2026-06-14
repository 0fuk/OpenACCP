# Multi Frontier Closure Fixture

This strict fixture shows the minimum coordination control plane for a Frontier lane that has finished all B0/B1/B2-safe work and is ready for Primary final-authority consume.

Validate:

```bash
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/source-pack.json --ruleset source-pack --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/execution-boundary.json --ruleset execution-boundary --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/current-manifest.json --ruleset current-manifest --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/sequence-registry.json --ruleset sequence-registry --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/lane-registry.json --ruleset lane-registry --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/source-status-registry.json --ruleset source-status-registry --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/decision-registry.json --ruleset decision-registry --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/child-ledgers/frontier-docs.json --ruleset child-ledger --strict
python tools/openaccp_validate.py --artifact examples/multi-frontier-closure/frontier-closures/frontier-docs.json --ruleset frontier-closure --strict
```
