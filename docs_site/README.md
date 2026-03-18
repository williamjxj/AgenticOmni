# docs_site Usage Guide

This folder contains all files and configuration needed to generate the GitHub Pages documentation site for the OmniAI project.

## Contents
- `_includes/` — Jekyll HTML snippets (navigation, etc.)
- `_layouts/` — Jekyll page layouts
- `_config.yml` — Jekyll configuration file
- `index.md` — Main landing page for the documentation site
- `GITHUB_PAGES_SETUP.md` — Setup and deployment instructions for GitHub Pages
- `QUICKSTART_HF.md` — HuggingFace integration quickstart guide

## How to Use
1. **GitHub Pages Source**: In your repository settings, set GitHub Pages to use the `/docs_site` folder as the publishing source.
2. **Local Preview**: To preview the site locally, install Jekyll and run `bundle exec jekyll serve` from within `docs_site/`.
3. **Customizing**: Edit the files in this folder to update the documentation site. Use `_includes/` and `_layouts/` for reusable HTML and layouts.
4. **Adding Docs**: Place new Markdown files here or link to files in the main `docs/` folder as needed.

## Notes
- This folder is for documentation site generation only. It does not affect the core application code.
- For app documentation, see the main `README.md` and `docs/` folder in the project root.

---
For more, see `GITHUB_PAGES_SETUP.md` in this folder.