"""Run Close Call audits against JSONL stale-closure records."""

from __future__ import annotations

import argparse
import json
import re
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
    # Security is an escalation even when it appears only in metadata or a path.
    security_pattern = re.compile(r"security|xss|vulnerab|cve|sanitiz|auth|csrf|injection", re.I)
    paths = " ".join(str(item.get("path", "")) for item in pr.get("files", []))
    if security_pattern.search(f"{pr.get('title', '')} {paths}"):
        return "ESCALATE"
    source_by_ref = {}
    for item in pr.get("comments", []):
        source_by_ref[("comment", str(item.get("id")))] = item
    for item in pr.get("reviews", []):
        source_by_ref[("review", str(item.get("id")))] = item
    for item in pr.get("linked_issues", []):
        source_by_ref[("issue", str(item.get("number")))] = item

    # Only source metadata from the PR record is authoritative. Never trust
    # author_association/state fields that a model may put into its claim.
    sources = [(claim, source_by_ref.get((claim.get("type"), str(claim.get("ref")))))
               for claim in verified]
    if any(c.get("supports") == "keep_open" and source and
           source.get("author_association") in {"MEMBER", "OWNER", "COLLABORATOR"}
           for c, source in sources):
        return "UNSUPPORTED"
    if any(c.get("type") == "review" and source and source.get("state") == "APPROVED"
           for c, source in sources):
        return "UNSUPPORTED"
    if any(c.get("type") == "issue" and source and source.get("state_at_close") == "OPEN"
           for c, source in sources):
        return "UNSUPPORTED"
    if any(c.get("supports") == "close" and source and
           source.get("author_association") in {"MEMBER", "OWNER", "COLLABORATOR"}
           for c, source in sources):
        return "CONFIRMED"
    if any(c.get("supports") == "close" and source and
           source.get("author") == pr.get("author") for c, source in sources):
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
