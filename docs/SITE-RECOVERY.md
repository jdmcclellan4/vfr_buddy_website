# vfrbuddy.com outage recovery

**Live hosting (now):** GitHub Pages via `.github/workflows/github-pages.yml` and root `CNAME` (`www.vfrbuddy.com`). GoDaddy **www** should point at GitHub (see repo **Settings → Pages** for the exact DNS targets if not using the `CNAME` file alone).

**Long-term / Azure path:** [AZURE-RESTORE.md](AZURE-RESTORE.md)

## Summary

The old Azure Static Web App (`red-field-0c4740a10.7.azurestaticapps.net`) is gone and `AZURE_STATIC_WEB_APPS_API_TOKEN` is invalid, so Azure deploys fail until you recreate the SWA and update the secret.

Until Azure is restored, keep GitHub Pages enabled and **do not** remove the root `CNAME` or the Pages workflow.
