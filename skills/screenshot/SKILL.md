---
name: screenshot
description: Capture a screenshot of a web page and save it to the .temp folder in the current workspace. Use when the user wants to take a screenshot of a URL, capture a page visually, or save a web page as an image.
version: 1.0.0
allowed-tools:
  - Bash(node skills/screenshot/scripts/check-deps.mjs)
  - Bash(node skills/screenshot/scripts/screenshot.mjs *)
  - Bash(node skills/screenshot/scripts/validate-url.mjs *)
  - Bash(pwd)
---

# Screenshot Skill

Save a screenshot of any URL to `.temp/` in the current workspace.

## Setup

Run `check-deps.mjs` first to check if Playwright is installed.

If packages are missing, ask the user to choose:

### Option 1: Global Install (Recommended)
```bash
npm install -g playwright playwright-extra puppeteer-extra-plugin-stealth
npx playwright install chromium --with-deps
```

### Option 2: NPX
```bash
npx playwright install chromium --with-deps
```

## Workflow

1. Run `check-deps.mjs`
2. If dependencies are missing, wait for the user to install them
3. Validate the URL with `validate-url.mjs <url>`
4. Run `screenshot.mjs <url> [options]`
5. Return the saved file path

## Commands

```bash
# Check dependencies
node skills/screenshot/scripts/check-deps.mjs
# Exit 0 = ready, Exit 1 = missing packages

# Validate URL
node skills/screenshot/scripts/validate-url.mjs https://example.com/
# Exit 0 = valid, Exit 1 = invalid

# Take screenshot
node skills/screenshot/scripts/screenshot.mjs https://example.com/
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `url` | required | The URL to screenshot |
| `--format <fmt>` | `webp` | Output format: `webp`, `png`, `jpeg` |
| `--viewport` | viewport | Capture viewport only |
| `--full-page` | - | Capture full page |
| `--timeout <ms>` | `30000` | Page load timeout |

## Output

```
{workspace}/.temp/screenshot-{timestamp}.{format}
```

The agent creates `.temp/` if it doesn't exist.

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 10 | Missing dependencies | Show install instructions |
| 1 | Invalid URL | Report validation error |
| 2 | Page blocked | Report Cloudflare/CAPTCHA |
| 3 | Timeout | Report timeout after 30s |
| 1 | HTTP error | Report status code |

## Stealth Mode

The script applies browser fingerprint spoofing and Cloudflare challenge detection. This bypasses anti-bot protection on most websites.
