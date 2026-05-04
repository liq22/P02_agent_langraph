# PHMGA Experiment Readiness

## Project readiness definition

PHMGA is project-ready only when formal paper runs produce accepted evidence rows and non-empty main tables.

## Required experiment layers

### Proving lane

Purpose: engineering qualification only.

It answers whether a basic pipeline can produce validated DAG and graph-dependent artifacts. It does not enter formal result tables.

### Simple qualification lane

Purpose: real-data runtime closure.

It is useful for diagnosing environment and closure issues but does not enter formal main tables.

### Stage B backend comparison

Purpose: select a backend for formal runs.

Required rows:

```text
ottawa_ml_codex_v3
ottawa_ml_openrouter_glm_v2
ottawa_ml_bigmodel_glm47_v1
rm101_ml_codex_v3
rm101_ml_openrouter_glm_v2
rm101_ml_bigmodel_glm47_v1
```

A row is selection-eligible only if:

```text
keep=accept
artifact_contract_pass=pass
feature_separability_pass=pass
result_md exists
artifact_dir exists
```

### Stage C main results

Run after `selected_global_best_backend` is selected:

```text
ottawa_ml_main_v1
ottawa_torch_main_v1
rm101_ml_main_v1
rm101_torch_main_v1
```

### Stage D minimum ablations

Minimum submission ablations:

```text
ottawa_ml_intermediate_v1
rm101_ml_intermediate_v1
ottawa_torch_module_runtime_v1
rm101_torch_module_runtime_v1
```

## Hard blockers

- `selected_global_best_backend` remains pending.
- `doc/experiments/02_main_tables.md` has no passed rows.
- A main table row has no `result_md`.
- A main table row has no `artifact_dir`.
- A formal row fails artifact contract.
