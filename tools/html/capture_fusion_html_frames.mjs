import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

function readArg(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const html = path.resolve(readArg('--html', 'resource/fromAI/05_html_generated/fusion_quantum_bridge_project_v3.html'));
const url = readArg('--url', '');
const out = path.resolve(readArg('--out', 'resource/fromAI/10_review_proxies/html_fusion_v3_frames'));
const fps = Number(readArg('--fps', '60'));
const duration = Number(readArg('--duration', '49'));
const fromSeconds = Number(readArg('--from', '0'));
const toSeconds = Number(readArg('--to', String(duration)));
const timesArg = readArg('--times', '');
const format = readArg('--format', 'png').toLowerCase();
const quality = Number(readArg('--quality', '95'));
const chrome = readArg('--chrome', 'C:/Program Files/Google/Chrome/Application/chrome.exe');
const totalFrames = Math.round(fps * duration);
const firstFrame = Math.max(0, Math.round(fromSeconds * fps));
const lastFrame = Math.min(totalFrames, Math.round(toSeconds * fps));
const requestedFrames = timesArg
  ? [...new Set(timesArg.split(',').map(Number).filter(Number.isFinite).map(value => Math.round(value * fps)))]
  : Array.from({ length: Math.max(0, lastFrame - firstFrame) }, (_, index) => firstFrame + index);

fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: chrome });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(url || `${pathToFileURL(html).href}?clean=1`);
await page.waitForTimeout(250);

for (const frame of requestedFrames) {
  await page.evaluate(value => window.quantumFusion.setTime(value), frame / fps);
  const extension = format === 'jpg' || format === 'jpeg' ? 'jpg' : 'png';
  const screenshotOptions = { path: path.join(out, `fusion_${String(frame).padStart(5, '0')}.${extension}`) };
  if (extension === 'jpg') Object.assign(screenshotOptions, { type: 'jpeg', quality });
  await page.screenshot(screenshotOptions);
  if (timesArg || frame % fps === 0) process.stdout.write(`captured ${frame / fps}s\n`);
}

await browser.close();
