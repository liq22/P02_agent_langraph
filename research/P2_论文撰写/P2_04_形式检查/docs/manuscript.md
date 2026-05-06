# Formal Check Summary

This node performs a bounded formal check of the current manuscript package against the selected Elsevier/IEEE-style working profile, the synchronized TeX draft, the citation registry, the workflow figure manifest, and known submission blockers. It does not rewrite the scientific content and does not claim submission readiness.

The current package has the expected article skeleton: title, abstract, introduction, preliminaries, methods, results, discussion, data availability, code availability, and references. The workflow figure has deterministic provenance, claim and evidence references, first callout, accepted node-local status, and an explicit boundary that it is a schematic rather than empirical evidence. The citation registry exists and uses method/reporting references rather than unsupported core scientific citations.

The formal gate is not submission-passing. The current final validator fails on three explicit classes: 109 pending P1_01-P1_05 checklist fields, 27 below-threshold review scores, and 6 P3_04 revision actions with `blocked` or `planned` status. Goal-level blockers also remain for selected-backend lock, RM101 reject evidence, PHMGA dirty worktree protection, PHMGA/Vibench metadata-H5 adapter preflight, and incomplete Stage C/D formal rows. These are retained as blocking gaps rather than hidden formatting issues.

See `artifacts/formal_check_report.md` for the ordered formal check, `artifacts/current_final_gate_trace.yaml` for the current validator trace, and `artifacts/gate_report.md` for gate inputs, hard blocks, and advisory issues.
