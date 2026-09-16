# Real data, numerical references and local hardware

Scope: acquire and admit actual data; no dataset claim is inferred from a download page. Follow `paper/experiments/DATA_DOWNLOAD_SOP.md`. Output: schema/split notes in P02, data and model artifacts only in Benchmark/private storage. Acceptance: one real record, fixed labels/units/independent-unit split, training-only fit, checkpoint reload and saved-prediction metric reproduction.

Reuse the installed pinned factory while its upstream main is behind. With a user-reviewed factory config:

```bash
phm-data --config "$PHM_DATA_CONFIG" summary
phm-data --config "$PHM_DATA_CONFIG" datasets
# ID/channels/range come from the inspected actual record, not a guessed example.
phm-data --config "$PHM_DATA_CONFIG" window "$SAMPLE_ID" \
  --start "$START" --end "$END" --channels "$CHANNELS" --max-points "$POINTS"
```

Then use the existing Benchmark real smoke and known local metadata/signal paths. Do not replace missing files with generated sensor data. A graph policy itself is training-free; checkpoint checks apply to the frozen numerical experts or a future learned estimator.

## 8 x RTX4090, never two-card execution

The editing runtime has no GPU or private PHM data. Theory, plan and API-agent orchestration run on CPU; there is no scientific reason to reserve GPUs for them. Any GPU-dependent baseline training or local-model inference is assigned to the user's **eight-card RTX4090 host**, not a guessed two-card setup.

```bash
nvidia-smi --query-gpu=index,name,memory.total --format=csv
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
python - <<'PY'
import torch
assert torch.cuda.device_count() == 8, 'Expected eight visible GPUs; do not fall back to two'
for i in range(8):
    print(i, torch.cuda.get_device_name(i))
PY
```

This validates visibility, not a training result. The external numerical baseline trainers are not implemented in this slice, so there is no fictitious torchrun command. Once a real trainer/checkpoint protocol is admitted, use either eight independently assigned jobs (one per card, disjoint outputs) or a tested eight-process distributed job. Record global batch, seed, precision, optimizer and per-card memory. Do not change effective batch/model merely to pass memory, and do not run two cards as an automatic substitute. Missing GPU/API/data terminates the dependent goal with a concrete blocker, not the whole paper's independent work.
