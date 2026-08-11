#!/usr/bin/env node
/**
 * Dependency Checker for Screenshot Skill
 * 
 * Checks if Playwright and required packages are installed.
 * Returns instructions for user to install if missing.
 * 
 * Usage:
 *   node scripts/check-deps.mjs
 * 
 * Exit codes:
 *   0 - All dependencies available
 *   1 - Dependencies missing
 */

import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';

const require = createRequire(import.meta.url);

const REQUIRED_PACKAGES = [
  'playwright',
  'playwright-extra',
  'puppeteer-extra-plugin-stealth',
];

function checkPackage(name) {
  try {
    require(name);
    return true;
  } catch {
    return false;
  }
}

function checkChromium() {
  try {
    // Try to find chromium in playwright's cache
    const result = execSync('npx playwright install chromium --dry-run 2>&1 || echo "not installed"', {
      encoding: 'utf8',
      timeout: 15000,
      windowsHide: true,
    });
    
    // If it says "is already installed" or returns empty, chromium exists
    if (!result.includes('Downloading') && !result.includes('not installed')) {
      return true;
    }
    
    // Check if chromium directory exists
    const path = require('path');
    const homeDir = process.env.HOME || process.env.USERPROFILE || '';
    const playwrightDir = path.join(homeDir, 'AppData', 'Local', 'ms-playwright');
    
    try {
      require('fs').accessSync(playwrightDir);
      return true;
    } catch {
      return false;
    }
  } catch {
    // Check local cache as fallback
    const path = require('path');
    const playwrightDir = path.join(__dirname, '..', '..', 'node_modules', 'playwright');
    try {
      require('fs').accessSync(path.join(playwrightDir, 'chromium'));
      return true;
    } catch {
      return false;
    }
  }
}

// Main
function main() {
  const missingPackages = REQUIRED_PACKAGES.filter(pkg => !checkPackage(pkg));
  const hasChromium = checkChromium();

  if (missingPackages.length === 0 && hasChromium) {
    console.log(JSON.stringify({
      ready: true,
      message: 'All dependencies are available',
    }));
    process.exit(0);
  }

  // Build response
  const response = {
    ready: false,
    message: '',
    missingPackages: [],
    needsBrowser: false,
    installOptions: null,
  };

  if (missingPackages.length > 0) {
    response.missingPackages = missingPackages;
    response.message = `Missing packages: ${missingPackages.join(', ')}`;
  }
  
  if (!hasChromium) {
    response.needsBrowser = true;
    response.message += (response.message ? '; ' : '') + 'Chromium browser not installed';
  }

  // Provide install instructions
  response.installOptions = {
    global: {
      description: 'Install globally (recommended for frequent use)',
      commands: [
        'npm install -g playwright playwright-extra puppeteer-extra-plugin-stealth',
        'npx playwright install chromium --with-deps',
      ],
    },
    npx: {
      description: 'Use npx without global install',
      commands: [
        'npx playwright install chromium --with-deps',
      ],
    },
  };

  console.error(JSON.stringify(response, null, 2));
  process.exit(1);
}

main();
