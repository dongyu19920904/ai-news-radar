const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const html = read("index.html");
const app = read("assets/app.js");
const styles = read("assets/styles.css");
const workflow = read(".github/workflows/update-news.yml");

test("every app element reference exists in the document", () => {
  const documentIds = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
  const appIds = [...app.matchAll(/byId\("([^"]+)"\)/g)].map((match) => match[1]);
  const missing = appIds.filter((id) => !documentIds.has(id));
  assert.deepEqual(missing, []);
});

test("core loads before app and page metadata points to the public site", () => {
  assert.ok(html.indexOf("./assets/core.js") < html.indexOf("./assets/app.js"));
  assert.match(html, /https:\/\/dongyu19920904\.github\.io\/ai-news-radar\//);
  assert.match(html, /<meta\s+name="description"/s);
});

test("static links opened in new tabs have opener protection", () => {
  const externalAnchors = [...html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/gs)].map((match) => match[0]);
  assert.ok(externalAnchors.length > 0);
  externalAnchors.forEach((anchor) => assert.match(anchor, /\brel="[^"]*noopener[^"]*"/));
});

test("rendering avoids untrusted innerHTML and URL assignment is centralized", () => {
  assert.doesNotMatch(app, /\.innerHTML\s*=/);
  assert.doesNotMatch(app, /\.href\s*=\s*item\./);
  assert.match(app, /core\.safeHttpUrl/);
});

test("Hallmark stamp, token import, and page-edge clipping are present", () => {
  assert.match(styles.split(/\r?\n/, 1)[0], /^\/\* Hallmark ·/);
  assert.match(styles, /@import url\("\.\.\/tokens\.css"\);/);
  assert.match(styles, /:root\s*\{[^}]*overflow-x:\s*clip;/s);
  assert.match(styles, /body\s*\{[^}]*overflow-x:\s*clip;/s);
});

test("page workflow publishes only the runtime artifact", () => {
  assert.match(workflow, /actions\/configure-pages@v5/);
  assert.match(workflow, /actions\/upload-pages-artifact@v4/);
  assert.match(workflow, /actions\/deploy-pages@v4/);
  assert.match(workflow, /cp data\/latest-24h\.json data\/latest-24h-all\.json data\/source-status\.json data\/waytoagi-7d\.json _site\/data\//);
  assert.doesNotMatch(workflow, /cp\s+-r\s+data/);
});
