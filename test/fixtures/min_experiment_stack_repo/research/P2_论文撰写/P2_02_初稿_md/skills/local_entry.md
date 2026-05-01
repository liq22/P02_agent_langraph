---
skill_id: P2_02_初稿_md_local_entry
purpose: Fixture manuscript scope.
default_delegate:
  canonical_global_skill: manuscript_worker
---

Runtime entry shim for this node-local research stack.

This shim applies to `research/P2_论文撰写/P2_02_初稿_md`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
