---
skill_id: P0_01_done_local_entry
purpose: Fixture completed leaf.
default_delegate:
  canonical_global_skill: leaf_node_writer
---

Runtime entry shim for this node-local research stack.

This shim applies to `research/P0_parent/P0_01_done`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
