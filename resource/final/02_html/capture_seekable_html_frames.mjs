import {chromium} from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

function arg(name,fallback){const i=process.argv.indexOf(name);return i>=0&&process.argv[i+1]?process.argv[i+1]:fallback;}
const html=path.resolve(arg('--html','index.html'));
const out=path.resolve(arg('--out','frames'));
const hook=arg('--hook','quantumOverlay');
const fps=Number(arg('--fps','60'));
const duration=Number(arg('--duration','5'));
const offset=Number(arg('--offset','0'));
const width=Number(arg('--width','640'));
const height=Number(arg('--height','1080'));
const prefix=arg('--prefix','frame');
const chrome=arg('--chrome','C:/Program Files/Google/Chrome/Application/chrome.exe');
const total=Math.round(duration*fps);
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:chrome});
const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
await page.goto(`${pathToFileURL(html).href}?clean=1`);
await page.waitForTimeout(200);
for(let frame=0;frame<total;frame++){
  const seconds=offset+frame/fps;
  await page.evaluate(({hook,seconds})=>window[hook].setTime(seconds),{hook,seconds});
  await page.screenshot({path:path.join(out,`${prefix}_${String(frame).padStart(5,'0')}.png`),omitBackground:true});
  if(frame%fps===0)process.stdout.write(`captured ${seconds.toFixed(3)}s\n`);
}
await browser.close();
