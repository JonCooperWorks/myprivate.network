#!/usr/bin/env python3
"""Build the blog from posts/ into public/blog/.

usage: python3 scripts/build_blog.py

Each post is a directory, posts/<slug>/, holding:

  post.md       front matter (date, summary) between --- lines, then Markdown.
                The first `# ` heading is the title.
  figures.json  optional: [{"file", "after", "alt", "caption", "wide"}], each
                figure placed after the one paragraph that starts with `after`
                (the Markdown text as written). WebP only.
  anything else is copied next to the post (figures, attachments), so the
                Markdown links to it by bare file name.

Markdown subset: #/##/### headings, paragraphs, - and 1. lists, pipe tables,
**bold**, *italic*, `code`, [links](url). No raw HTML, no images outside
figures.json. Output is deterministic: rebuilding without a source change
leaves public/ untouched.
"""
import datetime
import html
import json
import re
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
OUT = ROOT / "public" / "blog"
SITE = "https://myprivate.network"


def webp_size(path: Path):
    """Width and height of a WebP (VP8, VP8L or VP8X), for the img attributes."""
    b = path.read_bytes()
    assert b[:4] == b"RIFF" and b[8:12] == b"WEBP", path
    kind = b[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8L":
        bits = int.from_bytes(b[21:25], "little")
        return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
    assert kind == b"VP8 ", path
    w, h = struct.unpack("<HH", b[26:30])
    return w & 0x3FFF, h & 0x3FFF


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    codes = []
    text = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<em>\1</em>", text)

    def link(m):
        href = m.group(2)
        rel = ' rel="noopener"' if href.startswith("http") else ""
        return f'<a href="{html.escape(href)}"{rel}>{m.group(1)}</a>'

    text = re.sub(r"\[([^\]]+)\]\(((?:https?://)?[^)\s]+)\)", link, text)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)


def slugify(text: str) -> str:
    text = re.sub(r"[’'“”\"`]", "", text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def convert(md: str):
    """Return (title, body_html). Handles the subset the draft uses."""
    title, out, para, lst, table = "", [], [], None, []

    def flush():
        nonlocal para, lst, table
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table]
            head, aligns, body = rows[0], rows[1], rows[2:]
            right = [a.endswith(":") and not a.startswith(":") for a in aligns]
            cell = lambda tag, c, k: f'<{tag}{" class=\"num\"" if right[k] else ""}>{inline(c)}</{tag}>'
            th = "".join(cell("th", c, k) for k, c in enumerate(head))
            trs = "".join("<tr>" + "".join(cell("td", c, k) for k, c in enumerate(r)) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            table = []
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if lst:
            tag, items, start = lst
            lis = "".join(f"<li>{inline(i)}</li>" for i in items)
            attr = f' start="{start}"' if tag == "ol" and start != 1 else ""
            out.append(f"<{tag}{attr}>{lis}</{tag}>")
            lst = None

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.lstrip().startswith("|"):
            if para or lst:
                flush()
            table.append(line)
            continue
        if table:
            flush()
        if m := re.match(r"^(#{1,3})\s+(.*)$", line):
            flush()
            level, text = len(m.group(1)), m.group(2)
            if level == 1:
                title = text
            else:
                out.append(f'<h{level} id="{slugify(text)}">{inline(text)}</h{level}>')
            continue
        if m := re.match(r"^(-|\d+\.)\s+(.*)$", line):
            tag = "ul" if m.group(1) == "-" else "ol"
            if para or (lst and lst[0] != tag):
                flush()
            if not lst:
                start = int(m.group(1)[:-1]) if tag == "ol" else 1
                lst = (tag, [], start)
            lst[1].append(m.group(2))
            continue
        if lst:
            flush()
        para.append(line.strip())
    flush()
    return title, "\n      ".join(out)


def page(title, description, path, main, og_type="website"):
    url = f"{SITE}{path}"
    t, d = html.escape(title), html.escape(description)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#111310">
  <meta name="description" content="{d}">
  <title>{t} · myprivate.network</title>
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="myprivate.network">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/style.css?v=2">
  <link rel="stylesheet" href="/blog/blog.css?v=3">
</head>
<body>
  <div class="site-shell">
    <header class="masthead">
      <a class="wordmark" href="/" aria-label="myprivate.network home"><span class="logo" aria-hidden="true">↳</span> myprivate<span class="muted">.network</span></a>
      <a class="owner-link" href="/blog/">BLOG <span aria-hidden="true">↗</span></a>
    </header>

    <main>
{main}
    </main>

    <footer><span>MYPRIVATE.NETWORK</span><span>JUST RESEARCH.</span></footer>
  </div>
</body>
</html>
"""


def front_matter(text: str, where: Path):
    assert text.startswith("---\n"), f"{where}: no front matter"
    raw, md = text[4:].split("\n---\n", 1)
    meta = {}
    for line in raw.splitlines():
        if line.strip():
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    assert set(meta) == {"date", "summary"}, f"{where}: front matter needs exactly date and summary"
    return meta, md.lstrip("\n")


def add_figures(body: str, src: Path) -> str:
    spec = src / "figures.json"
    if not spec.exists():
        return body
    for fig in json.loads(spec.read_text(encoding="utf-8")):
        name, after = fig["file"], fig["after"]
        start = f"<p>{inline(after)}"
        assert body.count(start) == 1, f"{src.name}: figure anchor not found once: {after!r} ({body.count(start)})"
        w, h = webp_size(src / name)
        cls = "post-figure wide" if fig.get("wide") else "post-figure"
        tag = (f'<figure class="{cls}"><a href="{name}"><img src="{name}" width="{w}" height="{h}" '
               f'alt="{html.escape(fig["alt"])}" loading="lazy" decoding="async"></a>'
               f'<figcaption>{html.escape(fig["caption"], quote=False)}</figcaption></figure>')
        end = body.index("</p>", body.index(start)) + len("</p>")
        body = body[:end] + "\n      " + tag + body[end:]
    return body


def build_post(src: Path):
    slug = src.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug), f"bad slug: {slug}"
    meta, md = front_matter((src / "post.md").read_text(encoding="utf-8"), src)
    date = datetime.date.fromisoformat(meta["date"])
    title, body = convert(md)
    assert title, f"{slug}: no # title"
    minutes = max(1, round(len(re.findall(r"\w+", md)) / 220))
    post = dict(slug=slug, title=title, summary=meta["summary"], minutes=minutes,
                date_iso=date.isoformat(), date_text=f"{date.day} {date:%B %Y}".upper())
    out = OUT / slug
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    body = add_figures(body, src)
    for f in sorted(src.iterdir()):
        if f.name not in ("post.md", "figures.json") and not f.name.startswith("."):
            shutil.copyfile(f, out / f.name)
    main = f"""      <article class="post">
        <p class="eyebrow"><span class="cross">+</span> <time datetime="{post['date_iso']}">{post['date_text']}</time> · {minutes} MIN READ</p>
        <h1>{inline(title)}</h1>
        <div class="post-body">
      {body}
        </div>
        <p class="post-back"><a class="text-link" href="/blog/"><span class="back-arrow" aria-hidden="true">←</span> ALL POSTS</a></p>
      </article>"""
    (out / "index.html").write_text(page(title, post["summary"], f"/blog/{slug}/", main, "article"), encoding="utf-8")
    return post


def main():
    posts = [build_post(d) for d in sorted(POSTS.iterdir()) if (d / "post.md").exists()]
    posts.sort(key=lambda p: (p["date_iso"], p["slug"]), reverse=True)
    built = {p["slug"] for p in posts}
    stale = [d.name for d in OUT.iterdir() if d.is_dir() and d.name not in built]
    assert not stale, f"public/blog has posts with no source in posts/: {stale}"
    items = "\n".join(f"""          <li>
            <a href="/blog/{p['slug']}/">
              <time datetime="{p['date_iso']}">{p['date_text']}</time>
              <h2>{inline(p['title'])}</h2>
              <p>{html.escape(p['summary'], quote=False)}</p>
              <span class="read-link">READ · {p['minutes']} MIN <span aria-hidden="true">↗</span></span>
            </a>
          </li>""" for p in posts)
    index = f"""      <section class="post-index" aria-labelledby="blog-title">
        <p class="eyebrow"><span class="cross">+</span> NOTES FROM THE PRIVATE SIDE.</p>
        <h1 id="blog-title">Blog<em>.</em></h1>
        <ol class="post-list" reversed>
{items}
        </ol>
      </section>"""
    (OUT / "index.html").write_text(
        page("Blog", "Notes from a private network. Mostly research.", "/blog/", index), encoding="utf-8")
    for p in posts:
        print(f"{p['date_iso']}  {p['slug']}  ({p['minutes']} min)")


if __name__ == "__main__":
    sys.exit(main())
