"""Check the deployed snapshot, not just a successful Pages deployment receipt."""

import argparse
from datetime import datetime, timedelta, timezone
import time
from urllib.parse import urljoin

import requests


def verify(base_url: str, expected_generated_at: str) -> dict:
    response = requests.get(base_url, timeout=20)
    response.raise_for_status()
    assert "radar.aivora.cn" in response.text, "custom-domain homepage missing"
    payloads = {}
    for name in ("latest-24h.json", "source-status.json", "briefing-lite.json"):
        response = requests.get(urljoin(base_url, f"data/{name}"), params={"verify": expected_generated_at}, timeout=25)
        response.raise_for_status()
        payloads[name] = response.json()
        assert payloads[name]["generated_at"] == expected_generated_at, f"{name} still serves an older deployment"
    latest = payloads["latest-24h.json"]
    generated = datetime.fromisoformat(latest["generated_at"].replace("Z", "+00:00"))
    assert datetime.now(timezone.utc) - generated < timedelta(hours=2), "snapshot is stale"
    assert latest.get("items"), "AI feed is empty"
    status = payloads["source-status.json"]
    sites = {row["site_id"]: row for row in status["sites"]}
    assert "aibreakfast" not in sites, "retired collector is still active"
    expected = {"curated_media", "hackernews", "github_trending", "producthunt", "aihubtoday"}
    assert expected <= sites.keys(), "new collectors missing from published status"
    assert sites["curated_media"]["ok"] and sites["aihubtoday"]["ok"], "replacement sources failed"
    briefing = payloads["briefing-lite.json"]
    assert 0 < briefing["item_count"] <= 8, "briefing is empty or exceeds its contract"
    return {"generated_at": latest["generated_at"], "items": len(latest["items"]),
            "collectors": len(sites), "failed_sites": status["failed_sites"], "briefing": briefing["item_count"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expected-generated-at", required=True)
    args = parser.parse_args()
    for attempt in range(6):
        try:
            print(verify(args.base_url, args.expected_generated_at))
            break
        except (requests.RequestException, AssertionError, ValueError):
            if attempt == 5:
                raise
            time.sleep(5)
