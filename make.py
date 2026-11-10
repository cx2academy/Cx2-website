"""Builds the website from src/page.html.

  python3 make.py   ->  body.html        (preview page for Claude)
                        site/index.html  (the real website: Cloudflare Pages publishes the `site` folder)
                        site/privacy.html, site/terms.html  (from src/legal/)
                        site/about.html, site/how-to-check-a-cash-home-buyer.html, site/404.html  (from src/pages/)
                        site/robots.txt, site/sitemap.xml, site/_headers

Edit your details in the SITE block near the bottom of src/page.html, then run this again.
Put photos (owner.jpg, hero.jpg) inside the `site` folder.

For the real website, your details (name, phone, email, hours, story, areas, photo and
business data) are written straight into the HTML, so search engines and AI tools that
don't run JavaScript still see them. The preview banner is left out of the real site.
"""
import datetime, hashlib, html, json, os, re
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


DESC_SHORT = ("Cx2 Homebuyers is a local, owner-run Houston company that makes fair, as-is cash offers on houses. "
              "Sellers pay no commissions, repairs or closing costs, and there's never any obligation.")
D = (SITE.get("domain") or "").rstrip("/")
BIZ, COOPER, WEBSITE = D + "/#business", D + "/#cooper", D + "/#website"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def hours_spec(text):
    """'Mon to Sat, 9am to 7pm' -> schema.org OpeningHoursSpecification (skipped if the format is different)."""
    m = re.match(r"(\w{3}) to (\w{3}), (\d{1,2})(am|pm) to (\d{1,2})(am|pm)$", text or "")
    if not m:
        return None
    short = [d[:3] for d in DAYS]
    if m.group(1) not in short or m.group(2) not in short:
        return None
    days = DAYS[short.index(m.group(1)):short.index(m.group(2)) + 1]
    t = lambda h, ap: "%02d:00" % (int(h) % 12 + (12 if ap == "pm" else 0))
    return [{"@type": "OpeningHoursSpecification", "dayOfWeek": days,
             "opens": t(m.group(3), m.group(4)), "closes": t(m.group(5), m.group(6))}]


def business_node():
    b = {"@type": "LocalBusiness", "@id": BIZ, "name": "Cx2 Homebuyers", "legalName": "Cx2 Homebuyers LLC",
         "description": DESC_SHORT, "url": D + "/", "logo": D + "/logo-512.png",
         "image": [D + "/og.jpg", D + "/logo-512.png"],
         "address": {"@type": "PostalAddress", "addressLocality": "Houston", "addressRegion": "TX", "addressCountry": "US"},
         "areaServed": [{"@type": "City", "name": a + ", TX"} for a in SITE.get("areas", [])]}
    if SITE.get("phone"): b["telephone"] = "+1-" + "-".join(re.findall(r"\d+", SITE["phone"]))
    if SITE.get("email"): b["email"] = SITE["email"]
    hs = hours_spec(SITE.get("hours"))
    if hs: b["openingHoursSpecification"] = hs
    if SITE.get("owner"): b["founder"] = {"@id": COOPER}
    same = [u for u in [SITE.get("googleUrl")] + list(SITE.get("profiles") or []) if u]
    if same: b["sameAs"] = same
    return b


def person_node():
    p = {"@type": "Person", "@id": COOPER, "name": SITE.get("owner") or "Owner", "jobTitle": "Owner",
         "worksFor": {"@id": BIZ}, "url": D + "/about.html"}
    if SITE.get("ownerPhoto"): p["image"] = D + "/" + SITE["ownerPhoto"]
    if SITE.get("ownerProfiles"): p["sameAs"] = list(SITE["ownerProfiles"])
    return p


def text_of(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def faq_node(body):
    qs = []
    for m in re.finditer(r'<details data-k="[^"]*"><summary>(.*?)<svg.*?</summary>(.*?)</details>', body, re.S):
        qs.append({"@type": "Question", "name": text_of(m.group(1)),
                   "acceptedAnswer": {"@type": "Answer", "text": text_of(m.group(2))}})
    return {"@type": "FAQPage", "@id": D + "/#faq", "url": D + "/", "mainEntity": qs}


def ld_script(nodes):
    data = {"@context": "https://schema.org", "@graph": nodes}
    return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def business_data(body):
    website = {"@type": "WebSite", "@id": WEBSITE, "name": "Cx2 Homebuyers", "url": D + "/", "publisher": {"@id": BIZ}}
    return ld_script([business_node(), person_node(), website, faq_node(body)])


head, body = page.split("</style>", 1)
live = re.sub(r"live:\s*false,", "live: true, ", body, count=1)
live = prerender(live)
os.makedirs(os.path.join(here, "site"), exist_ok=True)
with open(os.path.join(here, "site/index.html"), "w") as f:
    f.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n')
    f.write(head + "</style>\n" + business_data(live) + "\n</head><body>\n" + live + "\n</body></html>\n")

# extra pages: src/legal/<name>.html and src/pages/<name>.html wrapped in src/legal/shell.html -> site/<name>.html
shell = open(os.path.join(here, "src/legal/shell.html")).read()
OG_IMG = D + "/og.jpg"


def page_head(title, desc, canon, og_type="website"):
    t = esc(title + " | Cx2 Homebuyers")
    return "\n".join([
        '<meta property="og:type" content="%s">' % og_type,
        '<meta property="og:site_name" content="Cx2 Homebuyers">',
        '<meta property="og:url" content="%s">' % canon,
        '<meta property="og:title" content="%s">' % t,
        '<meta property="og:description" content="%s">' % esc(desc),
        '<meta property="og:image" content="%s">' % OG_IMG,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">'])


def build_page(folder, name):
    body = open(os.path.join(here, folder, name + ".html")).read()
    title = re.search(r"<!--TITLE:(.*?)-->", body).group(1)
    desc = re.search(r"<!--DESC:(.*?)-->", body).group(1)
    body = re.sub(r"<!--(TITLE|DESC):.*?-->\n", "", body)
    if "{{STORY}}" in body:
        body = body.replace("{{STORY}}", "\n".join("<p>%s</p>" % esc(t) for t in SITE.get("story", [])))
    canon = D + "/" + name + ".html"
    extra = ""
    if name == "about":
        extra = page_head(title, desc, canon) + "\n" + ld_script([
            {"@type": "AboutPage", "@id": canon, "url": canon, "name": title, "description": desc,
             "about": {"@id": BIZ}, "mainEntity": {"@id": COOPER}, "isPartOf": {"@id": WEBSITE}},
            business_node(), person_node()])
    elif name == "how-to-check-a-cash-home-buyer":
        extra = page_head(title, desc, canon, "article") + "\n" + ld_script([
            {"@type": "Article", "@id": canon + "#article", "headline": "How to check if a cash home buyer is legit",
             "description": desc, "url": canon, "mainEntityOfPage": canon, "image": OG_IMG,
             "datePublished": "2026-11-10", "dateModified": LASTMOD.get(name + ".html", {}).get("date", "2026-11-10"),
             "author": {"@id": COOPER}, "publisher": {"@id": BIZ}, "isPartOf": {"@id": WEBSITE}},
            business_node(), person_node()])
    elif name in ("privacy", "terms"):
        extra = page_head(title, desc, canon)
    out = (shell.replace("{{TITLE}}", title).replace("{{DESC}}", desc).replace("{{BODY}}", body.strip())
                .replace("{{CANON}}", canon).replace("{{HEAD}}", extra))
    if name == "404":   # served at any missing path, so resolve links from the site root and keep it out of search
        out = out.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">\n<meta name="robots" content="noindex">', 1)
        out = re.sub(r'<link rel="canonical"[^>]*>\n', "", out)
        out = out.replace("{{HEAD}}\n", "")
    open(os.path.join(here, "site", name + ".html"), "w").write(out)


# sitemap dates: a page's date changes only when its built HTML actually changes (tracked in src/lastmod.json)
LASTMOD_FILE = os.path.join(here, "src/lastmod.json")
LASTMOD = json.load(open(LASTMOD_FILE)) if os.path.exists(LASTMOD_FILE) else {}
PAGES = [("legal", "privacy"), ("legal", "terms"), ("pages", "about"),
         ("pages", "how-to-check-a-cash-home-buyer"), ("pages", "404")]
SITEMAP = ["index.html", "about.html", "how-to-check-a-cash-home-buyer.html", "privacy.html", "terms.html"]
today = datetime.date.today().isoformat()


def stamp(fname):
    digest = hashlib.sha256(open(os.path.join(here, "site", fname), "rb").read()).hexdigest()
    rec = LASTMOD.get(fname)
    if not rec or rec["hash"] != digest:
        LASTMOD[fname] = {"hash": digest, "date": today}
        return True
    return False


for folder, name in PAGES:
    build_page("src/" + folder, name)
changed = [f for f in SITEMAP if stamp(f)]
if "how-to-check-a-cash-home-buyer.html" in changed:   # its schema shows the modified date, so rebuild once with it
    build_page("src/pages", "how-to-check-a-cash-home-buyer")
    stamp("how-to-check-a-cash-home-buyer.html")
json.dump(LASTMOD, open(LASTMOD_FILE, "w"), indent=1, sort_keys=True)

open(os.path.join(here, "site/robots.txt"), "w").write(
    "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % D)
with open(os.path.join(here, "site/sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for fname in SITEMAP:
        loc = D + "/" if fname == "index.html" else D + "/" + fname
        f.write("  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (loc, LASTMOD[fname]["date"]))
    f.write("</urlset>\n")
# Cloudflare Pages headers: keep the *.pages.dev copies out of search (the real site is the custom domain)
open(os.path.join(here, "site/_headers"), "w").write(
    "https://:project.pages.dev/*\n  X-Robots-Tag: noindex\n\n"
    "https://:version.:project.pages.dev/*\n  X-Robots-Tag: noindex\n\n"
    "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
print("built body.html, site/index.html, %s, robots.txt, sitemap.xml and _headers"
      % ", ".join("site/%s.html" % n for _, n in PAGES))
