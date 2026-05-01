# Missing BibTeX Index

## Problem

The problem is a paper node that includes citekey syntax but does not provide a local reference index. Reviewers can see that a citation marker exists, but the verifier cannot resolve the key to a BibTeX entry.

## Route

This fixture demonstrates that citation syntax alone is not enough for a qualified paper node [@missingFixture]. The route records the claim, the intended reference, and the expected validator blocker while keeping the rest of the node complete.

## Boundary

The boundary is explicit: the node must add `refs.bib` or `references.bib` before it can pass. The next action is to bind the cited key to a BibTeX entry and rerun the evaluator.
