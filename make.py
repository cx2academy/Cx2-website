"""Builds the website from src/page.html.

  python3 make.py   ->  body.html        (preview page for Claude)
                        site/index.html  (the real website: drag the `site` folder onto Netlify)

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
print("built body.html and site/index.html")
