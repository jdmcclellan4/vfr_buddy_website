# VFR Buddy website

Marketing and compliance site for **Google Play** (App Store later). Operated by Flight Forge LLC.

| Path | Play Console field |
|------|---------------------|
| `/` | Marketing website |
| `/legal/` | **Privacy policy** (required) |
| `/support/` | **Support URL** |
| `/legal/#delete` | Data deletion (only if you later add accounts) |

## Deploy on Azure Static Web Apps

**Canonical host:** `https://www.vfrbuddy.com` (custom domain on the SWA).

If the site is down (404 on Azure, failed GitHub Action with “No matching Static Web App”), follow **[docs/AZURE-RESTORE.md](docs/AZURE-RESTORE.md)** end to end.

Quick checklist:

1. [Azure portal](https://portal.azure.com) → **Static Web App** (Free) linked to **`jdmcclellan4/vfr_buddy_website`** / `main`.
2. Build: **app location** `/`, no API, no output (static files only; `skip_app_build` in workflow).
3. Copy the SWA **deployment token** into GitHub secret **`AZURE_STATIC_WEB_APPS_API_TOKEN`**.
4. SWA **Custom domains** → `www.vfrbuddy.com`; update GoDaddy **www** CNAME to the new `*.azurestaticapps.net` host Azure shows (the old `red-field-…` name is dead).
5. Verify `/legal/` and `/support/` before Play Console updates.

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
