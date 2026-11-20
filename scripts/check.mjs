// Check the static site before it deploys: every local href/src resolves to a
// file in public/, every page has a <title>, and no inline <script> (the CSP
// only allows script-src 'self'). Run: node scripts/check.mjs
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, dirname, resolve, relative } from 'node:path';

const root = resolve('public');
const files = [];
(function walk(d) {
  for (const n of readdirSync(d)) {
    const p = join(d, n);
    statSync(p).isDirectory() ? walk(p) : files.push(p);
  }
})(root);

const problems = [];
for (const file of files.filter(f => f.endsWith('.html') || f.endsWith('.css'))) {
  const text = readFileSync(file, 'utf8');
  const rel = relative(root, file);
  if (file.endsWith('.html')) {
    if (!/<title>[^<]+<\/title>/.test(text)) problems.push(`${rel}: no <title>`);
    if (/<script(?![^>]*\bsrc=)[^>]*>/i.test(text)) problems.push(`${rel}: inline <script> is blocked by the CSP`);
  }
  const refs = [...text.matchAll(/(?:href|src)="([^"]+)"/g), ...text.matchAll(/url\(["']?([^"')]+)["']?\)/g)].map(m => m[1]);
  for (const ref of refs) {
    if (/^(?:[a-z]+:|\/\/|#|%23|data:)/i.test(ref)) continue;
    const path = decodeURIComponent(ref.split(/[?#]/)[0]);
    if (!path) continue;
    let target = path.startsWith('/') ? join(root, path) : resolve(dirname(file), path);
    if (existsSync(target) && statSync(target).isDirectory()) target = join(target, 'index.html');
    if (!existsSync(target)) problems.push(`${rel}: broken link ${ref}`);
  }
}
if (problems.length) {
  console.error(problems.join('\n'));
  process.exit(1);
}
console.log(`ok: ${files.length} files`);
