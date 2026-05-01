# Edit Scope Violation

## Problem

The problem is a proposal node whose content passes the paper validators while the working tree contains files that are outside the allowed edit scope. The test forces NodeBench to enforce scope so the forbidden files become visible.

## Route

This fixture demonstrates that a valid paper claim can still be blocked by an invalid edit boundary [@scopeFixture]. The route keeps citation, claim support, and acceptance coverage complete while expecting the scope validator to fail.

## Boundary

The boundary is explicit: content quality does not authorize changes to protected files. The next action is to rerun the node in a clean scope or move edits into the harness-approved paths [@scopeFixture].
