# vfrbuddy.com outage recovery

## What broke

`www.vfrbuddy.com` still points at Azure (`red-field-0c4740a10.7.azurestaticapps.net`), but Azure returns **404 Web Site not found**. The Static Web App resource was removed or the custom domain is no longer bound to a live app.

## Option A — Restore Azure Static Web Apps (keeps current DNS)

1. Sign in at [Azure Portal](https://portal.azure.com).
2. **Create** → **Static Web App** (Free).
3. Source: GitHub → `jdmcclellan4/vfr_buddy_website`, branch `main`.
4. Build: app location `/`, output empty, **skip build** (static files only).
5. After create, copy the **deployment token** → GitHub repo **Settings → Secrets** → `AZURE_STATIC_WEB_APPS_API_TOKEN`.
6. Push any commit to `main` (or re-run **Azure Static Web Apps CI/CD**).
7. In the SWA → **Custom domains** → add `www.vfrbuddy.com` (and apex if needed). Follow Azure’s DNS validation if the hostname changed.

## Option B — GitHub Pages (this repo)

Workflow: `.github/workflows/github-pages.yml`

1. GitHub → **Settings → Pages** → Source: **GitHub Actions** (enable if prompted).
2. After a successful deploy, set **Custom domain** to `www.vfrbuddy.com`.
3. At your domain registrar, update DNS:
   - **www** → CNAME → `jdmcclellan4.github.io`
   - **apex** (`vfrbuddy.com`) → four GitHub Pages A records **or** redirect apex → www (registrar-dependent).
4. Remove old Azure CNAME for `www` once GitHub shows a valid certificate.

Temporary URL before DNS change: `https://jdmcclellan4.github.io/vfr_buddy_website/`

## Play Console URLs

After either option is live, verify:

- https://www.vfrbuddy.com/legal/
- https://www.vfrbuddy.com/support/

Update `SITE_ORIGIN` in the app repo if the canonical host changes.
