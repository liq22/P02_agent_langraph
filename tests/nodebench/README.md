# NodeBench

NodeBench exercises the node harness and evaluator layer. It tests whether the AutoResearch substrate can load a node snapshot, run registered validators, write reports, and return a stable pass/fail result.

Run:

```bash
python scripts/build_nodebench.py --root .
```

Reports are written to `tests/nodebench/reports/`.

Cases may include `expected.json` with `passed` and optional
`blocking_validator` fields. Expected-fail cases pass NodeBench when the
actual result matches that contract.
