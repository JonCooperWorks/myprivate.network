# myprivate.network

Personal research homepage and blog. Static HTML and CSS in `public/`, served by Cloudflare Pages (project `myprivatenetwork`).

```sh
npm ci
npm run dev              # local preview
node scripts/check.mjs   # link / title / CSP check
```

Deploys run from GitHub Actions (`.github/workflows/deploy.yml`): pushes to `main` go to production, pull requests get a preview URL. See `AGENTS.md` for how changes are made.

## PGP and security.txt

Public key: `public/pgp.asc`, fingerprint `BC60 5072 FA14 D633 BCA4 41C4 D604 A45C B6E5 3356`, expires 10 October 2028.

`/security.txt` and `/.well-known/security.txt` hold the same signed document; its metadata expires on 1 October 2027. Re-sign and copy it to both paths when it changes.

```sh
gpg --show-keys --with-fingerprint public/pgp.asc
gpg --verify public/security.txt
```
