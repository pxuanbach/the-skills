#!/usr/bin/env node
/**
 * Screenshot Tool for Agentic Skills (Stealth Mode)
 * 
 * Captures a screenshot of a web page using Playwright with stealth configurations
 * to bypass anti-bot detection (Cloudflare, etc.)
 * 
 * Usage:
 *   node screenshot.mjs <url> [options]
 * 
 * Options:
 *   --output <path>    Output file path (default: auto-generated in .temp/)
 *   --format <fmt>    Output format: webp, png, jpeg (default: webp)
 *   --full-page       Capture full page
 *   --viewport        Capture only viewport (default)
 *   --timeout <ms>    Page load timeout in ms (default: 30000)
 *   --width <px>      Viewport width (default: 1280)
 *   --height <px>     Viewport height (default: 720)
 *   --workspace <dir> Workspace directory for .temp/ (default: current dir)
 * 
 * Exit codes:
 *   0 - Success
 *   1 - Error (see stderr for details)
 *   2 - Blocked page (Cloudflare, CAPTCHA, etc.)
 *   3 - Timeout
 * 
 * Required dependencies:
 *   npm install -g playwright playwright-extra puppeteer-extra-plugin-stealth
 *   npx playwright install chromium
 */

import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Default config
const DEFAULT_FORMAT = 'webp';
const DEFAULT_TIMEOUT = 30000;
const DEFAULT_VIEWPORT = { width: 1280, height: 720 };
const DEFAULT_FULL_PAGE = false; // Capture viewport only by default

// Blocked page indicators - more specific to avoid false positives
const BLOCKED_PATTERNS = [
  /^captcha$/i,
  /^challenge$/i,
  /please wait while your request is being processed/i,
  /\u5f25/, // Cloudflare challenge page text
  /Checking if the site connection is secure/i,
  /ray id/i,
  /cloudflare ray id/i,
];

const BLOCKED_TITLES = [
  /access denied/i,
  /blocked/i,
  /forbidden/i,
  /security check/i,
];

// Realistic browser fingerprints
const FINGERPRINTS = [
  {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    hasTouch: false,
    isMobile: false,
  },
  {
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
    hasTouch: false,
    isMobile: false,
  },
  {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    viewport: { width: 1366, height: 768 },
    deviceScaleFactor: 1,
    hasTouch: false,
    isMobile: false,
  },
];

function parseArgs(argv) {
  const args = {
    url: null,
    output: null,
    format: DEFAULT_FORMAT,
    fullPage: DEFAULT_FULL_PAGE,
    timeout: DEFAULT_TIMEOUT,
    viewport: null,
    workspace: process.cwd(),
    stealth: true,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    
    if (arg === '--output' && argv[i + 1]) {
      args.output = argv[++i];
    } else if (arg === '--format' && argv[i + 1]) {
      args.format = argv[++i].toLowerCase();
    } else if (arg === '--full-page') {
      args.fullPage = true;
    } else if (arg === '--viewport' || arg === '-v') {
      args.fullPage = false;
    } else if (arg === '--timeout' && argv[i + 1]) {
      args.timeout = parseInt(argv[++i], 10);
    } else if (arg === '--width' && argv[i + 1]) {
      const width = parseInt(argv[++i], 10);
      args.viewport = args.viewport || { width, height: 720 };
      args.viewport.width = width;
    } else if (arg === '--height' && argv[i + 1]) {
      const height = parseInt(argv[++i], 10);
      args.viewport = args.viewport || { width: 1280, height: height };
      args.viewport.height = height;
    } else if (arg === '--workspace' && argv[i + 1]) {
      args.workspace = argv[++i];
    } else if (arg === '--no-stealth') {
      args.stealth = false;
    } else if (!arg.startsWith('--') && !args.url) {
      args.url = arg;
    }
  }

  return args;
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function generateOutputPath(workspace, format) {
  const tempDir = path.join(workspace, '.temp');
  ensureDir(tempDir);
  
  const timestamp = Date.now();
  const filename = `screenshot-${timestamp}.${format}`;
  return path.join(tempDir, filename);
}

function checkBlockedPage(content) {
  if (!content) return false;
  
  const lowerContent = content.toLowerCase();
  return BLOCKED_PATTERNS.some(pattern => pattern.test(lowerContent));
}

function selectFingerprint() {
  const index = Math.floor(Math.random() * FINGERPRINTS.length);
  return FINGERPRINTS[index];
}

async function takeScreenshot(url, options) {
  const {
    output,
    format,
    fullPage,
    timeout,
    viewport: customViewport,
    workspace,
    stealth: useStealth,
  } = options;

  const outputPath = output || generateOutputPath(workspace, format);

  if (!['webp', 'png', 'jpeg', 'jpg'].includes(format)) {
    throw new Error(`Unsupported format: ${format}. Use webp, png, or jpeg.`);
  }

  const playwrightFormat = format === 'jpg' ? 'jpeg' : format;

  // Select fingerprint
  const fingerprint = selectFingerprint();
  const viewport = customViewport || fingerprint.viewport;

  let browser = null;
  
  try {
    // Apply stealth plugin
    if (useStealth) {
      console.error(`Applying stealth configuration...`);
      const stealthPlugin = stealth();
      chromium.use(stealthPlugin);
    }

    // Launch args for anti-detection
    const launchArgs = [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-blink-features=AutomationControlled',
      '--disable-blink-features=IsRunningOnGpuBridgeHost',
      '--disable-features=IsolateOrigins,site-per-process',
      '--ash-no-nudges',
      '--disable-background-networking',
      '--disable-default-apps',
      '--disable-extensions',
      '--disable-hang-monitor',
      '--disable-popup-blocking',
      '--disable-prompt-on-repost',
      '--disable-sync',
      '--disable-translate',
      '--metrics-recording-only',
      '--no-first-run',
      '--safebrowsing-disable-auto-update',
      '--disable-renderer-backgrounding',
      '--disable-background-timer-throttling',
    ];

    console.error(`Launching headless browser (stealth mode)...`);
    browser = await chromium.launch({ 
      headless: true,
      args: launchArgs,
    });

    // Create context with fingerprint
    const context = await browser.newContext({
      viewport: viewport,
      deviceScaleFactor: fingerprint.deviceScaleFactor,
      hasTouch: fingerprint.hasTouch,
      isMobile: fingerprint.isMobile,
      userAgent: fingerprint.userAgent,
      locale: 'en-US',
      timezoneId: 'America/New_York',
      permissions: ['geolocation'],
    });

    const page = await context.newPage();

    // Inject stealth scripts
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
      });
      
      Object.defineProperty(navigator, 'plugins', {
        get: () => [
          { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
          { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
          { name: 'Native Client', filename: 'internal-nacl-plugin' },
        ],
      });
      
      Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
      });
      
      // Override permissions.query
      const originalQuery = window.navigator.permissions.query;
      window.navigator.permissions.query = (parameters) => {
        if (['notifications', 'persistent-storage', 'push', 'geolocation'].includes(parameters.name)) {
          return Promise.resolve({ state: Notification.permission });
        }
        return originalQuery(parameters);
      };
      
      // Remove automation indicators
      window.chrome = window.chrome || {};
      window.chrome.runtime = window.chrome.runtime || {};
    });

    // Set timeouts
    page.setDefaultTimeout(timeout);
    page.setDefaultNavigationTimeout(timeout);

    // Navigate to URL
    console.error(`Navigating to ${url}...`);
    
    let response = null;
    let attempts = 0;
    const maxAttempts = 2;
    
    while (attempts < maxAttempts && !response) {
      attempts++;
      try {
        response = await page.goto(url, { 
          waitUntil: 'domcontentloaded',
          timeout: timeout,
        });
      } catch (e) {
        if (attempts < maxAttempts) {
          console.error(`Retry ${attempts}/${maxAttempts}...`);
          await page.waitForTimeout(2000);
        } else {
          throw e;
        }
      }
    }
    
    if (!response) {
      throw new Error('No response received from the page');
    }

    const status = response.status();
    console.error(`Page loaded with status: ${status}`);

    if (status >= 400) {
      throw new Error(`Page returned HTTP ${status}`);
    }

    // Wait for potential Cloudflare challenge
    console.error(`Waiting for page to render...`);
    await page.waitForTimeout(4000);

    // Check for blocked pages
    const title = await page.title();
    const bodyText = await page.evaluate(() => document.body?.innerText || '').catch(() => '');
    
    console.error(`Page title: ${title}`);
    
    const titleBlocked = BLOCKED_TITLES.some(p => p.test(title));
    const bodyBlocked = checkBlockedPage(bodyText);
    
    if (titleBlocked || bodyBlocked) {
      throw Object.assign(
        new Error('Page is blocked (Cloudflare, CAPTCHA, or anti-bot protection detected)'), 
        { code: 2 }
      );
    }

    // Wait for page to fully load
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(1500);

    // Take screenshot
    console.error(`Taking ${fullPage ? 'full page' : 'viewport'} screenshot...`);
    
    const screenshotOptions = {
      type: playwrightFormat,
      fullPage: fullPage,
    };

    if (playwrightFormat === 'jpeg') {
      screenshotOptions.quality = 85;
    }

    const screenshot = await page.screenshot(screenshotOptions);
    fs.writeFileSync(outputPath, screenshot);
    console.error(`Screenshot saved to: ${outputPath}`);

    return {
      path: outputPath,
      format: format,
      fullPage: fullPage,
      size: screenshot.length,
    };

  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

function checkDependencies() {
  const deps = ['playwright', 'playwright-extra', 'puppeteer-extra-plugin-stealth'];
  const missing = [];
  
  for (const dep of deps) {
    try {
      require(dep);
    } catch {
      missing.push(dep);
    }
  }
  
  if (missing.length > 0) {
    console.error(JSON.stringify({
      success: false,
      error: 'Missing dependencies: ' + missing.join(', '),
      code: 10,
      installHint: {
        global: 'npm install -g playwright playwright-extra puppeteer-extra-plugin-stealth && npx playwright install chromium',
        npx: 'npx playwright install chromium',
      }
    }));
    return false;
  }
  return true;
}

async function main() {
  // Check dependencies first
  if (!checkDependencies()) {
    process.exit(10);
  }

  const args = parseArgs(process.argv.slice(2));

  if (!args.url) {
    console.error(JSON.stringify({
      error: 'No URL provided. Usage: node screenshot.mjs <url> [options]'
    }));
    process.exit(1);
  }

  try {
    const result = await takeScreenshot(args.url, args);
    console.log(JSON.stringify({
      success: true,
      ...result
    }));
    process.exit(0);
  } catch (error) {
    const exitCode = error.code || 1;
    console.error(JSON.stringify({
      success: false,
      error: error.message,
      code: exitCode
    }));
    process.exit(exitCode);
  }
}

main();
