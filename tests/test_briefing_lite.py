from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from scripts.update_news import build_briefing_lite_payload


UTC = timezone.utc


def make_item(
    index: int,
    *,
    site_id: str,
    score: float,
    now: datetime,
    official: bool = False,
) -> dict:
    effective_site = "official_ai" if official else site_id
    return {
        "id": f"item-{index}",
        "title": f"Item {index}",
        "title_zh": f"精选新闻 {index}",
        "url": f"https://example.com/{index}?utm_source=test",
        "source": f"Source {effective_site}",
        "site_id": effective_site,
        "published_at": (now - timedelta(hours=index)).isoformat(),
        "ai_score": score,
        "ai_label": "model_release",
        "private_field": "must not leak",
    }


def test_briefing_lite_is_small_safe_and_source_diverse():
    now = datetime(2026, 7, 31, 8, 0, tzinfo=UTC)
    items = [
        make_item(1, site_id="a", score=0.98, now=now),
        make_item(2, site_id="a", score=0.97, now=now),
        make_item(3, site_id="b", score=0.90, now=now),
        make_item(4, site_id="c", score=0.80, now=now, official=True),
        {**make_item(5, site_id="d", score=1.0, now=now), "url": "javascript:alert(1)"},
    ]

    payload = build_briefing_lite_payload(
        items,
        generated_at=now.isoformat(),
        window_hours=24,
        now=now,
        limit=3,
    )

    assert payload["item_count"] == 3
    assert payload["source_count"] == 3
    assert payload["minimum_ai_score"] == 0.7
    assert payload["items"][0]["site_id"] == "official_ai"
    assert {item["site_id"] for item in payload["items"]} == {"official_ai", "a", "b"}
    assert all("private_field" not in item for item in payload["items"])
    assert all("utm_source" not in item["url"] for item in payload["items"])
    compact_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    assert len(compact_json.encode("utf-8")) < 10_000


def test_briefing_lite_is_deterministic_and_honors_limit():
    now = datetime(2026, 7, 31, 8, 0, tzinfo=UTC)
    items = [make_item(index, site_id=f"site-{index % 4}", score=0.9, now=now) for index in range(12)]

    first = build_briefing_lite_payload(
        items,
        generated_at=now.isoformat(),
        window_hours=24,
        now=now,
        limit=8,
    )
    second = build_briefing_lite_payload(
        list(reversed(items)),
        generated_at=now.isoformat(),
        window_hours=24,
        now=now,
        limit=8,
    )

    assert first == second
    assert first["item_count"] == 8


def test_briefing_lite_counts_publishers_within_shared_adapters():
    now = datetime(2026, 7, 31, 8, 0, tzinfo=UTC)
    items = [
        {**make_item(1, site_id="opmlrss", score=0.95, now=now), "source": "Publisher A"},
        {**make_item(2, site_id="opmlrss", score=0.94, now=now), "source": "Publisher B"},
        {**make_item(3, site_id="official_ai", score=0.93, now=now), "source": "Vendor C"},
    ]

    payload = build_briefing_lite_payload(
        items,
        generated_at=now.isoformat(),
        window_hours=24,
        now=now,
        limit=3,
    )

    assert payload["source_count"] == 3
    assert {item["source"] for item in payload["items"]} == {"Publisher A", "Publisher B", "Vendor C"}


def test_briefing_lite_keeps_best_duplicate_url_regardless_of_input_order():
    now = datetime(2026, 7, 31, 8, 0, tzinfo=UTC)
    weaker = make_item(1, site_id="opmlrss", score=0.72, now=now)
    stronger = {
        **make_item(2, site_id="official_ai", score=0.99, now=now, official=True),
        "url": weaker["url"],
        "title_zh": "更权威的同链接版本",
    }

    forward = build_briefing_lite_payload(
        [weaker, stronger],
        generated_at=now.isoformat(),
        window_hours=24,
        now=now,
        limit=1,
    )
    reversed_payload = build_briefing_lite_payload(
        [stronger, weaker],
        generated_at=now.isoformat(),
        window_hours=24,
        now=now,
        limit=1,
    )

    assert forward == reversed_payload
    assert forward["items"][0]["title"] == "更权威的同链接版本"
