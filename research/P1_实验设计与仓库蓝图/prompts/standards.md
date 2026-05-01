# P1 experiment and protocol standards

## Purpose

Use these checks when a P1 node designs protocol, baseline, repository structure, execution contracts, or experiment readiness.

## Standards

- Define the hypothesis before the implementation: expected signal, failure signal, and what either result would teach.
- Run baseline first. Never interpret a new method before the clean baseline and metric parser are verified.
- Change one conceptual variable per run unless the execution contract explicitly permits a bundled change.
- Bind every experiment to data, split, baseline, metric, budget, editable paths, protected paths, and rollback policy.
- Prefer cheap pilots before full campaigns. A null pilot should be allowed to kill or narrow an idea.
- Use bounded ranking or tournament logic for candidate ideas, but do not let tournament search become an unbounded global loop.
- Maintain traceability from run log to metric row to kept/discarded decision to current claim.

## Stop Or Narrow

- Stop if the metric cannot be parsed or the baseline cannot be reproduced.
- Stop before high-cost execution unless the budget, owner approval, and rollback path are explicit.
- Narrow if the proposed experiment tests several hypotheses at once.
