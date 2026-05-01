---
skill_id: P1_02_伪代码_local_entry
purpose: 收敛伪代码与接口契约，使后续实现与评测协议对齐。
node_mode: lite
node_profile: lite_research_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: leaf_node_writer
outputs:
- docs/manuscript.md
- artifacts/interface_contract.yaml
extra_status_updates:
- progress_pct
---

Runtime entry shim for this lite node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_02_伪代码`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
