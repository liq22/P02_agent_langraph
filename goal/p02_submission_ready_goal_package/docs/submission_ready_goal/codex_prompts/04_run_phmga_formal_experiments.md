# Codex Prompt: Run PHMGA Formal Experiments

```text
/goal
Advance PHMGA formal paper experiments from pending to evidence-backed rows.

Preconditions:
- DATA_ROOT audited.
- Vibench read bundles exist for Ottawa and RM101.
- PHMGA handoff/preflight passes.

Stage B required rows:
- ottawa_ml_codex_v3
- ottawa_ml_openrouter_glm_v2
- ottawa_ml_bigmodel_glm47_v1
- rm101_ml_codex_v3
- rm101_ml_openrouter_glm_v2
- rm101_ml_bigmodel_glm47_v1

After Stage B:
- Update result_md for each executed row.
- Update result ledger only for executed rows.
- Do not mark keep=accept unless artifact_contract_pass and feature_separability_pass are pass.
- Select selected_global_best_backend only if a backend is eligible on both Ottawa and RM101.

Stage C after selection:
- ottawa_ml_main_v1
- ottawa_torch_main_v1
- rm101_ml_main_v1
- rm101_torch_main_v1

Minimum Stage D:
- ottawa_ml_intermediate_v1
- rm101_ml_intermediate_v1
- ottawa_torch_module_runtime_v1
- rm101_torch_module_runtime_v1

Update main tables only with passed rows.
```
