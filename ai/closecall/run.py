"""Run Close Call audits against JSONL stale-closure records."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from prompt import build_prompt, model_record


MODEL = "gemma4:e4b"


def call_ollama(prompt: str, model: str = MODEL, timeout: int = 600) -> tuple[dict, float]:
    started = time.perf_counter()
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "format": "json", "options": {"temperature": 0}}).encode()
    request = Request("http://127.0.0.1:11434/api/generate", data=payload,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read())
    elapsed = time.perf_counter() - started
    text = body.get("response", "")
    try:
        return json.loads(text), elapsed
    except json.JSONDecodeError:
        # One retry is required by the project spec. Ask for JSON without changing
        # the source record or exposing future labels.
        retry = Request("http://127.0.0.1:11434/api/generate", data=json.dumps({
            "model": model, "prompt": prompt + "\nReturn valid JSON only; no markdown.",
            "stream": False, "format": "json", "options": {"temperature": 0},
        }).encode(), headers={"Content-Type": "application/json"})
        with urlopen(retry, timeout=timeout) as response:
            retry_body = json.loads(response.read())
        return json.loads(retry_body.get("response", "")), time.perf_counter() - started


def stub_response(pr: dict) -> tuple[dict, float]:
    """Deterministic smoke-test response used until the verifier is available."""
    return {"claims": [], "reasons_not_to_close": ["No model call was made."],
            "summary": "ESCALATE: model output unavailable."}, 0.0


def verify_claims(pr: dict, claims: list[dict]) -> list[dict]:
    """Use Lio's verifier when available; otherwise use the required temporary stub."""
    try:
        sys.path.insert(0, str(Path(__file__).parents[2] / "backend" / "verifier"))
        from verify import verify_claims as real_verify  # type: ignore
        return real_verify(pr, claims)
    except (ImportError, FileNotFoundError):
        return [{**claim, "verified": True, "check": "temporary stub verifier"}
                for claim in claims]


def verdict(pr: dict, claims: list[dict]) -> str:
    verified = [c for c in claims if c.get("verified") is True]
    text = " ".join(str(c.get("quote", "")) for c in verified).lower()
    security = any(word in text for word in ("security", "xss", "vulnerability", "cve"))
    if security or any(c.get("supports") == "keep_open" and c.get("author_association") in
                       {"MEMBER", "OWNER", "COLLABORATOR"} for c in verified):
        return "ESCALATE" if security else "UNSUPPORTED"
    if any(c.get("type") == "review" and c.get("state") == "APPROVED" for c in verified):
        return "UNSUPPORTED"
    if any(c.get("type") == "issue" and c.get("state_at_close") == "OPEN" for c in verified):
        return "UNSUPPORTED"
    if any(c.get("supports") == "close" and c.get("author") == pr.get("author") for c in verified):
        return "CONFIRMED"
    return "ESCALATE"


def audit(pr: dict, use_stub: bool = False, model: str = MODEL) -> dict:
    try:
        response, latency = stub_response(pr) if use_stub else call_ollama(build_prompt(pr), model)
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama/model call failed: {exc}") from exc
    raw_claims = response.get("claims", []) if isinstance(response, dict) else []
    checked = verify_claims(pr, raw_claims)
    result = {
        "repo": pr.get("repo"), "pr_number": pr.get("pr_number"),
        "verdict": verdict(pr, checked),
        "summary": response.get("summary", "") if isinstance(response, dict) else "",
        "claims": checked,
        "reasons_not_to_close": response.get("reasons_not_to_close", []) if isinstance(response, dict) else [],
        "claims_total": len(raw_claims),
        "claims_rejected": sum(c.get("verified") is False for c in checked),
        "model": model, "latency_s": round(latency, 3),
    }
    if "outcome" in pr:
        result["outcome"] = pr["outcome"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--stub", action="store_true")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args()
    output = args.output or Path("ai/out/audits.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open() as source, output.open("w") as target:
        for line in source:
            if line.strip():
                target.write(json.dumps(audit(json.loads(line), args.stub, args.model)) + "\n")


if __name__ == "__main__":
    main()
