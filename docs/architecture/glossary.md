# Glossary

This glossary defines the small set of terms that the repo uses as operating
language. User-facing docs should link here instead of redefining these terms.

- `node`: a folder-backed research unit under `research/`.
- `graph`: scheduler files under `backend/graph/`; these files choose work order and do not store research content.
- `skill`: a procedure contract that tells an agent what to read, write, and stop on.
- `worker`: a skill that performs one selected task after a node has been chosen.
- `contract`: an explicit input/output agreement, usually for execution work.
- `projection`: a generated view that can be rebuilt from source files.
- `gate`: a named check that can stop progress; its trigger and owner must be explicit.
- `canonical source`: the file that owns a specific repository fact or decision.
- `local_entry`: the selected node's entry file; it chooses the next local read and delegate.
- `local_wrapper`: a node-local IO binder used when a worker needs a narrower input/output adapter.
- `local_execution`: a node-local execution binder used when an execution node has a declared run path.
- `node_mode`: registry field that controls local stack depth: `parent`, `lite`, `standard`, or `execution`.
- `node_profile`: registry field that adds research-role guidance for validation and generated views.
- `execution_profile`: registry field that distinguishes execution nodes such as experiment execution or result synthesis.

Completion words:

- `ready`: the node can be scheduled.
- `done`: the selected node has met its local acceptance checklist.
- `pass`: one named check passed.
- `submission-ready`: the final submission check passed.
- `framework healthy`: maintenance checks passed; the paper may still be incomplete.
