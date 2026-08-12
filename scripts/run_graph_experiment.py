#!/usr/bin/env python3
"""Run matched reactive or B5 graph-guided PHM Agent experiments."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from phm_agent_benchmark.phase1 import Budget, LocalPaderbornDataPort, ModelProfile, OpenAICompatibleLLM
from phm_agent_benchmark.phase1.experiment import aggregate_results, attach_model_cost, load_dataset_protocol, run_rotation
from graph_phm_paper import GraphDecisionAgent, ReactivePHMAgent, evaluate_decision_states


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


async def run(args: argparse.Namespace) -> None:
    protocol = load_dataset_protocol(args.protocol)
    base_url = os.environ[args.base_url_env]
    api_key = os.environ[args.api_key_env]
    model = os.environ[args.model_env]
    agent_cls = GraphDecisionAgent if args.arm == "graph" else ReactivePHMAgent

    def factory(model_id: str):
        del model_id
        return agent_cls(
            OpenAICompatibleLLM(
                base_url=base_url,
                api_key=api_key,
                temperature=args.temperature,
                seed=args.seed,
                max_output_tokens=args.max_output_tokens_per_turn,
            ),
            model=model,
        )

    core_budget = Budget()
    monitoring_budget = Budget(max_tool_calls=72, max_window_reads=3, max_operator_calls=50, max_model_calls=3, max_llm_turns=72)
    with LocalPaderbornDataPort(args.metadata, args.signal, public_id_seed=int(protocol["agent_visibility"]["sample_handle"]["seed"])) as data:
        trajectories, records, run_info = await run_rotation(
            data,
            protocol,
            args.rotation,
            factory,
            tasks=args.tasks,
            train_samples_per_bearing=8,
            validation_samples_per_bearing=8,
            test_samples_per_bearing=(3 if args.tasks == ["online_replay_monitoring"] else 1),
            budget=core_budget,
            monitoring_budget=monitoring_budget,
        )

    profile = ModelProfile(args.provider_label, model, "openai_chat_completions", args.input_usd_per_million, args.output_usd_per_million)
    attach_model_cost(records, profile)
    state_rows = []
    for index, trajectory in enumerate(trajectories):
        state_rows.append({
            "episode_index": index,
            "task_id": trajectory["trajectory"]["task_id"],
            **evaluate_decision_states(trajectory["trajectory"]["steps"]),
        })
    args.output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(args.output / "rollout.jsonl", trajectories)
    _write_jsonl(args.output / "evaluation.jsonl", records)
    _write_jsonl(args.output / "state_evaluation.jsonl", state_rows)
    summary = aggregate_results(records)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "graph_phm_run_v0",
        "arm": "B5" if args.arm == "graph" else "reactive",
        "agent": agent_cls.__name__,
        "benchmark_protocol": protocol["schema_version"],
        "rotation": args.rotation,
        "tasks": args.tasks,
        "seed": args.seed,
        "provider_model": profile.to_dict(),
        "budget": monitoring_budget.to_dict() if args.tasks == ["online_replay_monitoring"] else core_budget.to_dict(),
        "result_status": "formal_candidate" if run_info.get("early_termination_reason") is None else "partial_failure",
        **run_info,
    }
    (args.output / "run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("reactive", "graph"), required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--signal", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--rotation", default="rotation_0")
    parser.add_argument("--tasks", nargs="+", default=["cold_start_fault_diagnosis", "unsupervised_anomaly_detection"])
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens-per-turn", type=int, default=2048)
    parser.add_argument("--provider-label", required=True)
    parser.add_argument("--input-usd-per-million", type=float, required=True)
    parser.add_argument("--output-usd-per-million", type=float, required=True)
    parser.add_argument("--base-url-env", default="LLM_BASE_URL")
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    parser.add_argument("--model-env", default="LLM_MODEL")
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
