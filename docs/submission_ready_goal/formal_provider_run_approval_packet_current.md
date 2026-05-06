# Formal Provider Run Approval Packet

- generated_at: 2026-05-05
- generated_by: codex-local
- scope: PHMGA Ottawa/RM101 formal provider rows only
- status: approval packet prepared; no provider call executed by this packet

## Boundary

This packet records the exact external-run boundary before any formal provider call.

- It does not read `.env`.
- It does not print API keys.
- It does not run OpenRouter or BIGMODEL calls.
- It does not change review scores, checklist states, or PHMGA ledger rows.

Formal PHMGA provider runs can send real-data-derived workflow context to the selected provider. This may include dataset identifiers, metadata-derived task context, prompt/planning context, feature and run summaries, artifact-validation context, and model/provider metadata. It must not intentionally send raw API keys, local `.env` contents, private tokens, unrelated repository files, or protected human-only files.

## User Model Policy

| Provider | Allowed model policy | Active row model |
| --- | --- | --- |
| OpenRouter | free models only | `z-ai/glm-4.5-air:free` |
| BIGMODEL | GLM-4.7-flash free model only | `glm-4.7-flash` |

OpenRouter Nemotron free rows exist in the PHMGA ledger, but this packet's planned run set is limited to the active GLM/free rows unless a later instruction expands the candidate set.

## Candidate Rows

| Dataset | Provider | Run preset | Config path | Key env |
| --- | --- | --- | --- | --- |
| Ottawa | OpenRouter | `ottawa_ml_openrouter_glm_v2` | `config/runs/ottawa_ml_openrouter_glm_v2.yaml` | `OPENROUTER_API_KEY` |
| RM101 | OpenRouter | `rm101_ml_openrouter_glm_v2` | `config/runs/rm101_ml_openrouter_glm_v2.yaml` | `OPENROUTER_API_KEY` |
| Ottawa | BIGMODEL | `ottawa_ml_bigmodel_glm47_v1` | `config/runs/ottawa_ml_bigmodel_glm47_v1.yaml` | `BIGMODEL_API_KEY` |
| RM101 | BIGMODEL | `rm101_ml_bigmodel_glm47_v1` | `config/runs/rm101_ml_bigmodel_glm47_v1.yaml` | `BIGMODEL_API_KEY` |

## Command Plan

Run from the PHMGA submodule:

```bash
cd research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
```

If environment variables are not already exported in the shell, load them without printing values:

```bash
set -a
. /mnt/k/2_work/lqql_os/lqql_06_工作与项目/03_论文流水线/p02_agent_langraph/.env
set +a
```

OpenRouter preflights and formal runs:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy python main.py runtime.action=preflight +runs=ottawa_ml_openrouter_glm_v2
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy python main.py +runs=ottawa_ml_openrouter_glm_v2
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy python main.py runtime.action=preflight +runs=rm101_ml_openrouter_glm_v2
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy python main.py +runs=rm101_ml_openrouter_glm_v2
```

BIGMODEL preflights and formal runs:

```bash
python main.py runtime.action=preflight +runs=ottawa_ml_bigmodel_glm47_v1
python main.py +runs=ottawa_ml_bigmodel_glm47_v1
python main.py runtime.action=preflight +runs=rm101_ml_bigmodel_glm47_v1
python main.py +runs=rm101_ml_bigmodel_glm47_v1
```

## Acceptance Criteria

A formal row can be considered accepted only when all of these are true:

- provider/model matches the policy above;
- process exits successfully or the failure is recorded as reject evidence;
- artifact contract check passes;
- feature-separability or equivalent result-quality gate passes where configured;
- run outputs are written under the configured `artifacts/paper/...` path;
- `doc/experiments/01_result_ledger.md` and the relevant handoff/result markdown are updated with keep/reject, artifact path, provider/model, and failure reason where applicable;
- no key value appears in logs or committed artifacts.

## Stop Conditions

Stop and record reject evidence instead of retrying blindly if any of these occur:

- provider returns rate-limit, auth, payment, non-free-model, or transport errors;
- config resolves to a non-free OpenRouter model or non-`glm-4.7-flash` BIGMODEL model;
- expected artifact directory is absent or incomplete;
- artifact contract fails;
- feature-quality gate fails;
- logs or outputs appear to include secret values.

## Provider Approval Text Still Required By Tool Policy

The P1_01-P1_05 checklist closure and user-authorized P3_04 action closure have been completed; the final validator passes in submission-ready mode. Real provider calls remain a separate optional evidence-strengthening path because they disclose real-data-derived workflow context.

Use this exact text when approving real provider calls that disclose real-data-derived workflow context:

```text
批准将 RM101/Ottawa formal provider runs 的真实数据派生 workflow context 发送给 OpenRouter/BIGMODEL 服务，仅使用免费模型策略。
```
