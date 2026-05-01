---
skill_id: P2_论文撰写_local_entry
purpose: 协调 `P2_论文撰写` 子树推进，并把执行保持在子节点而不是父节点壳层。
node_mode: parent
node_profile: routing_parent
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
- prompts/standards.md
default_delegate:
  local_action_only: true
decision_rule:
- when: 存在明确 ready 的子节点
  stop_with: route_child_first
- when: 当前父节点仅需更新协调状态
  then: keep_default_delegate
extra_status_updates:
- progress_pct
---

Runtime entry shim for this parent node.

This shim applies to `research/P2_论文撰写`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `prompts/standards.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
