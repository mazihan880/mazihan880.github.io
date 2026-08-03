#!/usr/bin/env python3
"""Refresh the citation snapshot used by the static homepage."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


PROFILE_ID = "xKOhjOkAAAAJ"
PROFILE_URL = (
    "https://scholar.google.com/citations"
    f"?hl=en&user={PROFILE_ID}&pagesize=100"
)
TRANSLATED_PROFILE_URL = (
    "https://scholar-google-com.translate.goog/citations"
    f"?hl=en&user={PROFILE_ID}&pagesize=100"
    "&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en"
)
REGIONAL_PROFILE_URLS = tuple(
    f"https://{host}/citations?hl=en&user={PROFILE_ID}&pagesize=100"
    for host in (
        "scholar.google.com.sg",
        "scholar.google.co.uk",
        "scholar.google.ca",
    )
)
FETCH_URLS = (PROFILE_URL, *REGIONAL_PROFILE_URLS, TRANSLATED_PROFILE_URL)
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "scholar.json"


def canonicalize_scholar_url(href: str) -> str:
    resolved = urljoin(PROFILE_URL, href)
    parsed = urlsplit(resolved)
    if parsed.netloc != "scholar-google-com.translate.goog":
        return resolved

    query = urlencode([
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.startswith("_x_tr_")
    ])
    return urlunsplit(("https", "scholar.google.com", parsed.path, query, ""))


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
            self._row["scholar_url"] = canonicalize_scholar_url(attributes.get("href") or "")
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


def fetch_profile(opener=urlopen) -> ScholarParser:
    failures: list[str] = []

    for url in FETCH_URLS:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
                )
            },
        )
        try:
            with opener(request, timeout=30) as response:
                html = response.read().decode("utf-8", errors="replace")
        except Exception as error:
            failures.append(f"{url}: {error}")
            continue

        parser = ScholarParser()
        parser.feed(html)
        if parser.rows:
            return parser
        failures.append(f"{url}: response contained no publications")

    raise RuntimeError("Google Scholar profile fetch failed: " + "; ".join(failures))


def update_snapshot(fetcher=fetch_profile, output: Path = OUTPUT, allow_stale: bool = False) -> bool:
    try:
        parser = fetcher()
    except RuntimeError as error:
        if allow_stale and output.is_file():
            print(f"::warning::{error}. Keeping the last valid Scholar snapshot.")
            return False
        raise

    payload = {
        "profile_id": PROFILE_ID,
        "profile_url": PROFILE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_citations": parser.total_citations,
        "papers": parser.rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(parser.rows)} papers; total citations: {parser.total_citations}")
    return True


def main() -> None:
    update_snapshot(allow_stale=os.environ.get("ALLOW_STALE_SCHOLAR") == "1")


if __name__ == "__main__":
    main()
