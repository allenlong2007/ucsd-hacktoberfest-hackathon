"""Download a few project CSVs from the Zenodo abandoned-PR dataset and combine them.

Usage: python backend/data/fetch_zenodo.py [--files 3] [--max-mb 200]
Exits with code 2 if Zenodo is unreachable, so the caller can fall back to
`fetch_live.py --closed 1000`.
"""
import argparse
import csv
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

RECORD_API = "https://zenodo.org/api/records/4892300"
OUT_DIR = Path(__file__).parent / "out"
RAW_DIR = OUT_DIR / "zenodo_raw"
OUT_CSV = OUT_DIR / "historical_prs.csv"
TIMEOUT = 30

COLUMNS = ["repo", "pr_number", "title", "author", "created_at", "closed_at", "state",
           "merged", "abandoned_label", "lines_added", "lines_deleted", "files_changed",
           "review_comments"]

# Output column -> possible source column names (lowercased) in the dataset CSVs.
ALIASES = {
    "repo": ["repo", "project", "repository", "project_name", "repo_name"],
    "pr_number": ["pr_number", "number", "pr_id", "pull_request_id", "id", "pr"],
    "title": ["title", "pr_title"],
    "author": ["author", "user", "author_login", "contributor", "submitter"],
    "created_at": ["created_at", "created", "open_date", "opened_at"],
    "closed_at": ["closed_at", "closed", "close_date"],
    "state": ["state", "status"],
    "merged": ["merged", "is_merged", "merged_at"],
    "abandoned_label": ["abandoned", "is_abandoned", "abandoned_label", "label", "contributor_abandoned"],
    "lines_added": ["lines_added", "additions", "added_lines", "loc_added"],
    "lines_deleted": ["lines_deleted", "deletions", "deleted_lines", "loc_deleted"],
    "files_changed": ["files_changed", "changed_files", "num_files", "n_files"],
    "review_comments": ["review_comments", "num_review_comments", "n_review_comments", "reviewcomments"],
}


def get(url):
    return urllib.request.urlopen(url, timeout=TIMEOUT)


def list_files():
    with get(RECORD_API) as r:
        rec = json.load(r)
    return rec.get("files", [])


def download(f, dest, max_bytes):
    if f["size"] > max_bytes:
        raise RuntimeError(f"{f['key']} is {f['size'] / 1e6:.0f} MB, over limit")
    url = f["links"]["self"]
    with get(url) as r, open(dest, "wb") as out:
        while chunk := r.read(1 << 20):
            out.write(chunk)


def csv_rows(path):
    """Yield (name, DictReader) for every CSV in path (plain or inside a zip)."""
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.lower().endswith(".csv"):
                    with z.open(n) as fh:
                        yield n, csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"))
    else:
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            yield path.name, csv.DictReader(fh)


def map_row(row, colmap, repo_default):
    out = {c: (row.get(colmap[c], "") if c in colmap else "") for c in COLUMNS}
    if not out["repo"]:
        out["repo"] = repo_default
    merged = str(out["merged"]).strip().lower()
    out["merged"] = "" if merged == "" else str(merged not in ("0", "false", "no", "none", "nan"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=int, default=3, help="how many project files to use")
    ap.add_argument("--max-mb", type=int, default=200, help="skip files larger than this")
    args = ap.parse_args()

    try:
        files = list_files()
    except Exception as e:
        print(f"Zenodo unreachable ({e}). Fall back to: python backend/data/fetch_live.py --closed 1000",
              file=sys.stderr)
        return 2

    cands = sorted((f for f in files if f["key"].lower().endswith((".csv", ".zip"))), key=lambda f: f["size"])
    print("Files in record (smallest first):")
    for f in cands:
        print(f"  {f['key']}  {f['size'] / 1e6:.1f} MB")
    picked = [f for f in cands if f["size"] <= args.max_mb * 1e6][: args.files]
    if not picked:
        print("No CSV/zip files within size limit; see list above.", file=sys.stderr)
        return 2

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=COLUMNS)
        w.writeheader()
        for f in picked:
            dest = RAW_DIR / f["key"]
            try:
                print(f"Downloading {f['key']} ...")
                download(f, dest, args.max_mb * 1e6)
            except Exception as e:
                print(f"  failed: {e}", file=sys.stderr)
                continue
            for name, reader in csv_rows(dest):
                lower = {(h or "").strip().lower(): h for h in (reader.fieldnames or [])}
                colmap = {c: lower[a] for c, al in ALIASES.items() for a in al if a in lower}
                missing = [c for c in COLUMNS if c not in colmap]
                print(f"  {name}: columns {list(lower)}; unmapped output columns: {missing}")
                repo_default = Path(name).stem
                n = 0
                for row in reader:
                    w.writerow(map_row(row, colmap, repo_default))
                    n += 1
                total += n
                print(f"  {name}: {n} rows")
    print(f"Wrote {total} rows to {OUT_CSV}")
    return 0 if total else 2


if __name__ == "__main__":
    sys.exit(main())
