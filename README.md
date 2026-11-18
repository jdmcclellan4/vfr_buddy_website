# VFR Buddy website

Marketing and compliance site for **Google Play** (App Store later). Operated by Flight Forge LLC.

| Path | Play Console field |
|------|---------------------|
| `/` | Marketing website |
| `/legal/` | **Privacy policy** (required) |
| `/support/` | **Support URL** |
| `/legal/#delete` | Data deletion (only if you later add accounts) |

## Deploy (GitHub Pages)

**Canonical host:** `https://www.vfrbuddy.com`

Hosting runs on **GitHub Pages** via Actions — no Azure account required.

1. Push to **`main`** → workflow **Deploy GitHub Pages**.
2. Repo **Settings → Pages** → source **GitHub Actions**; custom domain **`www.vfrbuddy.com`**.
3. GoDaddy: **www** CNAME → **`jdmcclellan4.github.io`** (not Azure).

Full steps: **[docs/GITHUB-PAGES.md](docs/GITHUB-PAGES.md)**.

Optional Azure path: **[docs/AZURE-RESTORE.md](docs/AZURE-RESTORE.md)** (workflow is manual-only until SWA exists).

## Google Play Data safety (match this policy)

Pro is a **$4.99 / year** Google Play subscription when billing is live:

- **Does the app collect user data?** Yes - precise location, only if the user requests nearest weather. Used for app functionality. Not linked to identity. Not used for advertising. Not sold. Shared with NOAA AWC as a bounding box.
- **Other data:** Favorites and settings stay on-device only.
- **Account creation:** No.
- **Data deletion:** Users uninstall the app. No cloud account.
- **Encryption in transit:** Yes (HTTPS to NOAA).

Privacy contact: `vfrbuddy@outlook.com`.

## Local preview

```bash
npx --yes serve .
```
