#!/usr/bin/env python3
"""Refresh the citation snapshot used by the static homepage."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


PROFILE_ID = "xKOhjOkAAAAJ"
PROFILE_URL = (
    "https://scholar.google.com/citations"
    f"?hl=en&user={PROFILE_ID}&pagesize=100"
)
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "scholar.json"


class ScholarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, object]] = []
        self.total_citations = 0
        self._row: dict[str, object] | None = None
        self._field: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())

        if tag == "meta" and attributes.get("name") == "description":
            match = re.search(r"Cited by\s+([\d,]+)", attributes.get("content") or "")
            if match:
                self.total_citations = int(match.group(1).replace(",", ""))

        if tag == "tr" and "gsc_a_tr" in classes:
            self._row = {"title": "", "citations": 0, "year": "", "scholar_url": ""}

        if self._row is None:
            return

        if tag == "a" and "gsc_a_at" in classes:
            self._field = "title"
            self._row["scholar_url"] = urljoin(PROFILE_URL, attributes.get("href") or "")
            self._buffer = []
        elif tag == "a" and "gsc_a_ac" in classes:
            self._field = "citations"
            self._buffer = []
        elif tag == "span" and "gsc_a_h" in classes:
            self._field = "year"
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._row is not None and self._field:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._row is not None and self._field and tag in {"a", "span"}:
            value = " ".join("".join(self._buffer).split())
            if self._field == "citations":
                self._row[self._field] = int(value) if value.isdigit() else 0
            else:
                self._row[self._field] = value
            self._field = None
            self._buffer = []

        if tag == "tr" and self._row is not None:
            if self._row.get("title"):
                self.rows.append(self._row)
            self._row = None


def main() -> None:
    request = Request(
        PROFILE_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")

    parser = ScholarParser()
    parser.feed(html)
    if not parser.rows:
        raise RuntimeError("Google Scholar returned no publications; snapshot was not changed.")

    payload = {
        "profile_id": PROFILE_ID,
        "profile_url": PROFILE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_citations": parser.total_citations,
        "papers": parser.rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(parser.rows)} papers; total citations: {parser.total_citations}")


if __name__ == "__main__":
    main()
