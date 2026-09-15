#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd -- "$HERE/.." && pwd)
BENCHMARK_ROOT=${PHM_BENCHMARK_ROOT:?Set PHM_BENCHMARK_ROOT to the compatible Benchmark checkout}
export PYTHONPATH="$ROOT/src:$BENCHMARK_ROOT/src${PHM_DATA_FACTORY_SRC:+:$PHM_DATA_FACTORY_SRC}${PYTHONPATH:+:$PYTHONPATH}"
if [[ -n "${PHM_PYTHON:-}" ]]; then PY=("$PHM_PYTHON"); else PY=(uv run --project "$BENCHMARK_ROOT" --frozen python); fi
if [[ "${1:-}" == test ]]; then
  shift
  exec "${PY[@]}" -m unittest discover -v -s "$HERE/tests" "$@"
fi
exec "${PY[@]}" "$HERE/study.py" "$@"
