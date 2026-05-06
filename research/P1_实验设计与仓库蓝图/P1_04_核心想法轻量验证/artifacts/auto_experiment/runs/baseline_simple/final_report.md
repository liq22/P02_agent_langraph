# PHMGA Final Report: OTTAWA_SYNTH / ml

## Conclusion
- Dataset: OTTAWA_SYNTH
- Graph path: ml
- DAG hash: `77939d5174070d351b08929f5ee53b8ece96e928ad9cfec7f089d957976e8918`
- Nodes: 18
- Operator categories: AGGREGATE, DECISION, EXPAND, INPUT, MULTI_VARIABLE, TRANSFORM
- train: acc=1.000, macro_f1=1.000
- val: acc=1.000, macro_f1=1.000
- test: acc=0.833, macro_f1=0.829

## Protocol
- Catalog: synthetic
- Metadata schema: synth_v1
- Split sizes: train=4, val=2, test=2
- Window: size=256, stride=128, mode=sliding

## Evidence
- Manifest warnings: 0
- Artifact keys: algorithm, decision_side_outputs, feature_list, feature_pipeline, feature_separability_summary, importance, metrics, predictions, similarity_artifacts

## Workflow
- User instruction: Generate a paper-ready PHM workflow from canonical metadata.
- Plan steps: 16
- Workflow rounds: 1
- Decision side outputs: 1

## DAG Quality
- Recommendation: n/a
- Quality issues: 

## Analysis Workflow
- Front-end simple chain: signal_context -> StepPlan -> execute -> reflect -> compile -> inquirer -> report
- Simple policy: use reflection as the only loop controller; do not run dag_quality or rollback.
- Back-end hand-off: validated DAG JSON -> bridge -> graph-dependent artifacts -> final report

## Optional Similarity Artifacts
- Keys: class_centroid_similarity, class_centroids, split_sizes, test_to_train_mean_similarity
