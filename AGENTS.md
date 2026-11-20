# Working on myprivate.network

A static site: everything served is in `public/`. No build step.

## Making a change

1. Edit files under `public/`. Keep the CSP in `public/_headers` in mind: no inline `<script>`, no third-party scripts, images only from this site or `data:`.
2. Run `node scripts/check.mjs` (broken local links, missing `<title>`, inline scripts).
3. Preview with `npm ci && npm run dev`.
4. Open a pull request. The Check workflow runs the same check, and Cloudflare Pages builds a preview at `<branch>.myprivate-network.pages.dev` (the link appears as a check on the commit).
5. Merging to `main` makes Cloudflare Pages deploy to https://myprivate.network. Confirm the home page, `/blog/`, `/security.txt` and `/pgp.asc` answer 200 afterwards.

When you bump a stylesheet, bump its `?v=` query in the pages that link it, or visitors keep the old one.

## Rules

- The homepage carries no personal name, biography or GitHub link.
- `public/security.txt` and `public/.well-known/security.txt` are the same signed document. Don't edit them by hand: they have to be re-signed with the PGP key, which is not in this repo.
- Blog posts are generated elsewhere and copied into `public/blog/<slug>/`. Fix the source and regenerate rather than hand-editing a post's HTML.
- Deploys need no credentials: Cloudflare Pages is connected to this repository and builds every push. Never commit Cloudflare tokens.
