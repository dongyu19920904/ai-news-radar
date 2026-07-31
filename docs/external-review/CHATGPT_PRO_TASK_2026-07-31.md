# ChatGPT Pro Engineering Task: AI News Radar Delightful Learning Edition

## Role and operating model

You are the external senior engineer for this task. Codex is the accountable
maintainer and final reviewer. Your output is advisory until Codex independently
applies it, reviews it, and runs the repository gates.

You cannot access the maintainer's local filesystem, private GitHub state,
browser session, secrets, or deployment environment. Treat the attached ZIP as
the complete source/context available to you.

## Background

AI News Radar is an existing public, automatically updated AI-news website. It
uses a Python ingestion pipeline to fetch and normalize high-signal public
sources, writes static JSON under `data/`, and serves a no-build vanilla
HTML/CSS/JavaScript frontend from GitHub Pages.

The user wants a public AI-latest-news web program that is:

- fun and interesting;
- genuinely useful rather than decorative;
- playful enough that people want to explore;
- educational enough that a short visit leaves the reader with a concrete
  takeaway.

The current page is capable but visually dense and operational. The goal is to
upgrade the reader experience without replacing or weakening the ingestion
pipeline.

## Current architecture

- `scripts/update_news.py`: Python source ingestion, normalization,
  deduplication, AI relevance scoring, and JSON generation.
- `data/latest-24h.json`: reader-facing AI-focused payload.
- `data/latest-24h-all.json`: lazy-loaded all-mode payload.
- `data/source-status.json`: source health and coverage.
- `data/waytoagi-7d.json`: WaytoAGI update data.
- `index.html`, `assets/app.js`, `assets/styles.css`: static frontend.
- `.github/workflows/update-news.yml`: scheduled update and commit flow.
- `tests/`: Python tests for fetch/filter/normalization behavior.

The source ZIP intentionally excludes generated data, private OPML, reports,
credentials, Git history, caches, and runtime state.

## Non-breakable boundaries

1. Keep the site static and runnable without an API key, login, cookies, server,
   database, bundler, or paid service.
2. Preserve compatibility with the current JSON field names and fallback
   behavior. Existing payloads may omit optional fields.
3. Preserve these reader/maintainer flows:
   - AI-focused view;
   - lazy-loaded all-source view;
   - search;
   - site filtering;
   - dedupe toggle in all mode;
   - WaytoAGI latest-day / seven-day switch;
   - source coverage and advanced source-health details;
   - graceful partial failure when one JSON endpoint cannot load.
4. Do not move advanced source configuration into the first viewport.
5. Do not introduce React/Vue/Svelte, a build step, a runtime dependency, a
   client-side AI API call, analytics, trackers, ads, or remote user storage.
6. Store reader-only state in `localStorage`; handle unavailable/corrupt storage
   without breaking the page.
7. Do not fabricate summaries, metrics, testimonials, citations, freshness,
   translations, or "why it matters" claims. Show only data present in payloads
   or clearly label deterministic UI-derived categories as such.
8. Keep all outbound article links canonical, opening safely with
   `rel="noopener noreferrer"`.
9. No secret, token, API key, cookie, private OPML, email body, or personal data
   may appear in code, fixtures, logs, or reports.

## Product direction

Audience: Chinese-speaking AI enthusiasts, builders, and knowledge workers who
want a fast daily scan but do not want an RSS-reader configuration project.

Primary job: understand the day's AI signal in roughly three minutes, then open
the few original sources that matter.

Tone: warm, smart, playful, and specific. Avoid childish decoration and generic
"AI dashboard" aesthetics.

Design contract:

- Macrostructure: **Ecosystem Index** — multiple discovery surfaces (today's
  short list, latest stream, source cuts, saved learning).
- Theme: **Hum** — warm cream paper, rounded sans type, controlled multi-accent
  surfaces, one character/mascot moment, and purposeful motion.
- Navigation: visible primary search / command-palette affordance, keyboard
  accessible.
- Footer: kinetic marquee that stops under reduced-motion.
- All colors and font declarations must use named CSS tokens. Emit a root
  `tokens.css` and import it from the production stylesheet.
- CSS color literals belong only in the token file and must use OKLCH.
- No purple gradients, gradient text, fake browser/phone chrome, glassmorphism,
  emoji-as-icons, three equal feature cards, thick side-stripe cards, pure white
  or black, or generic floating blobs.
- No italic headings.
- Use one off-grid/asymmetric moment and one intentionally hand-made exception.
- Mobile must work at 320, 375, 414, and 768 CSS px with no horizontal scroll.
- Put `overflow-x: clip` on both `html` and `body`.
- Clickable labels must not wrap; touch targets must be at least 44x44 px.
- All controls need default, hover, focus-visible, active, disabled, loading,
  error, and success treatment where the state is meaningful.
- Focus indicators appear instantly and meet contrast requirements.
- Honor `prefers-reduced-motion`.
- Animate transform and opacity only. Use no more than three animation
  primitives across the page.

## Required reader features

Design and implement a coherent version of all three:

### 1. "Three-minute briefing"

- Select a small, deterministic set of high-value items from the existing AI
  payload. Prefer freshness, explicit AI relevance score when present, official
  sources, and source diversity.
- Explain the selection rule honestly in UI/help text. Do not pretend it is an
  LLM summary or editorial judgment.
- Let readers move through the selected items with keyboard and touch controls.

### 2. "Radar surprise"

- A playful control selects one currently filtered story for discovery.
- The result must be reachable by keyboard, announced accessibly, and never
  auto-navigate without user action.
- Avoid casino mechanics, infinite spinning, or manipulative engagement.

### 3. "My takeaway"

- Readers can save an article and optionally attach one short personal takeaway.
- Persist locally only.
- Show a lightweight daily progress cue such as 0/3, but do not invent streaks
  or sync claims.
- Provide clear remove/edit behavior and a useful empty state.

You may add a compact source-memory quiz only if it stays small, uses real loaded
items, is fully keyboard accessible, and does not displace the three required
features.

## Engineering scope

Primary modification scope:

- `index.html`
- `assets/app.js`
- `assets/styles.css`
- new `tokens.css`
- focused frontend contract tests under `tests/`
- short documentation updates when behavior or local validation changes
- `.hallmark/log.json` entry after the design is finalized

Avoid modifying `scripts/update_news.py`, source fetchers, JSON schemas, or
workflow behavior unless you can demonstrate a concrete compatibility defect
that blocks the reader experience. If you believe such a change is necessary,
explain it before including it and isolate it.

## Accessibility and security requirements

- Semantic heading order and landmarks.
- Native controls or fully implemented ARIA patterns.
- Command palette/modal must trap/restore focus, close on Escape, and not leak
  tab focus to the page behind it.
- Search changes must announce the settled result count politely rather than on
  every keystroke.
- Avoid `innerHTML` for untrusted feed data. Use `textContent` and DOM APIs.
- Treat every news title, source name, URL, and status string as untrusted.
- Validate outbound URLs; allow only `http:` and `https:` before assigning
  navigable `href`.
- Handle malformed JSON fields, invalid timestamps, invalid URLs, missing DOM
  nodes, empty arrays, and denied `localStorage`.

## Required deliverables

Return one downloadable ZIP containing:

1. all complete modified/new source files at repository-relative paths;
2. `CHANGELOG_CHATGPT_PRO.md` summarizing design and engineering decisions;
3. `PATCH.diff` as a unified diff against the attached baseline;
4. `TEST_REPORT.md` listing exact commands run, outcomes, and limitations;
5. `FILE_SHA256.txt` with SHA-256 for every delivered file.

Also summarize in chat:

- architecture/design rationale;
- exact files changed;
- compatibility and security risks;
- tests actually run;
- anything you did not verify.

## Mandatory checks

Run whatever is possible in your environment and report exact outputs:

```bash
python -m py_compile scripts/update_news.py
python -m pytest -q
node --check assets/app.js
git diff --check
```

Add and run focused tests for the new deterministic selection logic, safe URL
handling, local-storage fallback, and required DOM hooks. If you add no browser
test dependency, provide a no-dependency contract test that still catches
missing IDs/handlers/tokens.

Manually inspect or automate these viewports:

- 320x568
- 375x812
- 414x896
- 768x1024
- 1440x900

Verify keyboard-only flows, reduced motion, empty state, partial load failure,
search, filters, all-mode loading, saved takeaways, and external links.

## Prohibited operations and claims

- Do not commit, push, create a PR, deploy, change repository settings, modify
  GitHub Secrets, migrate data, or interact with real users.
- Do not claim production validation, GitHub Pages success, live-feed success,
  or cross-browser support unless you actually performed that exact check and
  can provide evidence.
- Do not include generated `data/`, private OPML, `.env`, caches, screenshots
  containing personal information, browser state, or credentials.
- Do not replace real tests with claims based only on code inspection.
- Do not minify or obfuscate the returned source.

## Acceptance criteria

The delivery passes only if Codex can independently establish all of the
following:

1. The page feels deliberately playful and materially different from a generic
   AI dashboard.
2. A first-time reader understands what to do without opening advanced settings.
3. The three-minute briefing, radar surprise, and local takeaway flows work by
   mouse, touch, and keyboard.
4. Existing data-loading, filtering, all-mode, WaytoAGI, and source-health
   behavior remains compatible.
5. No fabricated content, unsafe URL assignment, untrusted HTML injection,
   credential leak, or remote personal-data storage is introduced.
6. Required repository gates pass.
7. Responsive checks pass at all listed widths with no horizontal overflow.
8. The project remains a static, forkable, no-secret GitHub Pages site.
