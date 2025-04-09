# GM Profile Static Site Generator

This repository automatically generates a static website from your StartPlaying.games GM profile. It scrapes your game listings and creates a customized site where you can track analytics and run your own ads.

## Features

- Automatically crawls your StartPlaying.games GM profile
- Creates static HTML pages for each game
- Includes Google Analytics integration
- Deploys to GitHub Pages
- Runs daily or on-demand via GitHub Actions

## Setup Instructions

### 1. Fork this repository

Click the "Fork" button at the top right of this repository to create your own copy.

### 2. Configure your settings

Edit the `scraper.py` file to update these values:

- `GM_PROFILE_URL`: Change to your StartPlaying.games GM profile URL
- `ANALYTICS_TAG`: Replace `YOUR-ANALYTICS-ID` with your Google Analytics tracking ID

### 3. Enable GitHub Pages

1. Go to your repository's Settings
2. Navigate to "Pages" in the sidebar
3. Under "Source", select "GitHub Actions"
4. Save the changes

### 4. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. You'll see the "Generate Static Site" workflow

### 5. Run the workflow

You can run the workflow manually:
1. Go to the "Actions" tab
2. Select "Generate Static Site" workflow
3. Click "Run workflow"

The site will also update automatically every day at midnight UTC.

### 6. Access your site

Your site will be available at: `https://[your-github-username].github.io/[repository-name]/`

## Customization

### Templates

Edit the templates in the `templates` directory to customize the look and feel:
- `base.html`: The main layout template
- `index.html`: The homepage listing all games
- `game.html`: Individual game page template

### Styling

The site uses Tailwind CSS for styling. You can modify the classes in the templates to change the appearance.

### Adding Ads

To add your own ads, edit the template files and insert your ad code where appropriate.

## Troubleshooting

### The scraper isn't finding my games

The HTML structure of StartPlaying.games may change over time. If the scraper stops working, you may need to update the CSS selectors in the `scraper.py` file.

### GitHub Actions aren't running

Make sure you've enabled GitHub Actions for your repository and that you have the necessary permissions.