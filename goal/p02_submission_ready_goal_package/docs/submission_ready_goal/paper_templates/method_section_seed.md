# Method Section Seed

## Data reading boundary

We separate data reading from graph-guided PHM reasoning. PHM-Vibench data_factory is used as the data reading and catalog interface. It loads metadata, resolves dataset readers, accesses H5/raw signal files, and produces read bundles. After this read-only stage, PHMGA constructs the canonical DatasetProtocol, performs split-before-windowing, normalizes signal layout, and executes the graph-guided workflow.

## PHMGA workflow

The PHMGA mainline follows:

```text
protocol -> PHMState/StateGraph -> plan_agent -> execute_agent -> dag_quality_evaluator -> reflect_agent -> validated DAG JSON -> bridge -> graph-dependent artifacts -> inquirer_agent -> report_agent
```

## Evidence generation

Every formal result must write artifact bundles and ledger rows before entering paper tables.
