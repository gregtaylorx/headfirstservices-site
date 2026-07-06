# headfirstservices.com — static site

Plain HTML/CSS, no build step. Structure:

```
/index.html          → hub homepage (all apps)
/visastay/index.html → VisaStay product page
/packlite/index.html → PackLite coming-soon page
/assets/css/style.css
/assets/img/
/robots.txt
/sitemap.xml
```

Adding app #3+ later: copy `/visastay/` as a template, add a card to
`/index.html`'s product grid, add the URL to `sitemap.xml`.

## Deploy — Cloudflare Pages

Domain is already on Cloudflare, so Pages is the path of least resistance.

**Option A — direct upload (fastest, no git required)**
1. Cloudflare dashboard → Workers & Pages → Create → Pages → **Upload assets**
2. Upload this whole folder (drag the `site` folder contents, not the zip)
3. Project name e.g. `headfirstservices` → deploy
4. Pages → your project → Custom domains → add `headfirstservices.com` + `www.headfirstservices.com`
5. Cloudflare will auto-create/adjust the DNS records (CNAME) since the zone is already on Cloudflare

**Option B — git-connected (recommended once you're iterating often)**
1. Push this folder to a GitHub repo (e.g. `headfirstservices-site`)
2. Cloudflare dashboard → Workers & Pages → Create → Pages → **Connect to Git**
3. Build settings: **Framework preset: None**, **Build command: (empty)**, **Build output directory: /**
4. Same custom domain step as above

Either way: no build tooling, no npm install — it's just static files.

## Current deploy status (as of Jul 2026)

- Deployed via direct upload (`npx wrangler pages deploy . --project-name=headfirstservices --commit-dirty=true`), not git-connected. Re-run this command after every content change.
- Custom domain `headfirstservices.com` is bound directly to this Pages project (Custom Domains tab). It serves `/`, `/visastay/*`, `/packlite/*`, and `/assets/*` natively.
- The old `hfs-assets` Worker (a stale pre-existing VisaStay marketing page) previously held the `headfirstservices.com` domain and has been detached.
- A temporary reverse-proxy Worker (`hfs-visastay-proxy`, repo: `nomad-suite/visastay-proxy`) was used before the Pages project owned the root domain, to serve `/visastay/*` etc. alongside the old Worker. It's now retired/deleted — no longer needed since Pages owns the whole domain.

## After going live

- Submit `https://headfirstservices.com/sitemap.xml` in Google Search Console + Bing Webmaster Tools
- Android is in closed testing — update the Google Play badge in `/visastay/index.html` once it's public
- If PackLite publishes, convert `/packlite/index.html` from teaser to full product page (mirror `/visastay/` layout)
- Legal pages (privacy/delete-account) currently stay hosted at gregtaylorx.github.io — that's what's registered with Google Play / App Store. Don't move them without updating both store listings first.
