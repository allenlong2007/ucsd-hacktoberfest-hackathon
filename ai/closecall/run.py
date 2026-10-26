"""Run rePRieve audits against JSONL stale-closure records."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from prompt import build_prompt, model_record


MODEL = "gemma4:e4b"


def load_env() -> None:
    """Load ignored local config without overriding exported environment values."""
    for path in (Path(__file__).parents[2] / ".env", Path(__file__).parents[1] / ".env"):
        if path.is_file():
            for line in path.read_text().splitlines():
                key, sep, value = line.strip().removeprefix("export ").partition("=")
                if sep and key and not key.startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def request_json(url: str, payload=None, headers=None, timeout=600) -> dict:
    request = Request(url, data=None if payload is None else json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json", **(headers or {})})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read())
        except HTTPError as exc:
            if exc.code == 429 and url.startswith("https://generativelanguage.googleapis.com/") and attempt < 5:
                try:
                    retry_after = float(exc.headers.get("Retry-After", "0"))
                except ValueError:
                    retry_after = 0
                delay = max(retry_after, 2 ** (attempt + 1))
                print(f"Gemini rate limit: retrying in {delay:g}s", file=sys.stderr)
                while delay > 0:
                    pause = min(delay, 60)
                    time.sleep(pause)
                    delay -= pause
                continue
            # Do not include the authenticated URL (or the key) in errors/logs.
            raise RuntimeError(f"Model service returned HTTP {exc.code}") from None


def gemini_models() -> list[str]:
    load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in the environment or ignored ai/.env file.")
    names, token = [], ""
    while True:
        query = {"key": key, "pageSize": 1000}
        if token:
            query["pageToken"] = token
        body = request_json("https://generativelanguage.googleapis.com/v1beta/models?" + urlencode(query))
        names.extend(item["name"] for item in body.get("models", [])
                     if re.search(r"gemma[-_ ]?4", item.get("name", ""), re.I)
                     and "generateContent" in item.get("supportedGenerationMethods", []))
        token = body.get("nextPageToken")
        if not token:
            return sorted(names)


def parse_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    # Models sometimes copy literal line breaks from a source quote into strings.
    # Preserve those characters; the real verifier still checks the exact evidence.
    result = json.loads(text, strict=False)
    if not isinstance(result, dict) or not isinstance(result.get("claims"), list) or not all(
        isinstance(claim, dict) for claim in result["claims"]
    ) or not isinstance(result.get("reasons_not_to_close"), list) or not isinstance(result.get("summary"), str):
        raise ValueError("Expected claims array, reasons_not_to_close array, and summary string")
    return result


def call_model(prompt: str, model: str, backend: str, timeout=600) -> tuple[dict, float]:
    started = time.perf_counter()
    for attempt in range(2):
        instruction = prompt + ("\nReturn valid JSON only; no markdown. Escape quotation marks and "
                                "newlines inside JSON strings. Use at most five claims, each quoting "
                                "a short exact source substring of at most 200 characters." if attempt else "")
        if backend == "ollama":
            payload = {"model": model, "prompt": instruction, "stream": False,
                       "format": "json", "options": {"temperature": 0}}
            try:
                body = request_json("http://127.0.0.1:11434/api/generate", payload, timeout=timeout)
            except RuntimeError as exc:
                if "HTTP 501" not in str(exc):
                    raise
                # Some local Gemma runtimes do not implement constrained JSON.
                payload.pop("format")
                body = request_json("http://127.0.0.1:11434/api/generate", payload, timeout=timeout)
            text = body.get("response", "")
        else:
            body = request_json(
                f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent",
                {"contents": [{"role": "user", "parts": [{"text": instruction}]}]},
                {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, timeout)
            candidates = body.get("candidates", [])
            text = "".join(part.get("text", "") for part in
                           (candidates[0].get("content", {}).get("parts", []) if candidates else [])
                           if not part.get("thought"))
        try:
            return parse_response(text), time.perf_counter() - started
        except (ValueError, json.JSONDecodeError):
            if attempt:
                raise


def call_ollama(prompt: str, model: str = MODEL, timeout: int = 600) -> tuple[dict, float]:
    return call_model(prompt, model, "ollama", timeout)


def stub_response(pr: dict) -> tuple[dict, float]:
    """Deterministic smoke-test response used until the verifier is available."""
    return {"claims": [], "reasons_not_to_close": ["No model call was made."],
            "summary": "ESCALATE: model output unavailable."}, 0.0


def resolve_verifier(pr: dict):
    """Honor PYTHONPATH first; never silently substitute a stub on real records."""
    try:
        sys.path.append(str(Path(__file__).parents[2] / "backend" / "verifier"))
        real_verify = importlib.import_module("verify").verify_claims
        return real_verify, "real"
    except ModuleNotFoundError as exc:
        if exc.name != "verify":
            raise
        if pr.get("_fixture") is not True:
            raise RuntimeError("Real verifier required for non-fixture input. Set PYTHONPATH to its directory.") from None
        return (lambda record, claims: [{**claim, "verified": True,
                 "check": "temporary stub verifier (fixture only)"} for claim in claims]), "stub"


def verify_claims(pr: dict, claims: list[dict]) -> list[dict]:
    verifier, _ = resolve_verifier(pr)
    return verifier(pr, claims)


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


def audit(pr: dict, use_stub: bool = False, model: str = MODEL, backend: str = "ollama") -> dict:
    verifier, verifier_mode = resolve_verifier(pr)
    if use_stub and pr.get("_fixture") is not True:
        raise RuntimeError("--stub is allowed only on fixture records")
    try:
        response, latency = stub_response(pr) if use_stub else call_model(build_prompt(pr), model, backend)
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama/model call failed: {exc}") from exc
    raw_claims = response.get("claims", []) if isinstance(response, dict) else []
    checked = verifier(pr, raw_claims)
    result = {
        "repo": pr.get("repo"), "pr_number": pr.get("pr_number"),
        "verdict": verdict(pr, checked),
        "summary": response.get("summary", "") if isinstance(response, dict) else "",
        "claims": checked,
        "reasons_not_to_close": response.get("reasons_not_to_close", []) if isinstance(response, dict) else [],
        "claims_total": len(raw_claims),
        "claims_rejected": sum(c.get("verified") is False for c in checked),
        "model": f"{backend}:{model}", "latency_s": round(latency, 3),
        "verifier": verifier_mode,
    }
    if "outcome" in pr:
        result["outcome"] = pr["outcome"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--stub", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--backend", choices=("ollama", "gemini"), default="ollama")
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--resume", action="store_true", help="Skip already audited PRs in the output")
    parser.add_argument("--workers", type=int, default=1, help="Maximum concurrent audits; keep Ollama at 1")
    args = parser.parse_args()
    if args.delay < 0:
        parser.error("--delay must be nonnegative")
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    load_env()
    model = args.model or MODEL
    if args.backend == "gemini" or args.list_models:
        available = gemini_models()
        if args.list_models:
            print(json.dumps(available))
            return
        if not available:
            parser.error("No Gemma 4 generateContent model is available for this API key.")
        model = args.model or available[0]
        if not model.startswith("models/"):
            model = "models/" + model
        if model not in available:
            parser.error("Requested model is not in the discovered Gemma 4 model list.")
        print(f"Using gemini:{model}", file=sys.stderr)
    if args.input is None:
        parser.error("input JSONL is required")
    records = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    for record in records:
        resolve_verifier(record)  # Fail before inference or truncating an output file.
        if args.stub and record.get("_fixture") is not True:
            parser.error("--stub is allowed only on fixture records")
    output = args.output or Path("ai/out/audits.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    completed = set()
    if args.resume and output.exists():
        for line in output.read_text().splitlines():
            row = json.loads(line)
            if row.get("model") != f"{args.backend}:{model}" or row.get("verifier") != "real":
                parser.error("Resume requires matching model and real verifier in existing audits")
            completed.add((row["repo"], row["pr_number"]))
    pending_records = iter(record for record in records
                           if (record["repo"], record["pr_number"]) not in completed)
    last_start = 0.0
    failures = []
    with output.open("a" if args.resume else "w") as target, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        exhausted = False
        while futures or not exhausted:
            while len(futures) < args.workers and not exhausted:
                record = next(pending_records, None)
                if record is None:
                    exhausted = True
                    break
                time.sleep(max(0, args.delay - (time.monotonic() - last_start)))
                futures[pool.submit(audit, record, args.stub, model, args.backend)] = record
                last_start = time.monotonic()
            if not futures:
                break
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                record = futures.pop(future)
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append((record["repo"], record["pr_number"]))
                    print(f"Audit failed for {record['repo']}#{record['pr_number']}: {exc}", file=sys.stderr)
                    continue
                target.write(json.dumps(result) + "\n")
                target.flush()
                completed.add((record["repo"], record["pr_number"]))
                print(f"{len(completed)}/{len(records)} {record['repo']}#{record['pr_number']}: "
                      f"{result['verdict']} ({result['latency_s']}s)", file=sys.stderr)
    if failures:
        raise RuntimeError(f"{len(failures)} audits failed; completed audits preserved. Rerun with --resume.")


if __name__ == "__main__":
    main()
