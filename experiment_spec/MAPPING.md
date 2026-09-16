# Paper 2 → Benchmark mapping

All executable work remains in `liq22/phm-agent-benchmark`. Its `python main.py --config <path>` defaults to plan; `--override command=run` performs the declared experiment and `command=finish` runs the shared statistics/plots. These mapping names do not relabel historical P2-E* experiments.

| Mapping | Question / estimand | Compared conditions | Benchmark implementation / config | Evidence boundary |
|---|---|---|---|---|
| G-main | Joint Graph effect | Generic vs original cue+filter | `src/phm_graph_agent/{agent,state}.py`; `configs/paper02_graph/main.yaml` | Not a pure topology effect |
| G-components | Cue, filtering, interaction | Four cells with identical history sanitation | `components.py`; `components.yaml` | Original Generic is not the factorial control |
| G-relevance | Stage identities beyond tool count | `factorial-filter` vs `factorial-cardinality` | `cardinality_control.py`, existing component factory; `mask_relevance.yaml`; `run.sh relevance` | Count/termination match at a common history; native and real PHM validation pending |
| G-memory | Persistence activation/effect | Graph vs Graph-no-memory | `state.py`; `memory.yaml` | Check reachable behavior; base may be a null manipulation |
| G-horizon | Length/sampling/resource sensitivity | Window counts | `horizon.yaml` | Current selector is not nested-prefix pure horizon |
| G-dynamic | Revision after public condition events | Matched policies with the same public events | Migrated state rules; unified event/assignment dispatch pending | No resurrection of the old independent Runner |
| G-extension | External transport/reliability | Within-domain matched controls | Dataset/task/SOTA bindings pending | Mock state coverage is not real task evidence |

Theory04–05 use the retained exact value/support calculations under Benchmark `experiments/graph_control`. Theory06 adds full subset enumeration through `run.sh cardinality`. These exact results are not Agent attempts or numerical classifier checkpoints. New 63-mask/six-summary data are in `results/graph_control/cardinality_20260916` and support main Section 7.3.

Real episodes use the existing six-file attempt bundle, shared metrics/effects CSV and figure source. P02 stores scientific interpretation and locations, never a second raw-result tree. Preserve base versus dynamic, cue versus filtering, public condition changes versus inferred fault onset. No relocation or source test establishes a new task effect.
