// Records the dashboard for launch/make_promo.py: Chrome's screencast at device pixels (1080x1920 from a
// 432x768 phone viewport at 2.5x), one jpeg per painted frame, each stamped on arrival.
// usage: node launch/record.mjs <base-url> <demo-password> <out-dir> '<json [{action, hold}]>'
// prints JSON {frames: [[seconds, file]], starts: [seconds], end: seconds}
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [, , BASE, PASSWORD, OUT, BEATS] = process.argv;
const beats = JSON.parse(BEATS);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const W = 432, H = 768, SCALE = 2.5;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => Date.now() / 1000;

const profile = fs.mkdtempSync(path.join(OUT, 'chrome-'));
const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--user-data-dir=${profile}`, '--remote-debugging-port=9334', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
let targets;
for (let i = 0; i < 60; i++) {
  try { targets = await (await fetch('http://127.0.0.1:9334/json')).json(); if (targets.find((t) => t.type === 'page')) break; } catch {}
  await sleep(250);
}
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0;
const pending = new Map();
const frames = [];
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d.result); pending.delete(d.id); return; }
  if (d.method === 'Page.screencastFrame') {
    const file = path.join(OUT, `f${String(frames.length).padStart(5, '0')}.jpg`);
    fs.writeFileSync(file, Buffer.from(d.params.data, 'base64'));
    frames.push([now(), file]);
    send('Page.screencastFrameAck', { sessionId: d.params.sessionId });
  }
};
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async (expression) => (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }))?.result?.value;
const waitFor = async (expr, ms = 15000) => { for (let t = 0; t < ms; t += 150) { if (await js(expr)) return; await sleep(150); } };

await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: SCALE, mobile: true });
await send('Emulation.setTouchEmulationEnabled', { enabled: true });
await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }] });
// sign in to the demo account on the same origin, then open the dashboard
await send('Page.navigate', { url: `${BASE}/login.html` });
await sleep(1200);
await js(`fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'talli.review',password:${JSON.stringify(PASSWORD)}})}).then(r=>r.ok)`);
await send('Page.navigate', { url: `${BASE}/unified.html` });
await waitFor(`document.body.innerText.includes('NEXT PAYMENT')`);
await sleep(600);

const click = (label) => js(`[...document.querySelectorAll('button')].find(b => b.textContent.trim().startsWith(${JSON.stringify(label)}))?.click()`);
await send('Page.startScreencast', { format: 'jpeg', quality: 90, maxWidth: W * SCALE, maxHeight: H * SCALE, everyNthFrame: 1 });
// a navigation ends the screencast, so remount Home instead: the amount counts up on camera
await click('Status');
await sleep(120);
await click('Home');

const starts = [];
for (const beat of beats) {
  const t = now();
  starts.push(t);
  if (beat.action === 'messages') await click('Messages');
  if (beat.action === 'status') {
    await click('Status');
    await sleep(900);
    await js(`(() => { const el = [...document.querySelectorAll('div')].find(d => getComputedStyle(d).overflowY === 'auto' && d.scrollHeight > d.clientHeight); if (el) el.scrollTo({top: el.scrollHeight * 0.18, behavior: 'smooth'}); })()`);
  }
  if (beat.action === 'card') await js(beat.card);
  await sleep(Math.max(0, beat.hold * 1000 - (now() - t) * 1000));
}
await sleep(1200);
const end = now();
await send('Page.stopScreencast');
ws.close();
chrome.kill();
try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
console.log(JSON.stringify({ frames, starts, end }));
process.exit(0);
