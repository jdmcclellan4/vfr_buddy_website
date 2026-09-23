from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CDN = "https://cdn.jsdelivr.net/gh/jdmcclellan4/vfr_buddy_website@main/"

for path in ROOT.rglob("*.html"):
    if path.name == "LOCAL-PREVIEW.html":
        continue
    text = path.read_text(encoding="utf-8")
    original = text
    text = text.replace('href="css/styles.css"', f'href="{CDN}css/styles.css"')
    text = text.replace('href="../css/styles.css"', f'href="{CDN}css/styles.css"')
    text = text.replace('src="assets/', f'src="{CDN}assets/')
    text = text.replace('src="../assets/', f'src="{CDN}assets/')
    text = text.replace('href="assets/', f'href="{CDN}assets/')
    text = text.replace('href="../assets/', f'href="{CDN}assets/')
    text = text.replace(
        "https://www.vfrbuddy.com/assets/",
        f"{CDN}assets/",
    )
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("updated", path.relative_to(ROOT))
