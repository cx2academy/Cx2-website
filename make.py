"""Builds the website from src/page.html.

  python3 make.py   ->  body.html        (preview page for Claude)
                        site/index.html  (the real website: Cloudflare Pages publishes the `site` folder)
                        site/privacy.html, site/terms.html  (from src/legal/)

Edit your details in the SITE block near the bottom of src/page.html, then run this again.
Put photos (owner.jpg, hero.jpg) inside the `site` folder.

For the real website, your details (name, phone, email, hours, story, areas, photo and
business data) are written straight into the HTML, so search engines and AI tools that
don't run JavaScript still see them. The preview banner is left out of the real site.
"""
import html, json, os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "src/page.html")).read()
icons = open(os.path.join(here, "src/icons.svg")).read()
page = src.replace("{{ICONS}}", icons)
open(os.path.join(here, "body.html"), "w").write(page)


def js_object_to_json(text):
    """Turn the SITE object literal (comments, bare keys, trailing commas) into JSON."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            j, buf = i + 1, []
            while text[j] != c:
                if text[j] == "\\":
                    buf.append(text[j:j + 2]); j += 2; continue
                buf.append(text[j]); j += 1
            body = "".join(buf)
            if c == "'":
                body = body.replace("\\'", "'").replace('"', '\\"')
            out.append('"' + body + '"'); i = j + 1
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            word, k = text[i:j], j
            while k < n and text[k] in " \t":
                k += 1
            out.append('"%s"' % word if k < n and text[k] == ":" else word); i = j
        else:
            out.append(c); i += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))


SITE = js_object_to_json(re.search(r"var SITE = (\{.*?\n\});", src, re.S).group(1))
esc = html.escape


def prerender(body):
    def fill(m):
        val = SITE.get(m.group(3)) or ""
        return m.group(1) + esc(str(val)) + m.group(4) if val else m.group(0)
    body = re.sub(r'(<(\w+)\b[^>]*\bdata-fill="(\w+)"[^>]*>)(</\2>)', fill, body)
    if SITE.get("phone"):
        tel = "tel:" + re.sub(r"[^0-9+]", "", SITE["phone"])
        body = re.sub(r'(data-tel\b[^>]*?)href="#offer"', r'\1href="%s"' % tel, body)
        body = re.sub(r'href="#offer"([^>]*?\bdata-tel\b)', r'href="%s"\1' % tel, body)
    if SITE.get("ownerPhoto"):
        img = '<img src="%s" alt="Photo of %s" width="800" height="1200" loading="lazy">' % (
            esc(SITE["ownerPhoto"]), esc(SITE.get("owner") or "the owner"))
        body = re.sub(r'(<div class="photo" data-photo="ownerPhoto"[^>]*>)(</div>)', r"\1" + img + r"\2", body)
    if SITE.get("story"):
        paras = "".join("<p>%s</p>" % esc(t) for t in SITE["story"])
        body = body.replace('<div class="story" id="story"></div>', '<div class="story" id="story">%s</div>' % paras)
    if SITE.get("areas"):
        lis = "".join("<li>%s</li>" % esc(a) for a in SITE["areas"])
        body = body.replace('<ul class="areas" id="areaList"></ul>', '<ul class="areas" id="areaList">%s</ul>' % lis)
    if SITE.get("formKey"):
        body = body.replace('<input type="hidden" name="access_key" id="f-key" value="">',
                            '<input type="hidden" name="access_key" id="f-key" value="%s">' % esc(SITE["formKey"]))
    if SITE.get("dealsClosed"):
        body = body.replace('<div class="stat" id="dealStat" hidden>', '<div class="stat" id="dealStat">')
    body = re.sub(r'<div class="preview" id="previewBar">.*?</div></div>\n?', "", body, count=1, flags=re.S)
    return body


def business_data():
    ld = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": "Cx2 Homebuyers LLC",
          "description": "Local, owner-run Houston company that makes as-is cash offers on houses in Greater Houston.",
          "areaServed": [{"@type": "City", "name": a + ", TX"} for a in SITE.get("areas", [])]}
    d = SITE.get("domain")
    if d:
        ld.update(logo=d + "/logo-512.png", image=d + "/logo-512.png", url=d)
    if SITE.get("phone"): ld["telephone"] = SITE["phone"]
    if SITE.get("email"): ld["email"] = SITE["email"]
    if SITE.get("googleUrl"): ld["sameAs"] = [SITE["googleUrl"]]
    if SITE.get("owner"): ld["founder"] = {"@type": "Person", "name": SITE["owner"]}
    return '<script type="application/ld+json">%s</script>' % json.dumps(ld).replace("</", "<\\/")


head, body = page.split("</style>", 1)
live = re.sub(r"live:\s*false,", "live: true, ", body, count=1)
live = prerender(live)
os.makedirs(os.path.join(here, "site"), exist_ok=True)
with open(os.path.join(here, "site/index.html"), "w") as f:
    f.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n')
    f.write(head + "</style>\n" + business_data() + "\n</head><body>\n" + live + "\n</body></html>\n")

# legal pages: src/legal/<name>.html wrapped in src/legal/shell.html -> site/<name>.html
shell = open(os.path.join(here, "src/legal/shell.html")).read()
for name in ("privacy", "terms"):
    body = open(os.path.join(here, "src/legal", name + ".html")).read()
    title = re.search(r"<!--TITLE:(.*?)-->", body).group(1)
    desc = re.search(r"<!--DESC:(.*?)-->", body).group(1)
    body = re.sub(r"<!--(TITLE|DESC):.*?-->\n", "", body)
    canon = (SITE.get("domain") or "") + "/" + name + ".html"
    out = (shell.replace("{{TITLE}}", title).replace("{{DESC}}", desc).replace("{{BODY}}", body.strip())
                .replace("{{CANON}}", canon))
    open(os.path.join(here, "site", name + ".html"), "w").write(out)
print("built body.html, site/index.html, site/privacy.html and site/terms.html")
