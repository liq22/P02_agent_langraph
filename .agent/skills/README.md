# Skills Map

Most users should not choose among every skill in this directory. Use one public entry for a normal run, then let the selected node and its `skills/local_entry.md` decide the bounded handoff.

## Public Entry Policy

Use `graph_driven_research_orchestrator` when the next node is not already selected. It reads the scheduler graph, enters exactly one node, follows that node's local entry file, allows one delegated step, refreshes the scheduler graph, and stops.

Use a different entry only when the user has already narrowed the request:

- Broad task but unclear scope: use the broad prompt adapter.
- Existing material to place into P0-P4 or a specific node: use material intake.
- Explicit hands-off repeated progression: use the autonomous lane.
- System prompt/skill/validator optimization: use the system optimizer.
- Completed topic or node retrospective to system update queue: use the patch curator.

The older P0-only intake name, `p0_research_intake`, is not active. Its role is replaced by the material-intake entry below, which supports P0-P4 or an explicit target node.

## Runtime Chain

```text
public router
-> graph_status.next_node
-> selected node README/status/local_entry
-> optional local wrapper or local execution
-> one canonical worker or helper
-> node-local docs/artifacts/logs/review/status
-> scheduler graph refresh
```

Keep the ownership boundary simple:

- The graph decides which node is next.
- The selected node's `local_entry.md` decides how to enter that node.
- A worker or helper does one bounded job.
- The node acceptance checklist decides completion.

## Skill Index

| Skill | Role | Use |
| --- | --- | --- |
| `graph_driven_research_orchestrator` | public entry | Choose the next graph node and run one bounded routing round. |
| `auto_research_campaign` | entry adapter | Resolve a broad user prompt into one node-local or worker step. |
| `research_material_intake` | entry adapter | Record user material into a phase or explicit node without forcing P0. |
| `autonomous_research_lane` | lane | Repeat bounded graph-led rounds only when hands-off progression is explicit. |
| `autoresearch-system-optimizer` | lane | Evaluate and improve this research system's prompts, skills, and validators. |
| `system_update_patch_curator` | lane | Curate completed-topic retrospectives into reviewable system update patch queues. |
| `idea_discovery_or_problem_formulation` | P0 worker | Formulate research questions, gaps, hypotheses, and scope boundaries. |
| `experiment_design_or_execution` | P1 worker | Prepare experiment design, protocols, contracts, and validation plans. |
| `auto_experiment_worker` | P1 execution worker | Run a bounded experiment only after an executable contract is selected. |
| `manuscript_worker` | P2 worker | Draft or revise one manuscript node. |
| `paper_figure` | P2 helper | Plan or refine figure mappings and captions from local evidence. |
| `draft_export_sync` | P2/P4 helper | Sync node drafts into declared export targets. |
| `deai_cn_skill` | P2 profile worker | Patch Chinese doctoral prose to reduce AI-like style. |
| `auto_review_loop` | P3 worker | Advance one simulated review or revision-planning round. |
| `external_node_reviewer` | P3 helper | Independently review one node and write the review verdict. |
| `aggregate_reviews` | P3/P4 helper | Aggregate node-local review or critique files into a compact digest. |
| `response_worker` | P4 worker | Draft or refine one point-to-point response node. |
| `response_coverage_check` | P4 helper | Check whether response mappings cover the target comments and evidence. |
| `citation_verifier` | cross-cutting helper | Verify citation facts and claim support inside one node. |
| `result_to_claim` | cross-cutting helper | Align local results with claims and missing evidence. |
| `structured_map_builder` | cross-cutting helper | Build compact node-local maps, matrices, registries, or digests. |
| `leaf_node_writer` | cross-cutting helper | Write or refine one lightweight leaf node when no specialized worker fits. |
| `karpathy-skills` | operator profile | Apply conservative coding and review behavior guidelines. |

## Rules For Adding Or Using Skills

- Do not add a new global skill when a node-local `skills/local_entry.md` can route to an existing worker.
- Do not call helpers directly from a repo-level prompt unless a selected node and concrete local input are already known.
- Do not let generated graph, Canvas, dashboard, or UI projections become a second source for worker choice.
- Keep new public entry points rare; prefer documenting how existing entries delegate.
