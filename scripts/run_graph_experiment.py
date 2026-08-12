#!/usr/bin/env python3
"""Run matched reactive or B5 graph policy through the benchmark RunBundle."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from phm_agent_benchmark.core_v0 import RunManifestV0, write_phase1_run_bundle
from phm_agent_benchmark.phase1 import (
    Budget,
    LocalPaderbornDataPort,
    ModelProfile,
    OpenAICompatibleLLM,
)
from phm_agent_benchmark.phase1.experiment import (
    aggregate_results,
    attach_model_cost,
    load_dataset_protocol,
    run_rotation,
)
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

    frozen = protocol["episode_sampling"]
    monitoring = args.tasks == ["online_replay_monitoring"]
    test_samples = (
        int(frozen["monitoring_windows_per_episode"])
        if monitoring
        else int(frozen["agent_test_samples_per_bearing"])
    )
    core_budget = Budget()
    monitoring_budget = Budget(
        max_tool_calls=72,
        max_window_reads=test_samples,
        max_operator_calls=50,
        max_model_calls=test_samples,
        max_llm_turns=72,
    )
    with LocalPaderbornDataPort(
        args.metadata,
        args.signal,
        public_id_seed=int(protocol["agent_visibility"]["sample_handle"]["seed"]),
    ) as data:
        trajectories, records, run_info = await run_rotation(
            data,
            protocol,
            args.rotation,
            factory,
            tasks=args.tasks,
            train_samples_per_bearing=int(frozen["train_samples_per_bearing"]),
            validation_samples_per_bearing=int(
                frozen["healthy_validation_samples_per_bearing"]
            ),
            test_samples_per_bearing=test_samples,
            budget=core_budget,
            monitoring_budget=monitoring_budget,
        )

    profile = ModelProfile(
        args.provider_label,
        model,
        "openai_chat_completions",
        args.input_usd_per_million,
        args.output_usd_per_million,
    )
    attach_model_cost(records, profile)
    summary = aggregate_results(records)
    status = (
        "partial_failure"
        if run_info.get("early_termination_reason") is not None
        else "evaluated"
    )
    arm_id = "B5" if args.arm == "graph" else "reactive"
    manifest = RunManifestV0(
        run_id=f"{arm_id}-{args.rotation}-seed-{args.seed}",
        benchmark_version="0.2.0a0",
        agent_id=agent_cls.agent_id,
        task_ids=tuple(args.tasks),
        dataset_protocol=str(protocol["schema_version"]),
        split_protocol=str(protocol["split"]["strategy"]),
        seed=args.seed,
        provider=profile.provider,
        provider_model_id=profile.model_id,
        inference_protocol=profile.protocol,
        status=status,
        metadata={
            "arm": arm_id,
            "rotation": args.rotation,
            "model_profile": profile.to_dict(),
            "budget": (
                monitoring_budget.to_dict() if monitoring else core_budget.to_dict()
            ),
            "result_status": (
                "formal_candidate" if status == "evaluated" else "partial_failure"
            ),
            **run_info,
        },
    )
    root = write_phase1_run_bundle(
        args.output,
        manifest=manifest,
        trajectory_rows=trajectories,
        evaluation_records=records,
        summary=summary,
    )
    state_rows = [
        {
            "episode_index": index,
            "task_id": row["trajectory"]["task_id"],
            **evaluate_decision_states(row["trajectory"]["steps"]),
        }
        for index, row in enumerate(trajectories)
    ]
    _write_jsonl(root / "state_evaluation.jsonl", state_rows)
    print(json.dumps({"output": str(root), "summary": summary}, indent=2, sort_keys=True))
    if status == "partial_failure":
        raise SystemExit("provider failure stopped this cohort unit")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("reactive", "graph"), required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--signal", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--rotation", default="rotation_0")
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=(
            "cold_start_fault_diagnosis",
            "unsupervised_anomaly_detection",
            "online_replay_monitoring",
        ),
        default=["cold_start_fault_diagnosis", "unsupervised_anomaly_detection"],
    )
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
