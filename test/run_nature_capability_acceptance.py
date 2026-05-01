#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


NODES = (
    Path("research/P0_项目申请书/P0_01_研究背景与调研"),
    Path("research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证"),
    Path("research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理"),
    Path("research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿"),
    Path("research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature"),
    Path("research/P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿"),
    Path("research/P2_论文撰写/P2_03_定稿_tex"),
    Path("research/P2_论文撰写/P2_04_形式检查"),
    Path("research/P3_论文模拟评审与修改_多轮/P3_04_修订动作"),
    Path("research/P4_论文回复_response/P4_02_问题映射矩阵"),
    Path("research/P4_论文回复_response/P4_05_覆盖检查"),
    Path("research/P4_论文回复_response/P4_06_修改证据"),
    Path("research/P4_论文回复_response/P4_07_再投稿打包"),
)
DIMENSIONS = (
    "originality_novelty",
    "scientific_importance",
    "evidence_technical_soundness",
    "reproducibility_transparency",
    "broad_interest_story_clarity",
    "review_robustness",
)
P1_04_PATH = Path("research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证")
P1_05_PATH = Path("research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理")
P1_09_PATH = Path("research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿")
P2_01_PATH = Path("research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature")
P2_02_03_PATH = Path("research/P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿")
P2_03_PATH = Path("research/P2_论文撰写/P2_03_定稿_tex")
P2_04_PATH = Path("research/P2_论文撰写/P2_04_形式检查")
P3_04_PATH = Path("research/P3_论文模拟评审与修改_多轮/P3_04_修订动作")
P4_02_PATH = Path("research/P4_论文回复_response/P4_02_问题映射矩阵")
P4_05_PATH = Path("research/P4_论文回复_response/P4_05_覆盖检查")
P4_06_PATH = Path("research/P4_论文回复_response/P4_06_修改证据")
P4_07_PATH = Path("research/P4_论文回复_response/P4_07_再投稿打包")
P1_04_RESULTS = P1_04_PATH / "artifacts" / "auto_experiment" / "results.tsv"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def read_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_bundle_assets(root: Path) -> list[dict]:
    payload = read_yaml(root / P4_07_PATH / "artifacts" / "resubmission_bundle_manifest.yaml")
    return [item for item in payload.get("assets") or [] if isinstance(item, dict)]


def complete_checklist(node_path: Path) -> dict:
    complete_item = {"item": "complete", "status": "done"}
    return {
        "node_id": node_path.as_posix().replace("/", "::"),
        "node_path": node_path.as_posix(),
        "required_questions_answered": [complete_item],
        "required_outputs": [{"path": "docs/manuscript.md", "status": "done"}],
        "quality_checks": [complete_item],
        "handoff_ready_if": [complete_item],
        "external_review_gate": {
            "required": True,
            "pass_condition": {
                "review_complete": True,
                "overall_verdict": "pass",
                "hard_fail": False,
                "independence_confirmed": True,
            },
        },
    }


def complete_review(node_path: Path) -> dict:
    return {
        "review_complete": True,
        "reviewer_agent_id": "external-reviewer-fixture",
        "reviewer_skill": "external_node_reviewer",
        "reviewed_node_path": node_path.as_posix(),
        "overall_score": 92,
        "overall_verdict": "pass",
        "hard_fail": False,
        "dimension_scores": {name: 4.6 for name in DIMENSIONS},
        "blocking_issues": [],
        "required_actions": [],
        "downstream_ready": True,
        "independence_confirmed": True,
    }


def write_node(root: Path, node_path: Path) -> None:
    node = root / node_path
    write_text(node / "README.md", f"# {node_path.name}\n")
    write_text(node / "status.yaml", "status: done\nauthor_agent_id: author-fixture\n")
    write_text(node / "docs" / "manuscript.md", "Complete evidence-backed node manuscript section.\n")
    write_yaml(node / "prompts" / "acceptance_checklist.yaml", complete_checklist(node_path))
    write_yaml(node / "review" / "verdict.yaml", complete_review(node_path))
    write_text(node / "review" / "AI_001.md", "Independent reviewer finds the node passes the configured gate.\n")
    write_yaml(node / "review" / "response.yaml", {"responses_complete": True})


def citation_registry_payload() -> dict:
    return {
        "citations": [
            {
                "citation_key": "smith2024",
                "claim_id": "claim-core-001",
                "claim_context": "The candidate improves the baseline on the fixture metric.",
                "claim_criticality": "core_claim",
                "source_ref": "research/P2_论文撰写/P2_03_定稿_tex/artifacts/sources/smith2024.pdf",
                "source_locator": "local pdf p. 1",
                "bibliographic_facts_checked": {
                    "title": True,
                    "authors": True,
                    "year": True,
                    "venue": True,
                },
                "support_status": "verified",
                "support_strength": "Directly supports the fixture core claim.",
                "action": "keep",
            },
            {
                "citation_key": "background2023",
                "claim_id": "claim-background-001",
                "claim_context": "Background context for the fixture field.",
                "claim_criticality": "background_context",
                "source_ref": "research/P2_论文撰写/P2_03_定稿_tex/artifacts/sources/background2023.pdf",
                "source_locator": "local pdf p. 2",
                "bibliographic_facts_checked": {
                    "title": True,
                    "authors": True,
                    "year": True,
                    "venue": True,
                },
                "support_status": "unverifiable",
                "support_strength": "Background-only citation; not used for a core or baseline claim.",
                "action": "revise_claim",
            },
        ]
    }


def literature_gap_map_payload() -> dict:
    return {
        "gaps": [
            {
                "gap_id": "gap-001",
                "gap_statement": "Closest prior work does not test the fixture intervention under the target split.",
                "nearest_prior_work": ["smith2024"],
                "citation_refs": ["smith2024"],
                "novelty_boundary": "The claim is limited to the fixture protocol and metric.",
                "falsifiable_question": "Does the candidate improve accuracy over the baseline on the fixture split?",
                "evidence_status": "supported",
                "action": "keep",
            }
        ]
    }


def claim_evidence_registry_payload() -> dict:
    return {
        "claims": [
            {
                "claim_id": "claim-core-001",
                "claim_type": "core_claim",
                "claim_text": "The candidate improves the fixture baseline.",
                "manuscript_location": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex#Results",
                "evidence_refs": [
                    {
                        "evidence_id": "ev-result-001",
                        "evidence_type": "experiment",
                        "source_ref": P1_04_RESULTS.as_posix(),
                    },
                    {
                        "evidence_id": "ev-citation-001",
                        "evidence_type": "citation",
                        "source_ref": "research/P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml",
                    },
                ],
                "support_status": "supported",
                "action": "keep",
            }
        ]
    }


def figure_manifest_payload(path: Path, figure_id: str) -> dict:
    return {
        "figures": [
            {
                "figure_id": figure_id,
                "source_kind": "pdf",
                "source_path": (path / "figures" / f"{figure_id}_source.pdf").as_posix(),
                "output_path": (path / "figures" / f"{figure_id}.pdf").as_posix(),
                "claim_ref": "claim-core-001",
                "evidence_ref": P1_04_RESULTS.as_posix(),
                "necessity": "essential",
                "first_callout_location": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex#Results",
                "status": "accepted",
                "locked_by_node_status": "done",
                "quality_checks": {
                    "vector_or_dpi_checked": True,
                    "caption_self_contained": True,
                    "colorblind_or_grayscale_checked": True,
                    "source_permission_checked": True,
                },
            }
        ]
    }


def failure_register_payload() -> dict:
    return {
        "failures": [
            {
                "failure_id": "fail-001",
                "context": "No negative fixture result invalidates the core claim.",
                "affected_claim_id": "claim-core-001",
                "severity": "low",
                "interpretation": "The fixture still records the checked alternative and limitation boundary.",
                "action": "document_limitation",
                "status": "accepted_limitation",
            }
        ]
    }


def keep_discard_ledger_payload() -> dict:
    return {
        "decisions": [
            {
                "item_id": "claim-core-001",
                "item_type": "claim",
                "decision": "keep",
                "rationale": "The fixture claim is supported by the checked P1_04 result rows.",
                "evidence_ref": P1_04_RESULTS.as_posix(),
            }
        ]
    }


def venue_requirements_payload() -> dict:
    return {
        "selected_profiles": ["nature_article", "ieee_tpami"],
        "active_gate_stage": "submission",
        "venue_fit_decision": "venue_gate_passed",
        "contradiction_list": [
            {
                "profile": "nature_article",
                "issue": "Fixture broad-interest risk was checked.",
                "status": "resolved",
            }
        ],
        "evidence_gaps": [],
        "scope_fit": {
            "nature_article": {
                "originality": True,
                "outstanding_importance": True,
                "interdisciplinary_interest": True,
                "broad_readership": True,
                "broader_context": True,
            },
            "ieee_tpami": {
                "computer_vision": True,
                "pattern_analysis_or_recognition": True,
                "selected_machine_intelligence": True,
                "machine_learning_for_pattern_analysis": True,
            },
        },
        "summary_paragraph_requirements": {
            "max_words": 200,
            "background": True,
            "rationale": True,
            "main_conclusion": True,
            "broader_context": True,
            "broad_reader_language": True,
        },
        "submission_blockers": [],
    }


def revision_action_map_payload() -> dict:
    return {
        "actions": [
            {
                "action_id": "act-001",
                "issue_id": "issue-001",
                "claim_id": "claim-core-001",
                "evidence_id": "ev-result-001",
                "target_path": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex",
                "target_location": "Results",
                "actionable_fix": "Bind the result claim to the fixture evidence rows.",
                "verification": "Check revision evidence map and manuscript location.",
                "status": "done",
            }
        ]
    }


def question_mapping_matrix_payload() -> dict:
    return {
        "mappings": [
            {
                "issue_id": "issue-001",
                "response_item_id": "rsp001",
                "claim_id": "claim-core-001",
                "evidence_id": "ev-result-001",
                "location": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex#Results",
                "response_strategy": "direct_answer_with_evidence",
                "status": "covered",
            }
        ]
    }


def coverage_check_report_payload() -> dict:
    return {
        "coverage": [
            {
                "issue_id": "issue-001",
                "response_item_id": "rsp001",
                "claim_id": "claim-core-001",
                "evidence_id": "ev-result-001",
                "manuscript_location": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex#Results",
                "actionable_fix": "No further action; response and manuscript location are linked.",
                "severity": "medium",
                "coverage_status": "covered",
            }
        ]
    }


def revision_evidence_map_payload() -> dict:
    return {
        "revisions": [
            {
                "issue_id": "issue-001",
                "evidence_id": "ev-result-001",
                "response_item_id": "rsp001",
                "claim_id": "claim-core-001",
                "evidence_kind": "manuscript",
                "manuscript_location": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex#Results",
                "modified_nodes": [P2_03_PATH.as_posix()],
                "revision_diff_ref": "fixture-diff-001",
                "status": "verified",
            }
        ]
    }


def write_complete_fixture(root: Path) -> None:
    for node_path in NODES:
        write_node(root, node_path)

    p001 = root / "research/P0_项目申请书/P0_01_研究背景与调研"
    write_yaml(p001 / "artifacts" / "literature_gap_map.yaml", literature_gap_map_payload())

    p104 = root / "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证"
    write_yaml(
        p104 / "artifacts" / "execution_contract.yaml",
        {
            "contract_mode": "executable",
            "repo_path": "./idea_validation_repo",
            "editable_paths": ["src", "configs"],
            "run_command": "python scripts/run_train.py",
            "metric": {"name": "accuracy", "direction": "higher_is_better", "pattern": r"^accuracy:\s*([0-9.]+)"},
            "budget": {"max_rounds": 2, "max_no_improve_rounds": 1, "max_crashes": 1, "max_minutes_per_run": 30},
        },
    )
    write_text(p104 / "artifacts" / "auto_experiment" / "results.tsv", "run\taccuracy\nbaseline\t0.80\ncandidate\t0.91\n")
    write_text(p104 / "logs" / "auto_experiment" / "latest_run.log", "accuracy: 0.91\n")

    p105 = root / P1_05_PATH
    write_yaml(
        p105 / "artifacts" / "result_registry.yaml",
        {
            "claims": [
                {
                    "claim": "candidate improves baseline",
                    "status": "supported",
                    "source_ledger": P1_04_RESULTS.as_posix(),
                    "ledger_rows": ["baseline", "candidate"],
                    "evidence": "P1_04 results.tsv rows baseline and candidate support the claim.",
                }
            ]
        },
    )
    write_yaml(
        p105 / "artifacts" / "hypothesis_status.yaml",
        {
            "hypotheses": [
                {
                    "hypothesis_id": "h001",
                    "status": "supported",
                    "linked_claims": ["candidate improves baseline"],
                }
            ]
        },
    )
    write_text(
        p105 / "artifacts" / "paper_ready_result_summary.md",
        "The candidate run improves the baseline in P1_04 results.tsv and can support the validation claim.\n",
    )
    write_yaml(p105 / "artifacts" / "failure_register.yaml", failure_register_payload())
    write_text(
        p105 / "artifacts" / "negative_result_note.md",
        "Negative result check: no failed fixture result overturns claim-core-001. "
        "Interpretation: scope remains limited to the fixture split and accuracy metric.\n",
    )
    write_yaml(p105 / "artifacts" / "keep_discard_ledger.yaml", keep_discard_ledger_payload())

    for node_path, figure_id in ((P1_09_PATH, "fig_result"), (P2_02_03_PATH, "fig_flow")):
        node = root / node_path
        write_text(node / "figures" / f"{figure_id}_source.pdf", "source figure")
        write_text(node / "figures" / f"{figure_id}.pdf", "output figure")
        write_yaml(node / "artifacts" / "figure_manifest.yaml", figure_manifest_payload(node_path, figure_id))

    p201 = root / P2_01_PATH
    write_yaml(p201 / "artifacts" / "venue_requirements.yaml", venue_requirements_payload())

    p203 = root / P2_03_PATH
    write_text(p203 / "artifacts" / "sources" / "smith2024.pdf", "verified source")
    write_text(p203 / "artifacts" / "sources" / "background2023.pdf", "background source")
    write_yaml(p203 / "artifacts" / "citation_registry.yaml", citation_registry_payload())
    write_yaml(p203 / "artifacts" / "claim_evidence_registry.yaml", claim_evidence_registry_payload())
    write_yaml(
        p203 / "section_map.yaml",
        {"sections": [{"section": "main", "source": "docs/manuscript.md", "status": "done"}]},
    )
    write_yaml(
        p203 / "sync_map.yaml",
        {"sync_mode": "generated", "sync_items": [{"tex_file": "tex/main.tex", "status": "done"}]},
    )
    write_text(
        p203 / "tex" / "main.tex",
        r"""\documentclass{article}
\title{Fixture Nature-Ready Study}
\begin{document}
\maketitle
\begin{abstract}A concise evidence-backed abstract.\end{abstract}
\section{Introduction}Important field gap and contribution.
\section{Methods}Reproducible protocol, data, code, and statistics.
\section{Results}Controlled evidence supports the central claim.
\section{Discussion}Limitations, alternatives, and impact.
\section*{Data availability}Fixture data paths are listed in the bundle.
\section*{Code availability}Fixture code paths are listed in the bundle.
\end{document}
""",
    )

    p204 = root / P2_04_PATH
    write_text(
        p204 / "artifacts" / "formal_check_report.md",
        "Checked venue_requirements.yaml. No open contradiction remains. No open evidence gap remains.\n",
    )

    write_yaml(root / P3_04_PATH / "artifacts" / "revision_action_map.yaml", revision_action_map_payload())
    write_yaml(root / P4_02_PATH / "artifacts" / "question_mapping_matrix.yaml", question_mapping_matrix_payload())
    write_yaml(root / P4_05_PATH / "artifacts" / "coverage_check_report.yaml", coverage_check_report_payload())
    write_yaml(root / P4_06_PATH / "artifacts" / "revision_evidence_map.yaml", revision_evidence_map_payload())

    p407 = root / P4_07_PATH
    for rel, text in {
        "artifacts/response_letter.tex": "response letter",
        "artifacts/evidence_registry.yaml": "evidence: complete\n",
        "artifacts/figures/figure1.pdf": "figure",
        "artifacts/tables/table1.tsv": "metric\tvalue\naccuracy\t0.91\n",
        "artifacts/submission_metadata.yaml": "journal: Nature\n",
    }.items():
        write_text(p407 / rel, text)
    write_yaml(
        p407 / "artifacts" / "resubmission_bundle_manifest.yaml",
        {
            "assets": [
                {"role": "manuscript", "path": "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex"},
                {"role": "response", "path": "research/P4_论文回复_response/P4_07_再投稿打包/artifacts/response_letter.tex"},
                {"role": "evidence", "path": "research/P4_论文回复_response/P4_07_再投稿打包/artifacts/evidence_registry.yaml"},
                {"role": "figures", "path": "research/P4_论文回复_response/P4_07_再投稿打包/artifacts/figures/figure1.pdf"},
                {"role": "tables", "path": "research/P4_论文回复_response/P4_07_再投稿打包/artifacts/tables/table1.tsv"},
                {"role": "metadata", "path": "research/P4_论文回复_response/P4_07_再投稿打包/artifacts/submission_metadata.yaml"},
                {"role": "citation_registry", "path": "research/P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml"},
                {"role": "figure_manifest", "path": "research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/figure_manifest.yaml"},
                {"role": "venue_requirements", "path": "research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml"},
                {"role": "question_mapping_matrix", "path": "research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml"},
                {"role": "coverage_check_report", "path": "research/P4_论文回复_response/P4_05_覆盖检查/artifacts/coverage_check_report.yaml"},
                {"role": "revision_evidence_map", "path": "research/P4_论文回复_response/P4_06_修改证据/artifacts/revision_evidence_map.yaml"},
            ]
        },
    )


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    script = repo_root() / "scripts" / "validate_research_truth.py"
    return subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--require-submission"],
        cwd=str(repo_root()),
        text=True,
        capture_output=True,
    )


def run_consistency_validator(root: Path) -> subprocess.CompletedProcess[str]:
    script = repo_root() / "scripts" / "validate_research_truth.py"
    return subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        cwd=str(repo_root()),
        text=True,
        capture_output=True,
    )


def expect_pass(root: Path) -> bool:
    proc = run_validator(root)
    print(proc.stdout.strip() or proc.stderr.strip())
    return proc.returncode == 0


def expect_consistency_pass(name: str, root: Path) -> bool:
    proc = run_consistency_validator(root)
    output = proc.stdout + proc.stderr
    ok = proc.returncode == 0
    print(f"{name}: {'pass' if ok else 'fail'}")
    if not ok:
        print(output.strip())
    return ok


def expect_fail(name: str, root: Path, expected_text: str) -> bool:
    proc = run_validator(root)
    output = proc.stdout + proc.stderr
    ok = proc.returncode != 0 and expected_text in output
    print(f"{name}: {'pass' if ok else 'fail'}")
    if not ok:
        print(output.strip())
    return ok


def main() -> int:
    all_ok = True
    with tempfile.TemporaryDirectory(prefix="nature_capability_") as tmpdir:
        tmp = Path(tmpdir)
        complete = tmp / "complete"
        write_complete_fixture(complete)

        print("== complete submission fixture ==")
        all_ok &= expect_pass(complete)

        background_case = tmp / "background_citation_unverifiable_advisory"
        shutil.copytree(complete, background_case)
        registry = citation_registry_payload()
        registry["citations"][0]["support_status"] = "verified"
        registry["citations"][1]["support_status"] = "unverifiable"
        registry["citations"][1]["claim_criticality"] = "background_context"
        write_yaml(background_case / P2_03_PATH / "artifacts" / "citation_registry.yaml", registry)
        print("\n== advisory citation gate ==")
        all_ok &= expect_pass(background_case)

        tpami_only = tmp / "tpami_only_profile"
        shutil.copytree(complete, tpami_only)
        payload = venue_requirements_payload()
        payload["selected_profiles"] = ["ieee_tpami"]
        payload["scope_fit"] = {"ieee_tpami": payload["scope_fit"]["ieee_tpami"]}
        payload.pop("summary_paragraph_requirements")
        write_yaml(tpami_only / P2_01_PATH / "artifacts" / "venue_requirements.yaml", payload)
        print("\n== selected venue profile gate ==")
        all_ok &= expect_pass(tpami_only)

        normal_mode = tmp / "normal_mode_does_not_run_submission_gates"
        shutil.copytree(complete, normal_mode)
        bad_venue = venue_requirements_payload()
        bad_venue["venue_fit_decision"] = "not_fit"
        write_yaml(normal_mode / P2_01_PATH / "artifacts" / "venue_requirements.yaml", bad_venue)
        (normal_mode / P2_03_PATH / "artifacts" / "citation_registry.yaml").unlink()
        print("\n== normal consistency mode ==")
        all_ok &= expect_consistency_pass("normal_mode_skips_submission_evidence_gates", normal_mode)

        cases = {
            "missing_citation_registry_rejected": (
                lambda root: (root / P2_03_PATH / "artifacts" / "citation_registry.yaml").unlink(),
                "citation_registry.yaml",
            ),
            "missing_literature_gap_map_rejected": (
                lambda root: (root / Path("research/P0_项目申请书/P0_01_研究背景与调研") / "artifacts" / "literature_gap_map.yaml").unlink(),
                "literature_gap_map.yaml",
            ),
            "core_claim_unverifiable_citation_rejected": (
                lambda root: write_yaml(
                    root / P2_03_PATH / "artifacts" / "citation_registry.yaml",
                    {
                        "citations": [
                            {
                                **citation_registry_payload()["citations"][0],
                                "support_status": "unverifiable",
                            }
                        ]
                    },
                ),
                "core_claim citation support_status=unverifiable",
            ),
            "comparison_baseline_unverifiable_citation_rejected": (
                lambda root: write_yaml(
                    root / P2_03_PATH / "artifacts" / "citation_registry.yaml",
                    {
                        "citations": [
                            {
                                **citation_registry_payload()["citations"][0],
                                "claim_criticality": "comparison_baseline",
                                "support_status": "unverifiable_access",
                            }
                        ]
                    },
                ),
                "comparison_baseline citation support_status=unverifiable_access",
            ),
            "citation_block_handoff_rejected": (
                lambda root: write_yaml(
                    root / P2_03_PATH / "artifacts" / "citation_registry.yaml",
                    {
                        "citations": [
                            {
                                **citation_registry_payload()["citations"][0],
                                "action": "block_handoff",
                            }
                        ]
                    },
                ),
                "action=block_handoff",
            ),
            "core_claim_pending_claim_evidence_rejected": (
                lambda root: write_yaml(
                    root / P2_03_PATH / "artifacts" / "claim_evidence_registry.yaml",
                    {
                        "claims": [
                            {
                                **claim_evidence_registry_payload()["claims"][0],
                                "support_status": "pending",
                            }
                        ]
                    },
                ),
                "core_claim support_status=pending",
            ),
            "missing_results_rejected": (
                lambda root: (root / "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv").unlink(),
                "results.tsv",
            ),
            "review_only_contract_rejected": (
                lambda root: write_yaml(
                    root / "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/execution_contract.yaml",
                    {"contract_mode": "review_only"},
                ),
                "contract_mode",
            ),
            "reviewer_independence_rejected": (
                lambda root: write_yaml(
                    root / "research/P0_项目申请书/P0_01_研究背景与调研/review/verdict.yaml",
                    {**complete_review(Path("research/P0_项目申请书/P0_01_研究背景与调研")), "independence_confirmed": False},
                ),
                "reviewer independence",
            ),
            "p104_incomplete_review_rejected": (
                lambda root: write_yaml(
                    root / P1_04_PATH / "review" / "verdict.yaml",
                    {**complete_review(P1_04_PATH), "review_complete": False},
                ),
                "review_complete",
            ),
            "missing_run_log_rejected": (
                lambda root: (root / P1_04_PATH / "logs" / "auto_experiment" / "latest_run.log").unlink(),
                "latest_run.log",
            ),
            "incomplete_executable_contract_rejected": (
                lambda root: write_yaml(
                    root / P1_04_PATH / "artifacts" / "execution_contract.yaml",
                    {
                        "contract_mode": "executable",
                        "repo_path": "./idea_validation_repo",
                        "editable_paths": ["src"],
                        "metric": {"name": "accuracy", "direction": "higher_is_better", "pattern": r"^accuracy:\s*([0-9.]+)"},
                        "budget": {"max_minutes_per_run": 30},
                    },
                ),
                "run_command",
            ),
            "missing_hypothesis_status_rejected": (
                lambda root: (root / P1_05_PATH / "artifacts" / "hypothesis_status.yaml").unlink(),
                "hypothesis_status",
            ),
            "placeholder_result_registry_rejected": (
                lambda root: write_text(root / P1_05_PATH / "artifacts" / "result_registry.yaml", "placeholder: <待填写>\n"),
                "placeholder",
            ),
            "registry_without_ledger_anchor_rejected": (
                lambda root: write_yaml(
                    root / P1_05_PATH / "artifacts" / "result_registry.yaml",
                    {"claims": [{"claim": "candidate improves baseline", "status": "supported", "ledger_rows": ["candidate"], "evidence": "unanchored claim"}]},
                ),
                "anchored",
            ),
            "registry_without_ledger_row_rejected": (
                lambda root: write_yaml(
                    root / P1_05_PATH / "artifacts" / "result_registry.yaml",
                    {"claims": [{"claim": "candidate improves baseline", "status": "supported", "source_ledger": P1_04_RESULTS.as_posix(), "evidence": "P1_04 results.tsv"}]},
                ),
                "concrete ledger",
            ),
            "open_high_failure_rejected": (
                lambda root: write_yaml(
                    root / P1_05_PATH / "artifacts" / "failure_register.yaml",
                    {
                        "failures": [
                            {
                                **failure_register_payload()["failures"][0],
                                "severity": "high",
                                "status": "open",
                            }
                        ]
                    },
                ),
                "high failure is open",
            ),
            "negative_note_without_interpretation_rejected": (
                lambda root: write_text(
                    root / P1_05_PATH / "artifacts" / "negative_result_note.md",
                    "Negative result check: no failed fixture result is hidden.\n",
                ),
                "missing interpretation",
            ),
            "placeholder_tex_rejected": (
                lambda root: write_text(root / "research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex", "% 待补充\n"),
                "placeholder",
            ),
            "missing_manifest_rejected": (
                lambda root: (root / "research/P4_论文回复_response/P4_07_再投稿打包/artifacts/resubmission_bundle_manifest.yaml").unlink(),
                "resubmission_bundle_manifest",
            ),
            "missing_figure_claim_ref_rejected": (
                lambda root: write_yaml(
                    root / P1_09_PATH / "artifacts" / "figure_manifest.yaml",
                    {"figures": [{key: value for key, value in figure_manifest_payload(P1_09_PATH, "fig_result")["figures"][0].items() if key != "claim_ref"}]},
                ),
                "missing claim_ref",
            ),
            "missing_first_callout_location_rejected": (
                lambda root: write_yaml(
                    root / P1_09_PATH / "artifacts" / "figure_manifest.yaml",
                    {
                        "figures": [
                            {
                                **figure_manifest_payload(P1_09_PATH, "fig_result")["figures"][0],
                                "first_callout_location": "",
                            }
                        ]
                    },
                ),
                "missing first_callout_location",
            ),
            "missing_figure_evidence_ref_rejected": (
                lambda root: write_yaml(
                    root / P1_09_PATH / "artifacts" / "figure_manifest.yaml",
                    {"figures": [{key: value for key, value in figure_manifest_payload(P1_09_PATH, "fig_result")["figures"][0].items() if key != "evidence_ref"}]},
                ),
                "missing evidence_ref",
            ),
            "decorative_figure_rejected": (
                lambda root: write_yaml(
                    root / P1_09_PATH / "artifacts" / "figure_manifest.yaml",
                    {
                        "figures": [
                            {
                                **figure_manifest_payload(P1_09_PATH, "fig_result")["figures"][0],
                                "necessity": "decorative",
                            }
                        ]
                    },
                ),
                "invalid necessity",
            ),
            "missing_figure_quality_check_rejected": (
                lambda root: write_yaml(
                    root / P1_09_PATH / "artifacts" / "figure_manifest.yaml",
                    {
                        "figures": [
                            {
                                **figure_manifest_payload(P1_09_PATH, "fig_result")["figures"][0],
                                "quality_checks": {
                                    "vector_or_dpi_checked": True,
                                    "caption_self_contained": True,
                                    "colorblind_or_grayscale_checked": True,
                                },
                            }
                        ]
                    },
                ),
                "source_permission_checked",
            ),
            "missing_venue_contradiction_list_rejected": (
                lambda root: write_yaml(
                    root / P2_01_PATH / "artifacts" / "venue_requirements.yaml",
                    {key: value for key, value in venue_requirements_payload().items() if key != "contradiction_list"},
                ),
                "contradiction_list",
            ),
            "venue_not_fit_rejected": (
                lambda root: write_yaml(
                    root / P2_01_PATH / "artifacts" / "venue_requirements.yaml",
                    {
                        **venue_requirements_payload(),
                        "venue_fit_decision": "not_fit",
                    },
                ),
                "venue_fit_decision must be venue_gate_passed",
            ),
            "tpami_scope_missing_rejected": (
                lambda root: write_yaml(
                    root / P2_01_PATH / "artifacts" / "venue_requirements.yaml",
                    {
                        **venue_requirements_payload(),
                        "scope_fit": {
                            **venue_requirements_payload()["scope_fit"],
                            "ieee_tpami": {
                                **venue_requirements_payload()["scope_fit"]["ieee_tpami"],
                                "pattern_analysis_or_recognition": False,
                            },
                        },
                    },
                ),
                "scope_fit.ieee_tpami.pattern_analysis_or_recognition",
            ),
            "planned_revision_action_rejected": (
                lambda root: write_yaml(
                    root / P3_04_PATH / "artifacts" / "revision_action_map.yaml",
                    {
                        "actions": [
                            {
                                **revision_action_map_payload()["actions"][0],
                                "status": "planned",
                            }
                        ]
                    },
                ),
                "status=planned",
            ),
            "uncovered_question_mapping_rejected": (
                lambda root: write_yaml(
                    root / P4_02_PATH / "artifacts" / "question_mapping_matrix.yaml",
                    {
                        "mappings": [
                            {
                                **question_mapping_matrix_payload()["mappings"][0],
                                "status": "uncovered",
                            }
                        ]
                    },
                ),
                "status=uncovered",
            ),
            "partial_coverage_rejected": (
                lambda root: write_yaml(
                    root / P4_05_PATH / "artifacts" / "coverage_check_report.yaml",
                    {
                        "coverage": [
                            {
                                **coverage_check_report_payload()["coverage"][0],
                                "coverage_status": "partial",
                            }
                        ]
                    },
                ),
                "coverage_status=partial",
            ),
            "revision_evidence_missing_location_rejected": (
                lambda root: write_yaml(
                    root / P4_06_PATH / "artifacts" / "revision_evidence_map.yaml",
                    {
                        "revisions": [
                            {
                                key: value
                                for key, value in revision_evidence_map_payload()["revisions"][0].items()
                                if key != "manuscript_location"
                            }
                        ]
                    },
                ),
                "missing manuscript_location",
            ),
            "bundle_missing_citation_role_rejected": (
                lambda root: write_yaml(
                    root / P4_07_PATH / "artifacts" / "resubmission_bundle_manifest.yaml",
                    {
                        "assets": [
                            asset
                            for asset in load_bundle_assets(root)
                            if asset.get("role") != "citation_registry"
                        ]
                    },
                ),
                "citation_registry",
            ),
            "bundle_duplicate_role_rejected": (
                lambda root: write_yaml(
                    root / P4_07_PATH / "artifacts" / "resubmission_bundle_manifest.yaml",
                    {"assets": load_bundle_assets(root) + [load_bundle_assets(root)[0]]},
                ),
                "duplicate asset role",
            ),
        }

        print("\n== negative truth gates ==")
        for name, (mutate, expected_text) in cases.items():
            case_root = tmp / name
            shutil.copytree(complete, case_root)
            mutate(case_root)
            all_ok &= expect_fail(name, case_root, expected_text)

    if all_ok:
        print("\nnature capability acceptance: pass")
        return 0
    print("\nnature capability acceptance: fail")
    return 1


if __name__ == "__main__":
    sys.exit(main())
