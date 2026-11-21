# Working on myprivate.network

A static site: everything served is in `public/`. No build step.

## Making a change

1. Edit files under `public/`. Keep the CSP in `public/_headers` in mind: no inline `<script>`, no third-party scripts, images only from this site or `data:`.
2. Run `node scripts/check.mjs` (broken local links, missing `<title>`, inline scripts).
3. Preview with `npm ci && npm run dev`.
4. Open a pull request. The Check workflow runs the same check, and Cloudflare Pages builds a preview at `<branch>.myprivate-network.pages.dev` (the link appears as a check on the commit).
5. Merging to `main` makes Cloudflare Pages deploy to https://myprivate.network. Confirm the home page, `/blog/`, `/security.txt` and `/pgp.asc` answer 200 afterwards.

## Writing or changing a post

A post is a directory `posts/<slug>/`; the slug is its URL, `/blog/<slug>/`, so don't rename a published one.

- `post.md`: front matter with exactly `date` (YYYY-MM-DD) and `summary` (one line, used for the index and the page description), then Markdown. The first `# ` heading is the title.
- `figures.json` (optional): a list of `{"file", "after", "alt", "caption", "wide"}`. Each WebP figure goes after the one paragraph that starts with `after`.
- Any other file in the directory is published beside the post, so link to attachments by bare file name.

The Markdown subset is small: headings, paragraphs, lists, pipe tables, bold, italic, code and links. `scripts/build_blog.py` documents it.

```sh
python3 scripts/build_blog.py   # needs Python 3.12+; rewrites public/blog/
node scripts/check.mjs
```

Commit `posts/` and the rebuilt `public/blog/` together. The Check workflow fails when they disagree. Everything in this repository is public, drafts included: keep unpublished material out of it.

When you bump a stylesheet, bump its `?v=` query in the pages that link it, or visitors keep the old one.

## Rules

- The homepage carries no personal name, biography or GitHub link.
- `public/security.txt` and `public/.well-known/security.txt` are the same signed document. Don't edit them by hand: they have to be re-signed with the PGP key, which is not in this repo.
- Blog pages under `public/blog/` (the index and each post) are generated from `posts/`. Edit the source and rebuild; never hand-edit them. `public/blog/blog.css` is hand-written.
- Deploys need no credentials: Cloudflare Pages is connected to this repository and builds every push. Never commit Cloudflare tokens.
