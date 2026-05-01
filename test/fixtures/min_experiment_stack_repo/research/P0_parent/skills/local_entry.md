---
skill_id: P0_parent_local_entry
purpose: Fixture parent scope.
default_delegate:
  local_action_only: true
---

Runtime entry shim for this node-local research stack.

This shim applies to `research/P0_parent`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
