from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "css" / "styles.css").read_text(encoding="utf-8")
MARKER = '<style id="vfr-buddy-inline">'

for path in ROOT.rglob("*.html"):
    if path.name == "LOCAL-PREVIEW.html":
        continue
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        continue
    href = "css/styles.css" if path.parent == ROOT else "../css/styles.css"
    link = f'<link rel="stylesheet" href="{href}" />'
    if link not in text:
        continue
    block = f'{MARKER}\n{CSS}\n</style>'
    path.write_text(text.replace(link, block + "\n    " + link, 1), encoding="utf-8")
    print("patched", path.relative_to(ROOT))
