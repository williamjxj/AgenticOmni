# GitHub Pages Setup for AgenticOmni

This directory contains the configuration for the AgenticOmni documentation site hosted on GitHub Pages.

## 🌐 Live Site

Once deployed, your site will be available at: **https://williamjxj.github.io/AgenticOmni**

Links to documentation pages will use `.html` extensions (e.g., `/docs/QUICKSTART.html`) for explicit HTML rendering.

## 📁 Files Overview

- `_config.yml` - Jekyll configuration
- `index.md` - Homepage
- `_layouts/default.html` - Custom page layout
- `Gemfile` - Ruby dependencies for Jekyll
- `.github/workflows/pages.yml` - GitHub Actions workflow for automatic deployment
- `docs/` - Documentation files (automatically included)
- `assets/` - Images and static assets

## 🚀 Deployment Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/williamjxj/AgenticOmni
2. Click **Settings** > **Pages** (in the left sidebar)
3. Under **Source**, select:
   - Source: **GitHub Actions** (recommended)
   - Or select **Deploy from a branch** and choose **main** and **/ (root)**

### 2. Push Your Changes

```bash
git add .
git commit -m "Add GitHub Pages configuration"
git push origin main
```

### 3. Wait for Deployment

- Go to **Actions** tab in your GitHub repository
- You should see a "Deploy Jekyll Site to GitHub Pages" workflow running
- Once complete (usually 1-2 minutes), your site will be live!

### 4. Access Your Site

Visit: **https://williamjxj.github.io/AgenticOmni**

## 🎨 Customization

### URL Structure

This site is configured to use explicit `.html` extensions in URLs (e.g., `/docs/QUICKSTART.html` instead of `/docs/QUICKSTART`). This matches the behavior of your agentic-langgraph-accounting project.

The configuration is set in `_config.yml`:
```yaml
permalink: /:path/:basename.html
```

### Change Theme

Edit `_config.yml` and change the `theme` line:

```yaml
theme: jekyll-theme-cayman  # Current theme

# Available GitHub Pages themes:
# theme: jekyll-theme-minimal
# theme: jekyll-theme-slate
# theme: jekyll-theme-architect
# theme: jekyll-theme-merlot
# theme: jekyll-theme-tactile
```

### Update Site Information

Edit `_config.yml`:

```yaml
title: AgenticOmni
description: Your custom description
url: https://williamjxj.github.io
```

### Modify Homepage

Edit `index.md` to customize your landing page.

### Add New Pages

Create new `.md` files in the root or `docs/` directory. They'll automatically be available at their respective URLs.

## 🧪 Test Locally

To test your site locally before deploying:

1. Install Ruby (if not already installed)
2. Install dependencies:
   ```bash
   bundle install
   ```

3. Run Jekyll locally:
   ```bash
   bundle exec jekyll serve
   ```

4. Open http://localhost:4000 in your browser

## 📝 Adding Content

### Adding Documentation

Simply add `.md` files to the `docs/` folder. They'll automatically be available on the site.

### Adding Images

Place images in the `assets/` folder and reference them in markdown:

```markdown
![Alt text](assets/your-image.png)
```

### Linking Between Pages

Use relative links with .html extensions in markdown:

```markdown
[Quick Start](docs/QUICKSTART.html)
[Configuration](docs/environment.html)
[Home](index.html)
```

## 🔧 Troubleshooting

### Site Not Building

1. Check the **Actions** tab for build errors
2. Ensure all image paths in markdown are correct
3. Verify `_config.yml` syntax

### Changes Not Appearing

1. Wait 1-2 minutes after pushing
2. Hard refresh your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
3. Check if the GitHub Action completed successfully

### 404 Errors

1. Ensure GitHub Pages is enabled in repository settings
2. Check that the branch is correct (usually `main`)
3. Verify file names match exactly (markdown is case-sensitive)

## 📚 Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Jekyll Themes](https://pages.github.com/themes/)
- [Markdown Guide](https://www.markdownguide.org/)

## 🤝 Contributing

To contribute to the documentation:

1. Edit markdown files in the repository
2. Test locally with `bundle exec jekyll serve`
3. Commit and push changes
4. GitHub Actions will automatically rebuild the site

---

**Note**: After you enable GitHub Pages, the first deployment might take 5-10 minutes. Subsequent deployments are usually faster (1-2 minutes).
