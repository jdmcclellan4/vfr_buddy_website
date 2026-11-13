# vfrbuddy.com outage recovery

**Primary path (Azure):** [AZURE-RESTORE.md](AZURE-RESTORE.md)

## Summary

`www.vfrbuddy.com` was CNAME’d to a deleted Azure Static Web App. Recreate the SWA, refresh `AZURE_STATIC_WEB_APPS_API_TOKEN`, redeploy from `main`, and point GoDaddy **www** at the **new** Azure hostname.

GitHub Pages was a temporary fallback; remove Pages custom domain and the root `CNAME` file when staying on Azure.
