# Restore vfrbuddy.com on Azure Static Web Apps

Use this path when you want **Azure** (not GitHub Pages) to host the marketing site.

## What happened

The old Azure Static Web App (`red-field-0c4740a10.7.azurestaticapps.net`) was **deleted** or disconnected. GoDaddy may still CNAME `www` to that hostname, which produces **404 Web Site not found**. The GitHub secret `AZURE_STATIC_WEB_APPS_API_TOKEN` no longer matches any app.

## 1. Create a new Static Web App (portal)

1. Sign in: [Azure Portal](https://portal.azure.com) → **Create a resource** → **Static Web App**.
2. **Basics**
   - Subscription / resource group: use your existing group or create one (e.g. `vfrbuddy-rg`).
   - Name: e.g. `vfrbuddy-site`.
   - Plan: **Free**.
   - Region: **East US 2** (or closest to you).
3. **Deployment**
   - Source: **GitHub**.
   - Sign in to GitHub, org/account: **`jdmcclellan4`**, repo: **`vfr_buddy_website`**, branch: **`main`**.
4. **Build details** (static HTML — no build step)
   - Build Presets: **Custom**.
   - App location: `/`
   - Api location: *(leave empty)*
   - Output location: *(leave empty)*
5. **Review + create**.

Azure may add a **second** workflow file under `.github/workflows/`. That is normal. Either:

- Keep **one** workflow and one secret, or
- Delete the duplicate and use only `.github/workflows/azure-static-web-apps.yml`.

## 2. Fix the GitHub deployment token

1. In Azure → your new SWA → **Settings** → **Configuration** → copy the **deployment token**  
   *(or **Manage deployment token**).*
2. GitHub → [vfr_buddy_website Settings → Secrets](https://github.com/jdmcclellan4/vfr_buddy_website/settings/secrets/actions).
3. Create or update **`AZURE_STATIC_WEB_APPS_API_TOKEN`** with that token (matches the existing workflow).
4. **Actions** → run **Azure Static Web Apps CI/CD** on `main`, or push an empty commit.

When deploy succeeds, note the new default URL, e.g. `https://<something>.azurestaticapps.net/` — open `/legal/` in a browser to confirm.

## 3. Custom domain (www.vfrbuddy.com)

1. Azure SWA → **Custom domains** → **Add** → `www.vfrbuddy.com`.
2. Azure shows the **CNAME target** (often `<your-app>.azurestaticapps.net` — **not** the old `red-field-…` name unless you reused it).
3. **GoDaddy** → DNS for `vfrbuddy.com`:
   - **www** CNAME → value Azure shows (replace dead `red-field-0c4740a10.7.azurestaticapps.net`).
   - **@** apex: keep forward to `https://www.vfrbuddy.com` or Azure apex instructions.
4. Wait for validation → **HTTPS** enabled in Azure.

## 4. Turn off GitHub Pages (avoid fighting for `www`)

- GitHub → repo **Settings → Pages** → remove custom domain / disable Pages if prompted.
- This repo should **not** contain a root `CNAME` file when using Azure.

## 5. Verify Play Console URLs

- https://www.vfrbuddy.com/
- https://www.vfrbuddy.com/legal/
- https://www.vfrbuddy.com/support/

## CLI alternative (after `az login`)

```bash
az group create -n vfrbuddy-rg -l eastus2
az staticwebapp create \
  -n vfrbuddy-site \
  -g vfrbuddy-rg \
  -s https://github.com/jdmcclellan4/vfr_buddy_website \
  -b main \
  -l eastus2 \
  --app-location "/" \
  --login-with-github
az staticwebapp secrets list -n vfrbuddy-site -g vfrbuddy-rg
```

Paste the deployment token into GitHub Actions secret `AZURE_STATIC_WEB_APPS_API_TOKEN`.
