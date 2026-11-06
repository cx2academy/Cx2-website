# Cx2 Homebuyers website

Landing page for Cx2 Homebuyers LLC (Greater Houston).

- Edit content and your details in the `SITE` block at the bottom of `src/page.html`. `make.py` writes them straight into `site/index.html` so crawlers that skip JavaScript still see them.
- Run `python3 make.py` to rebuild `site/index.html`.
- Netlify publishes the `site` folder (see `netlify.toml`). The offer form uses Netlify Forms.
- Put photos (e.g. `owner.jpg`, `hero.jpg`) in `site/` and reference them in `SITE`.
