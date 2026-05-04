#!/usr/bin/env python3
"""Verify submission-ready LLM credentials without logging secrets."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_OPENROUTER_MODEL = "z-ai/glm-4.5-air:free"
DEFAULT_BIGMODEL_MODEL = "glm-4.7-flash"


def _strip_optional_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _load_env_file(path: Path) -> dict[str, Any]:
    loaded = 0
    skipped_existing = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        if key in os.environ:
            skipped_existing += 1
            continue
        os.environ[key] = _strip_optional_quotes(value)
        loaded += 1
    return {
        "path": str(path),
        "loaded": loaded,
        "skipped_existing": skipped_existing,
    }


def _post_json(url: str, *, api_key: str, body: dict[str, Any], timeout: float) -> tuple[int, dict[str, Any]]:
    payload = json.dumps(body).encode("utf-8")
    req = request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - caller controls fixed HTTPS URLs.
            text = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), json.loads(text)
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"error": {"message": text[:300]}}
        return int(exc.code), payload


def _get_json(url: str, *, api_key: str, timeout: float) -> tuple[int, dict[str, Any]]:
    req = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - caller controls fixed HTTPS URLs.
            text = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), json.loads(text)
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"error": {"message": text[:300]}}
        return int(exc.code), payload


def _message_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    return content if isinstance(content, str) else ""


def _has_completion_choice(payload: dict[str, Any]) -> bool:
    choices = payload.get("choices")
    return isinstance(choices, list) and bool(choices) and isinstance(choices[0], dict)


def _error_message(payload: dict[str, Any]) -> str:
    err = payload.get("error")
    if isinstance(err, dict):
        msg = err.get("message") or err.get("msg") or err.get("code")
        return str(msg)[:300]
    return ""


def check_provider(
    *,
    provider: str,
    model: str,
    env_var: str,
    url: str,
    timeout: float,
    auth_url: str | None = None,
) -> dict[str, Any]:
    api_key = os.getenv(env_var, "").strip()
    result: dict[str, Any] = {
        "provider": provider,
        "model": model,
        "api_key_env": env_var,
        "credential_present": bool(api_key),
        "credential_valid": None,
        "auth_status_code": None,
        "passed": False,
        "status_code": None,
        "response_ok": False,
        "error": None,
    }
    if not api_key:
        result["error"] = f"missing environment variable: {env_var}"
        return result

    if auth_url:
        try:
            auth_status_code, auth_payload = _get_json(auth_url, api_key=api_key, timeout=timeout)
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"auth_transport_error: {type(exc).__name__}: {exc}"
            return result
        result["auth_status_code"] = auth_status_code
        if auth_status_code == 200:
            result["credential_valid"] = True
        elif auth_status_code == 401:
            result["credential_valid"] = False
            result["error"] = _error_message(auth_payload) or "credential rejected by auth endpoint"
            return result

    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: ok"}],
        "temperature": 0,
        "max_tokens": 8,
    }
    try:
        status_code, payload = _post_json(url, api_key=api_key, body=body, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"transport_error: {type(exc).__name__}: {exc}"
        return result

    text = _message_text(payload).strip().lower()
    has_choice = _has_completion_choice(payload)
    result["status_code"] = status_code
    result["response_ok"] = bool(text) or has_choice
    if status_code == 200 and result["response_ok"]:
        result["credential_valid"] = True if result["credential_valid"] is None else result["credential_valid"]
        result["passed"] = True
        return result
    if status_code == 401:
        result["credential_valid"] = False
    elif status_code in {200, 400, 404, 429} and result["credential_valid"] is None:
        result["credential_valid"] = True

    result["error"] = _error_message(payload) or f"empty chat completion response; status={status_code}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openrouter-model", default=DEFAULT_OPENROUTER_MODEL)
    parser.add_argument("--bigmodel-model", default=DEFAULT_BIGMODEL_MODEL)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--output", default="")
    parser.add_argument("--env-file", default="", help="Optional .env file to load before checking credentials.")
    args = parser.parse_args()

    env_file: dict[str, Any] | None = None
    if args.env_file:
        path = Path(args.env_file)
        if not path.exists():
            raise SystemExit(f"env file not found: {path}")
        env_file = _load_env_file(path)

    if not args.openrouter_model.endswith(":free"):
        raise SystemExit("OpenRouter model must be a free model ending in ':free'.")
    if args.bigmodel_model != DEFAULT_BIGMODEL_MODEL:
        raise SystemExit(f"BigModel model must be {DEFAULT_BIGMODEL_MODEL!r}.")

    results = {
        "version": "llm_key_check_v1",
        "env_file": env_file,
        "checks": [
            check_provider(
                provider="openrouter",
                model=args.openrouter_model,
                env_var="OPENROUTER_API_KEY",
                url="https://openrouter.ai/api/v1/chat/completions",
                timeout=args.timeout,
                auth_url="https://openrouter.ai/api/v1/key",
            ),
            check_provider(
                provider="bigmodel",
                model=args.bigmodel_model,
                env_var="BIGMODEL_API_KEY",
                url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
                timeout=args.timeout,
            ),
        ],
    }
    results["passed"] = all(item["passed"] for item in results["checks"])
    text = json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
