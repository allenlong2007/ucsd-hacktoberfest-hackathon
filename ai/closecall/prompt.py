"""Prompt construction and output normalization for Close Call."""

import json


CLAIM_SHAPE = {
    "type": "comment | review | issue | activity",
    "ref": "source id (comment/review id or issue number)",
    "author": "source author",
    "quote": "short exact quote from the source",
    "supports": "keep_open | close",
}


def model_record(pr: dict) -> dict:
    """Remove future labels before the record is shown to the model."""
    return {k: v for k, v in pr.items() if k not in {"outcome", "evidence"}}


def build_prompt(pr: dict) -> str:
    record = json.dumps(model_record(pr), ensure_ascii=False, indent=2)
    return f"""You audit whether a stale GitHub pull request was justified to close.
Use only the PR data below, which is visible at the time of closure. Do not infer
future outcomes. Return JSON only, with exactly these keys:
{{"claims": [claim objects], "reasons_not_to_close": [strings], "summary": "one sentence"}}

Each claim must have this shape: {json.dumps(CLAIM_SHAPE)}.
Every quote must be copied exactly from a comment, review, or linked issue body.
Use the real source id in ref. Include claims supporting both sides when present.
The reasons_not_to_close list is a skeptical pass: list concrete reasons a human
should hesitate before confirming closure. Never invent sources or quotes.

PR record:
{record}
"""
