#!/usr/bin/env node
/**
 * URL Validator for Screenshot Skill
 * 
 * Validates URL format and checks for common issues.
 * 
 * Usage:
 *   node scripts/validate-url.mjs <url>
 * 
 * Exit codes:
 *   0 - Valid URL
 *   1 - Invalid URL format
 *   2 - URL is a file path or local address (not allowed for screenshots)
 */

import { URL } from 'node:url';

const INVALID_LOCALES = [
  'localhost',
  '127.0.0.1',
  '0.0.0.0',
  '::1',
  'file://',
  'ftp://',
];

const HTTPS_ONLY = false; // Allow http for testing

function isValidUrl(str) {
  if (!str || typeof str !== 'string') {
    return { valid: false, error: 'URL is empty or not a string' };
  }

  // Trim whitespace
  str = str.trim();

  // Check for basic URL structure
  if (!str.includes('://') && !str.startsWith('//')) {
    // Try adding https://
    str = 'https://' + str;
  }

  let url;
  try {
    url = new URL(str);
  } catch (e) {
    return { valid: false, error: `Invalid URL format: ${e.message}` };
  }

  // Check protocol
  if (!HTTPS_ONLY && !['http:', 'https:'].includes(url.protocol)) {
    return { valid: false, error: `Unsupported protocol: ${url.protocol}. Only http and https are supported.` };
  }

  if (HTTPS_ONLY && url.protocol !== 'https:') {
    return { valid: false, error: 'Only HTTPS URLs are allowed for screenshots.' };
  }

  // Check for local addresses
  const hostname = url.hostname.toLowerCase();
  if (INVALID_LOCALES.some(locale => hostname === locale || hostname.startsWith(locale + ':'))) {
    return { valid: false, error: 'Local addresses (localhost, 127.0.0.1, file://, etc.) cannot be screenshot.' };
  }

  // Check for private IP ranges (basic check)
  const privatePatterns = [
    /^10\./,
    /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
    /^192\.168\./,
    /^169\.254\./, // Link-local
  ];

  // Skip for hostnames that aren't IPs
  if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
    if (privatePatterns.some(pattern => pattern.test(hostname))) {
      return { valid: false, error: 'Private IP addresses cannot be screenshot.' };
    }
  }

  // Check for empty hostname after protocol
  if (!url.hostname) {
    return { valid: false, error: 'URL must have a valid hostname.' };
  }

  return { valid: true, url: url.toString(), normalized: str };
}

// Main
const args = process.argv.slice(2);
const inputUrl = args[0];

if (!inputUrl) {
  console.error(JSON.stringify({
    valid: false,
    error: 'No URL provided. Usage: node validate-url.mjs <url>'
  }));
  process.exit(1);
}

const result = isValidUrl(inputUrl);

if (result.valid) {
  console.log(JSON.stringify({
    valid: true,
    url: result.url,
    normalized: result.normalized
  }));
  process.exit(0);
} else {
  console.error(JSON.stringify({
    valid: false,
    error: result.error
  }));
  process.exit(1);
}
