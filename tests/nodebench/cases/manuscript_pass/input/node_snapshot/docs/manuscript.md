# Methods Fixture

## Methods and Replication

The method uses a three-stage pipeline: window normalization, compact feature extraction, and deterministic classification. Replication requires the dataset split, preprocessing version, feature list, model seed, and evaluation script. Each variable is declared before use so that a reviewer can trace how input windows become reported metrics. This fixture keeps the implementation abstract because NodeBench is testing evaluator behavior, not model performance.

## Evidence and Citation

The primary claim is that explicit method variables improve auditability; this is supported by the fixture evidence because every required variable is named and checked by the acceptance list [@nodebenchMethods]. Experimental evidence in a real node would need an artifact registry, but this benchmark demonstrates that citation and evidence markers are present [@nodebenchMethods]. The key contribution is the binding of method prose to verifier-readable outputs, as shown by the declared table and report fields [@nodebenchMethods].

## Boundary and Next Action

The boundary condition is strict: if the dataset split, random seed, or metric parser is missing, the node cannot claim replication quality. The next action is to run the same harness against a live manuscript node, inspect the blocking validator, and ask for human gate approval before any status transition. This fixture therefore shows a complete audit path while avoiding unsupported scientific claims [@nodebenchMethods].

## Reference

[@nodebenchMethods] NodeBench methods fixture.
