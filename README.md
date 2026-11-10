# Cx2 Homebuyers website

Landing page for Cx2 Homebuyers LLC (Greater Houston).

- Edit content and your details in the `SITE` block at the bottom of `src/page.html`. `make.py` writes them straight into `site/index.html` so crawlers that skip JavaScript still see them.
- Run `python3 make.py` to rebuild `site/index.html`.
- Cloudflare Pages publishes the `site` folder (build command: none, output directory: `site`).
- The offer form posts to Web3Forms, which emails each request. Put the access key in `formKey` in the SITE block.
- Put photos (e.g. `owner.webp`, `hero.jpg`) in `site/` and reference them in `SITE`.
- Other pages live in `src/legal/` (privacy, terms) and `src/pages/` (about, the "how to check a cash buyer" guide, 404). `make.py` wraps them in `src/legal/shell.html` and also writes `robots.txt`, `sitemap.xml` and `_headers`.
- Structured data (business, owner, website and FAQs) is built by `make.py` from the `SITE` block and the visible FAQ, so the two always match. Add profile links to `googleUrl`, `profiles` and `ownerProfiles`.
- Sitemap dates come from `src/lastmod.json`, which changes a page's date only when its built HTML changes.
- `node tools/og_image.js` redraws `site/og.jpg`, the share image (serve `site/` on port 8765 first).
