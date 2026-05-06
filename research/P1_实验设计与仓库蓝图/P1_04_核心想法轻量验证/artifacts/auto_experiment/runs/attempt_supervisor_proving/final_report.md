# PHMGA Final Report: OTTAWA_SYNTH / ml

## Conclusion
- Dataset: OTTAWA_SYNTH
- Graph path: ml
- DAG hash: `019fb559630d574579f914e2574fbd27b2b8181ba9d552e6ae68f6472fe3fbd6`
- Nodes: 9
- Operator categories: AGGREGATE, INPUT, TRANSFORM
- train: acc=1.000, macro_f1=1.000
- val: acc=1.000, macro_f1=1.000
- test: acc=1.000, macro_f1=1.000

## Protocol
- Catalog: synthetic
- Metadata schema: synth_v1
- Split sizes: train=4, val=2, test=2
- Window: size=256, stride=128, mode=sliding

## Evidence
- Manifest warnings: 0
- Artifact keys: algorithm, feature_list, feature_pipeline, feature_separability_summary, importance, metrics, predictions, similarity_artifacts

## Workflow
- User instruction: Generate a paper-ready PHM workflow from canonical metadata.
- Plan steps: 7
- Workflow rounds: 0
- Decision side outputs: 0

## DAG Quality
- Recommendation: n/a
- Quality issues: 

## Analysis Workflow
- Front-end proving chain: signal_context -> StepPlan -> execute -> compile -> verify
- Proving policy: no dag_quality evaluator, no reflection loop, no rollback.
- Back-end hand-off: validated DAG JSON -> bridge -> graph-dependent artifacts -> final report

## Optional Similarity Artifacts
- Keys: class_centroid_similarity, class_centroids, split_sizes, test_to_train_mean_similarity
