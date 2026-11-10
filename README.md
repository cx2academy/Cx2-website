# Cx2 Homebuyers website

Landing page for Cx2 Homebuyers LLC (Greater Houston).

- Edit content and your details in the `SITE` block at the bottom of `src/page.html`. `make.py` writes them straight into `site/index.html` so crawlers that skip JavaScript still see them.
- Run `python3 make.py` to rebuild `site/index.html`.
- Cloudflare Pages publishes the `site` folder (build command: none, output directory: `site`).
- The offer form posts to Web3Forms, which emails each request. Put the access key in `formKey` in the SITE block.
- Put photos (e.g. `owner.webp`, `hero.jpg`) in `site/` and reference them in `SITE`.
