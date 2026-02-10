# Aaron J Girard - Personal Website

A Quarto-based academic website for hosting on GitHub Pages.

## Quick Start

### Prerequisites

1. Install [Quarto](https://quarto.org/docs/get-started/)
2. Install Git

### Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. Add your profile photo:
   - Save your photo as `images/profile.jpg`

3. Preview the site locally:
   ```bash
   quarto preview
   ```

4. Render the site:
   ```bash
   quarto render
   ```

### Deploy to GitHub Pages

#### Option 1: Using GitHub Actions (Recommended)

1. Create a new repository on GitHub

2. Push this code to your repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

3. Create `.github/workflows/publish.yml`:
   ```yaml
   on:
     push:
       branches: main

   name: Quarto Publish

   jobs:
     build-deploy:
       runs-on: ubuntu-latest
       permissions:
         contents: write
       steps:
         - name: Check out repository
           uses: actions/checkout@v4

         - name: Set up Quarto
           uses: quarto-dev/quarto-actions/setup@v2

         - name: Render and Publish
           uses: quarto-dev/quarto-actions/publish@v2
           with:
             target: gh-pages
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

4. Go to your repository Settings → Pages → Set source to "gh-pages" branch

#### Option 2: Manual Deployment

1. Render the site:
   ```bash
   quarto render
   ```

2. The output is in the `docs/` folder (configured in `_quarto.yml`)

3. Push to GitHub and set Pages source to `docs/` folder on `main` branch

### Customization

#### Update Content

- **Home page**: Edit `index.qmd`
- **Research**: Edit `research.qmd`
- **Teaching**: Edit `teaching.qmd`
- **Publications**: Edit `publications.qmd`
- **Gallery**: Edit `gallery.qmd`

#### Update Styling

- Edit `styles.css` for custom styles
- Change the theme in `_quarto.yml` (see [Quarto themes](https://quarto.org/docs/output-formats/html-themes.html))

#### Update Navigation

- Edit the `navbar` section in `_quarto.yml`

### Things to Update

**Note:** The academicons extension is already included in `_extensions/`. If you want to reinstall it fresh, run:
```bash
quarto add schochastics/academicons
```

## File Structure

```
.
├── _quarto.yml          # Main configuration
├── index.qmd            # Home page
├── research.qmd         # Research page
├── teaching.qmd         # Teaching page
├── publications.qmd     # Publications (with sidebar TOC)
├── gallery.qmd          # Gallery page
├── styles.css           # Custom CSS
├── images/
│   └── profile.png      # Profile photo 
└── docs/                # Generated site (after render)
```

## License

Content © Aaron J Girard. All rights reserved.