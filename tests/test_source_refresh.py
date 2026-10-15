from datetime import datetime, timedelta, timezone

import pytest

from scripts import update_news as news

NOW = datetime(2026, 10, 16, 6, tzinfo=timezone.utc)


def test_hubtoday_reads_the_migrated_feed_with_source_dates():
    class Response:
        content = b'''<rss version="2.0"><channel><item><title>OpenAI launches a new model</title>
        <link>https://hex2077.dev/news/model</link><pubDate>Fri, 16 Oct 2026 05:00:00 GMT</pubDate>
        </item></channel></rss>'''

        def raise_for_status(self):
            pass

    class Session:
        def get(self, url, **_kwargs):
            assert url == "https://hex2077.dev/rss-zh-CN.xml"
            return Response()

    items = news.fetch_ai_hubtoday(Session(), NOW)
    assert len(items) == 1
    assert items[0].published_at == NOW - timedelta(hours=1)
    assert items[0].title == "OpenAI launches a new model"


def test_collectors_replace_breakfast_and_include_public_upstream_additions(monkeypatch):
    names = [
        "fetch_official_ai_updates", "fetch_curated_ai_media", "fetch_follow_builders",
        "fetch_techurls", "fetch_buzzing", "fetch_iris", "fetch_bestblogs", "fetch_tophub",
        "fetch_zeli", "fetch_hacker_news_algolia", "fetch_ai_hubtoday", "fetch_aibase",
        "fetch_aihot", "fetch_newsnow", "fetch_github_trending", "fetch_producthunt",
    ]
    for name in names:
        monkeypatch.setattr(news, name, lambda *_args: [])
    monkeypatch.setattr(news, "fetch_ai_breakfast", lambda *_args: pytest.fail("retired source must stay offline"))
    _, statuses = news.collect_all(object(), NOW)
    site_ids = {row["site_id"] for row in statuses}
    assert "aibreakfast" not in site_ids
    assert {"curated_media", "hackernews", "github_trending", "producthunt"} <= site_ids

    def failure(*_args):
        raise RuntimeError("temporary source outage")

    monkeypatch.setattr(news, "fetch_github_trending", failure)
    _, statuses = news.collect_all(object(), NOW)
    assert [row["site_id"] for row in statuses if not row["ok"]] == ["github_trending"]


def test_project_observation_and_update_times_do_not_fabricate_publication_dates():
    published = "2026-09-01T00:00:00Z"
    updated = "2026-10-16T05:00:00Z"
    assert news.event_time({"site_id": "producthunt", "published_at": published,
                            "updated_at": updated, "recency_basis": "updated_at"}) == NOW - timedelta(hours=1)
    assert news.event_time({"site_id": "github_trending", "published_at": None,
                            "observed_at": updated}) == NOW - timedelta(hours=1)
    project = {"site_id": "github_trending", "site_name": "GitHub Trending", "project_name": "owner/agent",
               "url": "https://github.com/owner/agent", "summary": "An AI coding agent", "published_at": None,
               "observed_at": NOW}
    raw = news.project_raw_items([project])[0]
    assert raw.published_at is None
    assert raw.meta["observed_at"] == news.iso(NOW)


def test_curated_media_respects_caps_and_filters_generic_headlines():
    xml = b'''<rss version="2.0"><channel>
      <item><title>Football results</title><link>https://example.com/sport</link><pubDate>Fri, 16 Oct 2026 05:00:00 GMT</pubDate></item>
      <item><title>OpenAI ships a model</title><link>https://example.com/ai</link><pubDate>Fri, 16 Oct 2026 05:00:00 GMT</pubDate></item>
      <item><title>Claude gets coding tools</title><link>https://example.com/claude</link><pubDate>Fri, 16 Oct 2026 05:00:00 GMT</pubDate></item>
    </channel></rss>'''
    feed = {"title": "The Verge", "xml_url": "https://example.com/feed", "max_entries": 1,
            "include_keywords": "openai,claude", "strict_title_filter": True}
    rows = news.parse_curated_ai_media_feed_items(xml, feed, NOW)
    assert len(rows) == 1
    assert rows[0].title == "OpenAI ships a model"


def test_curated_title_filter_uses_word_boundaries_not_ai_inside_other_words():
    feed = {"include_keywords": "ai,claude", "strict_title_filter": True}
    assert not news.curated_feed_entry_allowed(feed, "Chair design and airline news", "https://example.com/ai")
    assert news.curated_feed_entry_allowed(feed, "AI-powered Claude tools", "https://example.com/tools")


def test_curated_defaults_exclude_duplicate_and_stale_feeds():
    names = {feed["title"] for feed in news.CURATED_AI_MEDIA_FEEDS}
    assert "TechCrunch AI" not in names
    assert "VentureBeat AI" not in names
    assert {"The Decoder AI News", "MarkTechPost Research", "Claude Code Releases"} <= names


def test_producthunt_keeps_recent_updates_without_changing_original_publication():
    from scripts.public_project_sources import parse_producthunt_feed
    xml = '''<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>test</id><title>AI coding helper</title>
    <link href="https://www.producthunt.com/posts/helper"/>
    <published>2026-09-01T00:00:00Z</published><updated>2026-10-16T05:00:00Z</updated>
    <summary>Code reviews with AI</summary></entry></feed>'''
    rows = parse_producthunt_feed(xml, NOW)
    assert len(rows) == 1
    assert rows[0]["published_at"] == datetime(2026, 9, 1, tzinfo=timezone.utc)
    assert rows[0]["updated_at"] == NOW - timedelta(hours=1)
    assert not parse_producthunt_feed(xml.replace("2026-10-16T05:00:00Z", "2026-10-10T05:00:00Z"), NOW)


def test_old_microsoft_rss_resolves_to_verified_official_foundry_feed():
    assert news.RSS_FEED_REPLACEMENTS["https://blogs.microsoft.com/ai/feed/"] == "https://devblogs.microsoft.com/foundry/feed/"


def test_follow_builders_uses_public_api_fallback_and_keeps_other_feeds(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"items": []}

    class Session:
        def get(self, url, **_kwargs):
            if "raw.githubusercontent.com" in url:
                raise RuntimeError("temporary raw endpoint outage")
            assert url.startswith("https://api.github.com/repos/zarazhangrui/follow-builders/contents/")
            return Response()

    expected = [news.RawItem("followbuilders", "Follow Builders", "Blogs", "OpenAI update",
                             "https://example.com/update", NOW, {})]
    monkeypatch.setattr(news, "parse_follow_builders_items", lambda feeds, _now: expected if len(feeds) == 3 else [])
    assert news.fetch_follow_builders(Session(), NOW) == expected


@pytest.mark.parametrize("limit,expected_calls", [(0, 0), (2, 2), (80, 3)])
def test_translation_outage_has_a_request_budget_and_does_not_block_news(monkeypatch, limit, expected_calls):
    calls = []

    def unavailable(_session, title):
        calls.append(title)
        return None

    monkeypatch.setattr(news, "translate_to_zh_cn", unavailable)
    items = [{"title": f"OpenAI releases a new model version {i}", "url": f"https://example.com/{i}"}
             for i in range(20)]
    enriched, _, _ = news.add_bilingual_fields(items, items, object(), {}, limit)
    assert len(calls) == expected_calls
    assert len(enriched) == 20
    assert enriched[0]["title_en"] == items[0]["title"]
