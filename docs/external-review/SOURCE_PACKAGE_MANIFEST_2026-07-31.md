# Source Package Manifest

- Purpose: ChatGPT Pro engineering handoff for the playful AI News Radar reader
  experience.
- Git baseline:
  `561f69f14774642beec8dcdf1a1827a2905e1d24`
- Baseline branch: `master`
- Package:
  `ai-news-radar-source-561f69f-20260731.zip`
- Package size: `155634` bytes
- SHA-256:
  `1B851C61A6DFD65F5E15A87AAB89F1BD6E0A96BFB67CA851F5076ADD5C4FEB1A`
- Included files: `48`
- Included uncompressed bytes: `445580`

## Included scope

- Repository instructions and READMEs
- Static frontend source
- Python pipeline source
- Tests
- GitHub update workflow
- Public example OPML files
- Architecture, product, source-strategy, and handoff documentation
- In-repo Scout Skill
- ChatGPT Pro task specification
- Hallmark preflight record

## Excluded scope

- `.git/`
- `data/`
- `reports/`
- generated archives and snapshots
- private `feeds/follow.opml`
- `.env*`
- API keys, tokens, cookies, private keys, browser state, and credentials
- caches, virtual environments, `node_modules`, build output, databases, and
  runtime state

## Secret scan

The machine did not have gitleaks or trufflehog installed. The staging directory
was scanned before compression with:

1. sensitive filename and extension rules for `.env*`, private OPML, cookies,
   certificate/private-key formats, SQLite, and database files;
2. content signatures for AWS, GitHub, OpenAI-style, Google, and Slack keys,
   private-key headers, JWTs, and quoted credential assignments.

Results:

- sensitive filename hits: `0`
- known secret-format hits: `0`
- generic credential-assignment hits: `1`
- reviewed false positive:
  `tests/test_topic_filter.py:426`, the literal `api_key="test-key"` inside a
  unit-test fixture

No live secret or credential was found in the package.
