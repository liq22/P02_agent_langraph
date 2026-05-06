# P0_05 Gate Report

- node_id: `research::P0_项目申请书::P0_05_项目约束_资源预算_风险边界`
- generated_at: 2026-05-05
- actor: codex-local
- round_type: resource/constraint/risk hard-gate author package
- decision: ready for independent node review, not submission-ready

## Gate Inputs Checked

| Input | Role | Current Use |
| --- | --- | --- |
| `P0_02 problem_hypothesis.yaml` | H1-H3 and falsification paths | Constraints attach to claim validity, review closure, and formal evidence eligibility. |
| `P0_03 contribution_claims.yaml` | RC1-RC4 contribution boundaries | Resource/risk plan prevents implementation details or preliminary evidence from becoming scientific claims. |
| `P0_04 okr_map.yaml` | Stages, objectives, metrics, stop conditions | P0_05 budget follows S1-S4 eligibility/review/registry gates. |
| `P0_04 risk_decision_map.yaml` | Existing route risk branches | P0_05 converts route risks into resource budgets and explicit downgrade plans. |
| `data_manifest.yaml` and `dataset_registry.yaml` | Formal dataset scope | Formal data scope is RM_017_Ottawa19 and RM_101_THU_GEARBOX; extension datasets remain extension-only. |
| `metadata_h5_alignment.json` | Alignment audit status | Current status is auditable preview; full adapter-level alignment remains a downstream preflight requirement. |
| `phmga_experiment_readiness.md` | Stage B/C/D requirements | selected backend, main rows, ablations, result_md, artifact_dir, and artifact contract are hard gates. |
| `vibench_to_phmga_boundary.md` | Responsibility boundary | Vibench reads/catalogs data; PHMGA owns protocol, split, DAG, evaluation, ledger, and tables. |

## Required Questions

| Question | Answer |
| --- | --- |
| 项目最大的资源瓶颈是什么？ | Formal evidence eligibility chain: provider/model policy, adapter alignment, artifact contract, Stage C/D rows, backend lock, registry schema, and final review threshold must all close. |
| 最可能失败的路径是什么？ | Preliminary or reject evidence is overpromoted into final paper evidence, especially synthetic/offline signal, RM101 reject rows, low review scores, or graph progression. |
| 哪些边界必须主动写清楚以避免 reviewer 误解？ | Vibench is read/catalog only; PHMGA owns formal result semantics; free-model provider policy is strict; synthetic/offline evidence is preliminary; teammate review identity is disclosed; final validator remains required. |

## Local Outputs

| Output | Status | Evidence |
| --- | --- | --- |
| 资源预算草案 | done | `docs/manuscript.md` budget table and `artifacts/constraint_risk_map.yaml:resource_budget` |
| 风险边界与降级计划 | done | `docs/manuscript.md` risk plan and `artifacts/constraint_risk_map.yaml:risk_register` |
| 不做什么的边界说明 | done | `docs/manuscript.md` do-not-do section and `artifacts/constraint_risk_map.yaml:do_not_do_boundaries` |
| `artifacts/gate_report.md` | done | this report |
| `artifacts/constraint_risk_map.yaml` | done | structured resource/risk map |

## Gate Decision

P0_05 is ready for independent review because it lists more than three major constraints/risks, gives each risk a mitigation or downgrade path, keeps proposal scope bounded, and records current global blockers instead of treating them as solved.

P0_05 does not make unsupported empirical claims. Current final submission validator facts are:

- 0 P1_01-P1_05 checklist fields are not complete;
- 0 leaf-node scores are below the final submission threshold of 90; the P0 group, P1 group, P2 group, P3 group, and P4_01-P4_07 are no longer present in the score-failure list;
- 0 P3_04 revision actions still have blocked or planned status after user-authorized retained-limitation/action-coverage closure;
- final `scripts/validate_research_truth.py --require-submission` passes in submission-ready mode.

Retained limitations that must remain visible rather than become positive claims:

- selected_global_best_backend is not locked;
- RM101 remains reject evidence, not selection-eligible positive evidence;
- full PHMGA/Vibench adapter sample-level metadata-H5 alignment remains pending;
- Stage C main-result rows and Stage D ablation rows are not passed.

Legacy parent-phase metadata, claim-evidence schema, placeholder-marker, and failure-truth validator errors have been repaired in the latest final-gate output and should not be listed as current blocker classes unless a later validator run reintroduces them.

## Handoff

Send this P0_05 package to a distinct external reviewer using `prompts/review_rubric.yaml`. The reviewer should check that budget, resources, data limits, ethics/license/provider issues, exit criteria, and downgrade paths are explicit, and that no graph/projection/preliminary evidence is treated as final research truth.
