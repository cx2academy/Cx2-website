"""Builds the website from src/page.html.

  python3 make.py   ->  body.html        (preview page for Claude)
                        site/index.html  (the real website: drag the `site` folder onto Netlify)
                        site/privacy.html, site/terms.html  (from src/legal/)

Edit your details in the SITE block near the bottom of src/page.html, then run this again.
Put photos (owner.jpg, hero.jpg) inside the `site` folder.
"""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "src/page.html")).read()
icons = open(os.path.join(here, "src/icons.svg")).read()
page = src.replace("{{ICONS}}", icons)
open(os.path.join(here, "body.html"), "w").write(page)

head, body = page.split("</style>", 1)
live = re.sub(r"live:\s*false,", "live: true, ", body, count=1)
os.makedirs(os.path.join(here, "site"), exist_ok=True)
with open(os.path.join(here, "site/index.html"), "w") as f:
    f.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n')
    f.write(head + "</style>\n</head><body>\n" + live + "\n</body></html>\n")
# legal pages: src/legal/<name>.html wrapped in src/legal/shell.html -> site/<name>.html
shell = open(os.path.join(here, "src/legal/shell.html")).read()
for name in ("privacy", "terms"):
    body = open(os.path.join(here, "src/legal", name + ".html")).read()
    title = re.search(r"<!--TITLE:(.*?)-->", body).group(1)
    desc = re.search(r"<!--DESC:(.*?)-->", body).group(1)
    body = re.sub(r"<!--(TITLE|DESC):.*?-->\n", "", body)
    out = shell.replace("{{TITLE}}", title).replace("{{DESC}}", desc).replace("{{BODY}}", body.strip())
    open(os.path.join(here, "site", name + ".html"), "w").write(out)
print("built body.html, site/index.html, site/privacy.html and site/terms.html")
