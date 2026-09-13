# VFR Buddy website

Marketing and compliance site for **Google Play** (App Store later). Operated by Flight Forge LLC.

| Path | Play Console field |
|------|---------------------|
| `/` | Marketing website |
| `/legal/` | **Privacy policy** (required) |
| `/support/` | **Support URL** |
| `/legal/#delete` | Data deletion (only if you later add accounts) |

## Deploy on Azure Static Web Apps

1. In [Azure portal](https://portal.azure.com), create a **Static Web App** (Free plan).
2. Connect this GitHub repo (`jdmcclellan4/vfr_buddy_website`), branch `main`.
3. Build settings:
   - **App location:** `/` (repo root)
   - **Api location:** empty
   - **Output location:** empty
4. Copy the live `https://<name>.azurestaticapps.net` host into Play Console and into `SITE_ORIGIN` in the app repo (`vfr_buddy` → `src/config.ts`).

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
