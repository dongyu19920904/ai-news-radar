from datetime import datetime, timezone

import pytest

from scripts.verify_public_site import verify


def payloads(generated):
    sites = [{"site_id": site, "ok": True} for site in
             ["curated_media", "hackernews", "github_trending", "producthunt", "aihubtoday"]]
    return {
        "latest-24h.json": {"generated_at": generated, "items": [{"title": "OpenAI update"}]},
        "source-status.json": {"generated_at": generated, "sites": sites, "failed_sites": []},
        "briefing-lite.json": {"generated_at": generated, "item_count": 1},
    }


def mock_requests(monkeypatch, data):
    class Response:
        text = '<link rel="canonical" href="https://radar.aivora.cn/">'

        def __init__(self, value):
            self.value = value

        def raise_for_status(self):
            pass

        def json(self):
            return self.value

    monkeypatch.setattr("scripts.verify_public_site.requests.get",
                        lambda url, **_kwargs: Response(data.get(url.rsplit("/", 1)[-1])))


def test_smoke_checks_the_actual_published_generation(monkeypatch):
    generated = datetime.now(timezone.utc).isoformat()
    data = payloads(generated)
    mock_requests(monkeypatch, data)
    assert verify("https://radar.aivora.cn/", generated)["collectors"] == 5
    data["source-status.json"]["generated_at"] = "2026-10-09T00:00:00Z"
    with pytest.raises(AssertionError, match="older deployment"):
        verify("https://radar.aivora.cn/", generated)


def test_smoke_rejects_an_empty_feed(monkeypatch):
    generated = datetime.now(timezone.utc).isoformat()
    data = payloads(generated)
    data["latest-24h.json"]["items"] = []
    mock_requests(monkeypatch, data)
    with pytest.raises(AssertionError, match="empty"):
        verify("https://radar.aivora.cn/", generated)
