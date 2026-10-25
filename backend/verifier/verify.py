"""Check model-written claims against the real PR data (CONTRACT.md section 2). No AI.

verify_claims(pr, claims) returns copies of the claims with `verified` and `check` filled in.
A claim passes only if its ref exists in the PR data, the author matches, the item is
timestamped before pr["closed_at"], and the quote appears in the item's text
(case-insensitive, whitespace-normalized).
"""
from datetime import datetime

# claim type -> (pr key, id field, timestamp field, text fields searched for the quote)
SOURCES = {
    "comment": ("comments", "id", "created_at", ("body",)),
    "review": ("reviews", "id", "submitted_at", ("body", "state")),
    "issue": ("linked_issues", "number", None, ("title", "state_at_close")),
}


def norm(text):
    return " ".join(str(text or "").lower().split())


def parse_ts(value):
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def find_item(pr, ref, kinds):
    for kind in kinds:
        key, id_field, _, _ = SOURCES[kind]
        for item in pr.get(key) or []:
            if norm(item.get(id_field)) == norm(str(ref).lstrip("#")):
                return kind, item
    return None, None


def verify_one(pr, claim):
    ctype, ref = claim.get("type"), claim.get("ref")
    kinds = ("comment", "review") if ctype == "activity" else (ctype,)
    if ctype not in SOURCES and ctype != "activity":
        return False, f"unknown claim type {ctype!r}"
    kind, item = find_item(pr, ref, kinds)
    if item is None:
        return False, f"{ctype} {ref} not found in PR data"
    label = f"{kind} {ref}"
    if item.get("author") is not None and norm(item.get("author")) != norm(claim.get("author")):
        return False, f"{label} is by {item.get('author')}, not {claim.get('author')}"
    ts_field = SOURCES[kind][2]
    if ts_field:
        try:
            if parse_ts(item[ts_field]) >= parse_ts(pr["closed_at"]):
                return False, f"{label} is not before closed_at"
        except (KeyError, ValueError, TypeError):
            return False, f"{label} has no usable timestamp"
    quote = norm(claim.get("quote"))
    if not quote:
        return False, f"{label} claim has no quote"
    if not any(quote in norm(item.get(f)) for f in SOURCES[kind][3]):
        return False, f"quote not found in {label}"
    return True, f"{label} by {item.get('author')} contains quote"


def verify_claims(pr, claims):
    out = []
    for claim in claims:
        ok, check = verify_one(pr, claim)
        out.append({**claim, "verified": ok, "check": check})
    return out
