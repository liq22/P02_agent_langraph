# Experiment Protocol Fixture

## Dataset and Task

The dataset is a small public benchmark snapshot with fixed train, validation, and test splits. The task is fault classification from preprocessed vibration windows, where each input is one normalized window and each output is a class label. This NodeBench case is not intended to prove model quality; it only checks whether a node can expose an executable protocol shape with enough detail for a reviewer to inspect.

## Baseline and Metric

The required baseline is a deterministic feature-plus-linear-classifier pipeline. The primary metric is macro F1, and the secondary metric is accuracy. Every run must report the random seed, split identifier, preprocessing version, and evaluation command. The success criterion is not absolute performance; success means the metric can be recomputed from declared artifacts and compared against the baseline without hidden assumptions.

## Expected Artifacts and Failure Case

The expected table contains dataset, task, baseline, macro F1, accuracy, seed, and run command. The expected figure is a compact confusion matrix that reveals class-level failure modes. The failure case is explicit: if the split file, baseline command, metric definition, or output table is missing, the node stops at review and records the blocking gap. The next action is to bind the protocol to a real experiment contract.
