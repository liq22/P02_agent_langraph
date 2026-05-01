from __future__ import annotations
from pathlib import Path
import shutil
import subprocess
from .common import ValidationResult, is_paper_task


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "latex_build"
    strict = is_paper_task(harness)
    tex_files = list(node_path.glob("**/*.tex"))
    if not tex_files:
        return ValidationResult(vid, True, 0.80, "未发现 .tex 文件；跳过 LaTeX 构建。", []).to_dict()

    engine = shutil.which("tectonic") or shutil.which("latexmk") or shutil.which("pdflatex")
    if not engine:
        score = 0.0 if strict else 0.50
        return ValidationResult(vid, False, score, "发现 .tex 文件，但系统缺少 tectonic/latexmk/pdflatex。", []).to_dict()

    tex = tex_files[0]
    cmd = [engine, tex.name]
    if Path(engine).name == "latexmk":
        cmd = [engine, "-pdf", "-interaction=nonstopmode", tex.name]
    elif Path(engine).name == "pdflatex":
        cmd = [engine, "-interaction=nonstopmode", tex.name]
    try:
        proc = subprocess.run(cmd, cwd=str(tex.parent), text=True, capture_output=True, timeout=60)
    except Exception as e:
        return ValidationResult(vid, False, 0.0, "LaTeX 构建异常。", [repr(e)]).to_dict()

    if proc.returncode == 0:
        return ValidationResult(vid, True, 1.0, f"LaTeX 构建通过：{tex.name}", []).to_dict()
    tail = (proc.stdout + "\n" + proc.stderr).splitlines()[-20:]
    score = 0.0 if strict else 0.20
    return ValidationResult(vid, False, score, f"LaTeX 构建失败：{tex.name}", tail).to_dict()
