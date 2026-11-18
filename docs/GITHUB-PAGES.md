# Host vfrbuddy.com on GitHub Pages

Primary hosting when Azure is unavailable. Repo: **jdmcclellan4/vfr_buddy_website**, branch **main**.

## Deploy

Every push to `main` runs **Deploy GitHub Pages** (`.github/workflows/github-pages.yml`).

Project URL (before custom domain): **https://jdmcclellan4.github.io/vfr_buddy_website/**

## One-time GitHub setup

1. Open **Settings → Pages** on the repo.
2. **Build and deployment** → Source: **GitHub Actions** (not “Deploy from a branch”).
3. After a successful workflow run, under **Custom domain**, enter **`www.vfrbuddy.com`** and save.
4. Wait for **DNS check** and **HTTPS** (can take up to an hour).

The root **`CNAME`** file in the repo should contain `www.vfrbuddy.com`.

## GoDaddy DNS (required)

**www** must point at GitHub, not the old Azure host.

Edit the existing **www** CNAME:

| Type  | Name | Value                  |
|-------|------|------------------------|
| CNAME | www  | **jdmcclellan4.github.io** |

Remove or replace **`red-field-0c4740a10.7.azurestaticapps.net`**.

Do not put `https://` or trailing slashes in the value.

For apex **`vfrbuddy.com`**, use GoDaddy **Forwarding** to **`https://www.vfrbuddy.com`** (301).

## Verify

- https://jdmcclellan4.github.io/vfr_buddy_website/
- https://www.vfrbuddy.com/
- https://www.vfrbuddy.com/legal/
- https://www.vfrbuddy.com/support/

## Play Console / app

Set public URLs to **`https://www.vfrbuddy.com`** paths. Update `SITE_ORIGIN` in the app repo (`vfr_buddy` → `src/config.ts`) to match.

## Assets

HTML uses **jsDelivr** URLs tied to this **public** repo. Keep the repo public so CSS and images load.

## Azure later (optional)

See [AZURE-RESTORE.md](AZURE-RESTORE.md). Do not point **www** at Azure and GitHub at the same time.