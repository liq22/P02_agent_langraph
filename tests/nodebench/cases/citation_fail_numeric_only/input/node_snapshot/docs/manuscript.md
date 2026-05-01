# Numeric Citation Only

## Problem

The problem is a proposal node that looks structurally complete while relying on numeric references only. It defines the research question, the expected reviewer concern, and the practical boundary for audit. The section is intentionally long enough to pass the structure check without using a BibTeX citekey.

## Route

This fixture demonstrates that numeric-only citations can make a draft appear grounded even when the citation registry cannot resolve a stable key [1]. The route is to keep every other validator satisfied so that the citation validator is the only blocker.

## Boundary

The boundary is explicit: a qualified paper node must expose resolvable references, not only bracketed numbers. The next action is to replace numeric markers with citekeys and a local BibTeX index before handoff.
