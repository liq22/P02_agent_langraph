# Sync and dependency gate

Scope: read existing worktrees and PRs; never overwrite local work. Output: one concise continuation record containing actual source branches, installed methods and dependency decision. Acceptance: imports and the existing method/runtime tests pass on the exact pending migration, followed by a real episode. Leaf tests do not satisfy this gate.

In the Benchmark checkout:

```bash
git status --short
git worktree list
git fetch origin
# Switch/pull only after reconciling existing local work; do not auto-stash or reset.
python main.py --config configs/paper02_graph/components.yaml
python -m unittest discover -v -s experiments/graph_control/tests
```

The `main.py` command is a plan, not inference. Run the existing migration and runtime tests from their actual paths in this checkout before treating the merged method as validated. Record the first real failure; fix only its direct cause.

## Factory is not currently fast-forwardable to main

The existing gitlink is `58050716383e32ca79fdad0d9a45ad96a19eb838`; fetched main is `458fb013b1da6101c7f8c0bc45cd0e95fed7dd59`. GitHub comparison reports main **behind by 5**, with main itself as merge base. No pointer was changed. Main membership alone also does not prove an accepted tested release.

```bash
cd src/phm_data_factory
git status --short
git fetch origin
if ! git merge-base --is-ancestor HEAD origin/main; then
  echo 'STOP: main is not an accepted descendant of the pinned dependency' >&2
  exit 2
fi
# Only after upstream acceptance and a clean worktree:
git merge --ff-only origin/main
python -m pip install -e '.[yaml,agent,legacy]'
```

Do not execute the install/merge path by bypassing the ancestry failure. Once an actual descendant is accepted, perform the factory summary/window read, Benchmark smoke, fixed labels/split, checkpoint reload and metric reproduction in Goal03. Only then commit the parent pointer with the observed results. Do not downgrade the current dependency or modify factory core to force compatibility. While blocked, the independently executable toy and manuscript work continue.
