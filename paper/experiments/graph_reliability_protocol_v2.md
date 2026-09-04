# Graph P2-E9 repeated-run reliability protocol v2

**Status:** Generic-base dedicated runner ready; formal launch gated

**Machine-readable authority:** `graph_reliability_protocol_v2.yaml`

This protocol replaces the retired PHMskills-base v1 shell. The matched
control is `reactive-sequential-agent` with control identity
`benchmark_generic_llm_tool_agent_v1`; the treatment is
`graph-decision-agent`. Both are bound to `p2_graph_vs_generic_llm_v1`.

The registered extension remains ten new seeds by eight public replay
sequences by two arms: 80 matched pairs and 160 assigned episodes. Every
non-provider terminal remains in its denominator. Provider errors are retained
as immutable attempts and leave a unit incomplete until one later same-profile
non-provider terminal exists. The result is reported alongside, never pooled
with, the three-seed primary.

Before any formal execution or result, the endpoint authority was corrected to
match `CORE.md`: target-adverse replay `task.average_precision` is primary.
Within each repeat, AP is recomputed once over all 24 assigned windows from the
registered private DataPort assignment and the canonical successful submit
prefix in `rollout.jsonl`; the ten repeat-level AP values are then equally
weighted. Per-sequence AP averaging is forbidden. Missing windows remain in the
population under `phase1_replay_target_adverse_missing_score_v1`. Grounded
pass@1 and pass-all-10 remain explanatory rollout-reliability diagnostics.

The provider-free scheduler is safe to inspect:

```bash
python scripts/schedule_graph_reliability.py schedule \
  --output-root /path/to/isolated/reliability/root
```

It emits 160 deterministic unit commands and an explicit runner-readiness
report, but never invokes a command, imports a provider client, reads provider
environment values, or authorizes execution. Each command goes through
`run_graph_reliability_v2.py`, which binds the registered repeat seed, Generic
control/treatment identity, active dynamic protocol, public sequence, horizon
3, explicit token prices, and isolated profile root before delegating one unit
to the shared dynamic runner.

One emitted unit can be checked without provider access or filesystem writes by
appending `--validate-only`. Normal wrapper execution is provider-bound and is
therefore still subject to the Root-owned probe/quota gate; scheduler output by
itself is not launch authorization.

Acceptance and analysis remain independently provider-free and fail closed:

```bash
python scripts/schedule_graph_reliability.py accept \
  --output-root /path/to/isolated/reliability/root \
  --output /path/to/acceptance.json

python scripts/analyze_graph_reliability.py \
  --output-root /path/to/isolated/reliability/root \
  --acceptance /path/to/acceptance.json \
  --private-metadata-env PHM_PRIVATE_METADATA \
  --private-signal-env PHM_PRIVATE_SIGNAL \
  --output /path/to/result.json
```

They accept only a complete v2 exact-six cohort with the frozen Generic-base
identities. The analyzer independently rebuilds the horizon-3 private targets
through the registered Paderborn DataPort and never treats derived
`evaluation.jsonl` rows as target or prediction authority. The superseded v1
protocol and every v1 run root are rejected. No reliability, cost, or
Graph-effect claim exists from the schedule or gate mechanics alone.

The accepted-result consumer binds `formal_acceptance.json`,
`formal_result.json`, its table, SVG, and active manuscript to the paths in the
machine-readable protocol. The result `output_root` must equal the canonical
protocol `formal_root`, and every displayed interval reports its valid/2,000
bootstrap count. The consumer requires lexical and resolved source
containment, rejects input/output aliases and publication under input roots,
and accepts an existing output only as an ordinary single-link regular file.
Its production CLI accepts only this protocol, and every resolved output
remains inside the repository. After complete accepted evidence passes its
independent arithmetic checks, it stages and fsyncs all three outputs,
preserves file modes, and reverse-rolls back replacement failures. Its 20/20
focused checks cover provenance, path identity and containment, staging
cleanup, rollback, idempotence, and the registered reliability calculations.
