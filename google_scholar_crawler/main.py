#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime

from scholarly import scholarly

RESULTS_DIR = "results"
GS_ID_ENV = "GOOGLE_SCHOLAR_ID"


def get_author_data(scholar_id: str) -> dict:
    print(f"[info] Fetching author profile for ID={scholar_id}...", flush=True)
    author = scholarly.search_author_id(scholar_id)
    print("[info] Author found, filling details...", flush=True)
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    print("[info] Author data filled.", flush=True)
    return author


def normalize_author(author: dict) -> dict:
    author = dict(author)
    author["updated"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    pubs = author.get("publications", [])
    author["publications"] = {p["author_pub_id"]: p for p in pubs}
    return author


def save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> int:
    # scholar_id = os.getenv(GS_ID_ENV)
    scholar_id = "xlIBwREAAAAJ" 
    print(f"[debug] Using Google Scholar ID: {scholar_id!r}", flush=True)
    if not scholar_id:
        print(f"[error] Environment variable {GS_ID_ENV} is not set.", flush=True)
        return 1

    try:
        author = get_author_data(scholar_id)
    except Exception as e:
        print(f"[error] Failed to fetch author data: {e!r}", flush=True)
        return 1

    author = normalize_author(author)

    print("[debug] Author snapshot (truncated / use logs as needed):", flush=True)
    print(json.dumps(
        {k: author[k] for k in ("name", "citedby", "updated") if k in author},
        ensure_ascii=False,
        indent=2,
    ))


    save_json(os.path.join(RESULTS_DIR, "gs_data.json"), author)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(author.get("citedby", 0)),
    }
    save_json(os.path.join(RESULTS_DIR, "gs_data_shieldsio.json"), shieldio_data)

    print("[info] Saved results to 'results/'", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())