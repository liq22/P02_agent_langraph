# Current Final Gate Blocker Contract

generated_at: 2026-05-06

## Purpose

This artifact refreshes the P0_05 resource/risk boundary against the latest final submission validator output. It prevents stale blocker lists from being treated as current project truth.

## Latest Final-Gate Result

The current `scripts/validate_research_truth.py --require-submission` output passes in submission-ready mode:

- 0 P1_01-P1_05 acceptance checklist fields not complete;
- 0 leaf-node `overall_score` values below 90;
- 0 P3_04 revision actions with `blocked` or `planned` status.

## Repaired Legacy Blockers

The latest final-gate output no longer reports:

- parent-phase metadata/checklist/review template-marker errors;
- P1_03/P1_05/P2_02_04 claim-evidence registry schema errors;
- template-marker errors;
- failure-truth artifact errors.

These should remain in historical audit context only, not in the current blocker list.

## Retained Limitations

These remain disclosed limitations and must not be converted into positive empirical claims:

- selected global backend is not locked;
- accepted RM101 positive evidence is not locked;
- full PHMGA/Vibench adapter sample-level metadata-H5 alignment remains a final-evidence dependency;
- accepted Stage C main-result rows and Stage D ablation rows are not locked as final evidence;
- P3_04 revision actions were closed by explicit user authorization against P4_05/P4_06 coverage/retained-limitation evidence;
- distinct final-threshold re-review has raised all current score-failure-list nodes to 90 or above; no current score blocker remains.

## Guardrail

Any final-readiness statement must cite the latest validator output and the retained-limitation boundary, not older blocker lists. If the validator output changes, this contract must be refreshed before claiming that P0_05 resource/risk boundaries are current.
