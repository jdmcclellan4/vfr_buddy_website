/** Public contact. After Azure deploy, SITE_ORIGIN in src/config.ts should match this host. */
window.VFR_BUDDY_SITE = {
  domainLabel: "vfrbuddy.azurestaticapps.net",
  supportEmail: "vfrbuddy@outlook.com",
};

document.addEventListener("DOMContentLoaded", () => {
  const cfg = window.VFR_BUDDY_SITE;
  document.querySelectorAll("[data-support-email]").forEach((el) => {
    el.textContent = cfg.supportEmail;
    if (el.tagName === "A") el.setAttribute("href", "mailto:" + cfg.supportEmail);
  });
  document.querySelectorAll("[data-domain-label]").forEach((el) => {
    el.textContent = cfg.domainLabel;
  });
});
