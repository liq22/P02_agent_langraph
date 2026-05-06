# P2_05 Academic Expression And Claim Calibration

## Scope

This node performs a bounded prose and claim-calibration pass on the current P2 manuscript package. The source text reviewed in this round is the P2_03 TeX draft, with claim boundaries checked against the P2_03 claim-evidence registry, the P2_02_05 experiment/discussion claim map, the P2_01 venue/style requirements, and the P2_04 formal check report. The pass now records both the rewrite packet and a concrete TeX target map; high-risk and medium-risk replacements are either applied to the synchronized TeX files or marked as no-edit-needed without changing scientific claim strength.

The one-sentence contribution after calibration is: AutoResearch is presented as an evidence-governed human-agent research workflow that keeps node closure, claim identity, review gates, response coverage, negative evidence, and formal-result eligibility inspectable before manuscript claims are strengthened.

## Findings

The current draft is already conservative about empirical evidence. It states that the only quantitative signal in the draft is a preliminary synthetic/offline single-run result and that formal real-data, RM101, selected-backend, Stage C, Stage D, repeat, and final-review-threshold claims remain blocked. The main style risk is therefore not overclaiming through numbers, but the use of broad operating-system language that can make a process claim sound more established than the evidence package currently supports.

The main template-like sentence pattern is a general noun phrase followed by an abstract benefit, for example "turns manuscript production into a claim-grounded operating procedure" or "the contribution of this draft is the auditable connection." These phrases are readable but too compressed: they hide the actual mechanism, namely node-local artifacts, claim/evidence identifiers, review verdicts, response coverage, and limitation records. The replacement sentences in `artifacts/academic_expression_claim_calibration.md` make the mechanism explicit and keep the scientific meaning unchanged.

The methods section is stronger than the abstract because it names the unit of analysis, eligibility criteria, comparison conditions, and outcome measures. Its main polish need is precision around "contract" and "procedure." The revised wording defines the intervention as a documented package rather than as a broad system label, which is easier for a reviewer to audit.

The results and discussion text correctly prevents the synthetic/offline signal from becoming a formal performance claim. The only high-risk phrase is "negative as much as positive," which reads like a rhetorical contrast. The proposed replacement says directly that the result section reports both the bounded synthetic/offline signal and the retained unsupported or uncertain evidence.

## Patch-Ready Rewrite Packet

The rewrite packet contains nine local sentence or compact-passage patches. Each entry records the original sentence or passage, AI-like risk level, risk source, minimal replacement, and preserved evidence or terminology constraint. The packet is intentionally conservative: it does not add datasets, baselines, statistics, citations, or claims. It only makes the existing claim/evidence boundary more explicit. The companion `artifacts/tex_rewrite_target_map.yaml` binds every entry to a TeX file, line, anchor, application status, and no-upgrade constraint.

High-risk replacements are applied or already present for the abstract, introduction, and discussion targets. Medium-risk replacements are applied where they reduce broad labels without changing the method variables. Low-risk entries are kept as "no edit" records to show that the pass did not force unnecessary stylistic change.

## Claim And Evidence Boundary

The local claim-evidence registry for this node is `artifacts/claim_evidence_registry.yaml`. It records five claims: the scope of the style pass, the no-upgrade rule for scientific claims, the existence of the patch packet, the preservation of negative and uncertain evidence, and the continued lack of final submission readiness. The registry uses only supported or limitation claims and points to existing upstream artifacts rather than projection surfaces.

The pass preserves the current final-gate blockers without softening them: 109 pending P1_01-P1_05 checklist fields, 26 review scores below the submission threshold after the P2_04 re-review, 6 P3_04 revision actions with blocked or planned status, PHMGA/Vibench formal eligibility gaps, selected-backend and RM101 gaps, Stage C/D incompleteness, and PHMGA dirty-state protection before any future parent pointer update.

## Author Exit

P2_05 author exit is satisfied at the draft-artifact level because the node now has a prose calibration manuscript, a patch-ready rewrite packet, a TeX target/application map, synchronized high-risk edits, and a schema-shaped claim-evidence registry. Node close still depends on independent review and response coverage.
