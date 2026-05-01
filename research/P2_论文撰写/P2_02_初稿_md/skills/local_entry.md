---
skill_id: P2_02_初稿_md_local_entry
purpose: 协调 `P2_02_初稿_md` 子树推进，并把执行保持在子节点而不是父节点壳层。
node_mode: parent
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_action_only: true
decision_rule:
- when: 存在明确 ready 的子节点
  stop_with: route_child_first
- when: 当前父节点仅需更新协调状态
  then: keep_default_delegate
outputs:
- 初稿主线摘要
- 跨章节一致性修正建议
- artifacts/outline_map.yaml
extra_status_updates:
- progress_pct
---

Entry file for this parent node.

This entry applies to `research/P2_论文撰写/P2_02_初稿_md`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work inside the selected node and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
