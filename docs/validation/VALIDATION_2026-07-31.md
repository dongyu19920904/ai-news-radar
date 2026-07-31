# AI News Radar Validation Record

Date: 2026-07-31 (Asia/Shanghai)

## Published result

- Public site: <https://dongyu19920904.github.io/ai-news-radar/>
- Repository: <https://github.com/dongyu19920904/ai-news-radar>
- Implementation commit:
  `52960f220dd8e816a0de2e74ca660218e8739a85`
- Automated data commit:
  `efa7b20118f035c007fc929dbccd4384dc34ea3f`
- Successful workflow:
  <https://github.com/dongyu19920904/ai-news-radar/actions/runs/30603342528>
- GitHub Pages mode: custom workflow, public, HTTPS enforced

The deployed page returned HTTP 200. Its title, canonical URL, core script, and
main interaction script matched the implementation. SHA-256 comparison of
deployed and local runtime assets passed:

- `assets/app.js`:
  `8BDE00FEF97A7A4DF9857E276F3558FED1730D3D12BED2D244D605E37639866D`
- `assets/core.js`:
  `264C34F6041BA7F934E1B23575E30147220899B5DA8F405344279EFCB61B5176`
- `assets/styles.css`:
  `7B5F5E62FF162471CB0CF7C7C76CAF73CE9F7BB71A4023518D10F9952F39AE10`

The first production update generated its snapshot at
`2026-07-31T04:08:21Z` and published 439 AI-focused items from 14 sites and 99
source groups.

## Source handoff package

- Baseline commit:
  `561f69f14774642beec8dcdf1a1827a2905e1d24`
- File:
  `ai-news-radar-source-561f69f-20260731.zip`
- Location:
  `D:\网店\1. 账号商品资料合集\ai-news-radar-review\`
- Size: 155,634 bytes
- SHA-256:
  `1B851C61A6DFD65F5E15A87AAB89F1BD6E0A96BFB67CA851F5076ADD5C4FEB1A`
- Files: 48
- Known secret-format hits: 0
- Reviewed generic false positive: the literal `api_key="test-key"` in a unit
  test fixture

The package excluded Git history, generated data, reports, private OPML, local
environments, caches, databases, browser state, cookies, and credentials.

## ChatGPT Pro collaboration status

The source package and the full engineering task were prepared, but the
authenticated ChatGPT page could not be read by the browser-control channel.
Multiple bounded DOM and screenshot attempts timed out, and the channel later
became unavailable. No message or ZIP was blindly submitted, no ChatGPT output
was accepted, and no conversation link, report, patch, or attachment exists.

This means the requested external-engineer review did not occur. The
implementation and validation below were performed independently by Codex.

## Implemented scope

- Rebuilt the page as a Chinese, playful editorial AI briefing.
- Added deterministic three-item briefing selection with source diversity.
- Added safe random discovery from the active search and filters.
- Added local-only saved stories and 180-character takeaway notes.
- Added a command-palette search dialog with keyboard navigation.
- Preserved AI/all modes, deduplication, site/source filters, source health,
  WaytoAGI updates, and lazy all-mode loading.
- Centralized URL allow-listing to HTTP/HTTPS and removed untrusted
  `innerHTML` rendering.
- Added a tokenized OKLCH design system, keyboard focus states, reduced-motion
  fallback, 48-pixel touch targets, and page-edge clipping.
- Added a Pages deploy job that publishes only the runtime assets and four
  public JSON snapshots.
- Added conditional Windows `tzdata` so the existing test suite can collect on
  Windows.

## Test evidence

Local and detached-worktree runs both passed:

- Python: 58 passed
- Node frontend core and contract tests: 12 passed
- `node --check assets/core.js`: passed
- `node --check assets/app.js`: passed
- Python compile checks for all four scripts: passed
- Workflow YAML parse and job contract: passed
- `git diff --check`: passed
- Final changed-file credential scan: 0 sensitive filenames and 0 known
  credential-pattern files
- GitHub Actions update job: passed
- GitHub Actions Pages deploy job: passed
- Deployed runtime asset hashes: 3/3 matched

The isolated acceptance worktree was:
`D:\网店\1. 账号商品资料合集\ai-news-radar-acceptance-52960f2`.

## Responsive and browser evidence

The browser loaded real repository data and exposed the full accessible DOM:
navigation, briefing, radar, takeaway card, 80 initially rendered items,
load-more control, filters, source health, and WaytoAGI updates.

Viewport checks were run at 320, 375, 414, 768, and 1280 pixels. The first
320-pixel run found a 15-pixel horizontal overflow caused by a body minimum
width. The implementation removed that minimum and increased controls from 44
to 48 pixels. Static contracts enforce `overflow-x: clip` on both the root and
body. A final browser rerun after this fix could not be captured because the
browser-control channel stopped responding.

## Remaining limits

- There is no ChatGPT Pro review or correction cycle.
- A post-fix interactive browser rerun and screenshot set were not available.
- External article links were not exhaustively opened; the application only
  permits HTTP/HTTPS URLs and opens them with opener protection.
- Tests and Pages checks do not claim validation against private OPML,
  AgentMail, X API, real user data, or production secrets; those optional
  integrations remained disabled.
- GitHub Actions emitted a non-failing warning that current Pages actions still
  declare Node.js 20 while the runner forced Node.js 24.
