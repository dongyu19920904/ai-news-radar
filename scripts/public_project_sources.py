"""Public project parsers adapted from LearnPrompt/ai-news-radar 3d04d45."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from urllib.parse import urlparse, urlunparse

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as dtparser

GITHUB_TRENDING_URL = "https://github.com/trending?since=daily"
PRODUCTHUNT_FEED_URL = "https://www.producthunt.com/feed"
PROJECT_SOURCES = {"github_trending": "GitHub Trending", "producthunt": "Product Hunt"}
UTC = timezone.utc


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", BeautifulSoup(str(value or ""), "html.parser").get_text(" ", strip=True)).strip()


def public_url(value: Any, host: str) -> str:
    try:
        parsed = urlparse(str(value or "").strip())
        if parsed.scheme != "https" or parsed.hostname not in {host, f"www.{host}"} or parsed.username or parsed.password:
            return ""
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))
    except ValueError:
        return ""


def parse_github_trending(html: str, now: datetime) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("article.Box-row")
    if not rows:
        raise ValueError("GitHub Trending returned no repository rows")
    out = []
    seen = set()
    for rank, row in enumerate(rows[:50], 1):
        anchor = row.select_one("h2 a[href]")
        if anchor is None:
            continue
        href = str(anchor.get("href") or "")
        url = public_url(f"https://github.com{href}" if href.startswith("/") else href, "github.com")
        path = urlparse(url).path.strip("/")
        if not url or not re.fullmatch(r"[\w.-]+/[\w.-]+", path) or url in seen:
            continue
        seen.add(url)
        description = row.select_one("p")
        summary = clean_text(description.get_text(" ", strip=True) if description else "")[:800]
        stars = re.search(r"([\d,]+)\s+stars?\s+today", row.get_text(" ", strip=True), re.I)
        out.append({
            "site_id": "github_trending", "site_name": PROJECT_SOURCES["github_trending"],
            "project_name": path, "url": url, "summary": summary,
            "published_at": None, "observed_at": now, "source_rank": rank,
            "stars_today": int(stars.group(1).replace(",", "")) if stars else None,
        })
    if not out:
        raise ValueError("GitHub Trending repository links could not be parsed")
    return out


def source_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = dtparser.parse(str(value))
        return parsed.replace(tzinfo=UTC) if not parsed.tzinfo else parsed.astimezone(UTC)
    except (ValueError, TypeError, OverflowError):
        return None


def producthunt_activity(project: dict[str, Any]) -> datetime | None:
    # Only a missing update permits a publication fallback; invalid updates
    # must not turn into a different, apparently fresh event.
    return project.get("updated_at") if project.get("recency_basis") == "updated_at" else project.get("published_at")


def parse_producthunt_feed(xml: str, now: datetime) -> list[dict[str, Any]]:
    feed = feedparser.parse(xml)
    if not feed.entries:
        raise ValueError("Product Hunt returned no feed entries")
    out = []
    seen = set()
    for rank, entry in enumerate(feed.entries[:80], 1):
        name = clean_text(entry.get("title"))[:200]
        url = public_url(entry.get("link"), "producthunt.com")
        if not name or not url or url in seen:
            continue
        # Feed updates are useful discovery signals, not verified first launches.
        # feedparser aliases missing updated to published; a plain dict reads
        # only the actual feed fields so the fallback remains explicit.
        timestamps = dict(entry)
        published = source_timestamp(timestamps.get("published"))
        updated = source_timestamp(timestamps.get("updated"))
        basis = "updated_at" if "updated" in timestamps else "published_at"
        activity = updated if basis == "updated_at" else published
        if activity is None or not now - timedelta(hours=24) <= activity <= now:
            continue
        seen.add(url)
        contents = entry.get("content") or []
        body = entry.get("summary") or (contents[0].get("value") if contents else "") or ""
        soup = BeautifulSoup(body, "html.parser")
        # The official feed separates its tagline and Discussion/Link footer.
        for anchor in soup.select("a"):
            anchor.decompose()
        summary = clean_text(soup.get_text(" ", strip=True)).strip(" |")[:800]
        out.append({
            "site_id": "producthunt", "site_name": PROJECT_SOURCES["producthunt"],
            "project_name": name, "url": url, "summary": summary,
            "published_at": published, "updated_at": updated, "recency_basis": basis,
            "observed_at": now, "source_rank": rank,
        })
    return out


def fetch_github_projects(session: Any, now: datetime) -> list[dict[str, Any]]:
    response = session.get(GITHUB_TRENDING_URL, timeout=25)
    response.raise_for_status()
    return parse_github_trending(response.text, now)


def fetch_producthunt_projects(
    session: Any, now: datetime, *, clock: Callable[[], datetime] | None = None,
) -> list[dict[str, Any]]:
    response = session.get(PRODUCTHUNT_FEED_URL, timeout=25)
    response.raise_for_status()
    # Earlier sources can take minutes. Updates already present in this response
    # must be compared with observation time, not the whole job's start time.
    observed_at = max(now, clock() if clock else datetime.now(UTC))
    return parse_producthunt_feed(response.text, observed_at)
