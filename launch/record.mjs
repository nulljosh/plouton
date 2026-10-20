// Screencast recorder for launch/make_promo.py. Two jobs, one headless Chrome driver:
//   app:   the real dashboard at phone size (432x768 at 2.5x = 1080x1920), signed in to the demo account,
//          walking Home, Messages and Status for the given holds.
//   stage: launch/stage.html at 1920x1080, played once with the given plan.
// Every painted frame is saved as a jpeg stamped on arrival, so the edit can rebuild real time.
// usage: node launch/record.mjs app   <base-url> <demo-password> <out-dir> '<json [{action, hold}]>'
//        node launch/record.mjs stage <stage-url> <out-dir> '<json plan>'
// writes <out-dir>/rec.json: {frames: [[seconds, file]], starts: [seconds], end: seconds}
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const MODE = process.argv[2];
const args = process.argv.slice(3);
const OUT = MODE === 'app' ? args[2] : args[1];
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => Date.now() / 1000;

const profile = fs.mkdtempSync(path.join(OUT, 'chrome-'));
const chrome = spawn(CHROME, ['--headless=new', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required', `--user-data-dir=${profile}`,
  '--remote-debugging-port=9334', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
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
const waitFor = async (expr, ms = 20000) => { for (let t = 0; t < ms; t += 150) { if (await js(expr)) return; await sleep(150); } };
const screencast = (w, h) => send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: w, maxHeight: h, everyNthFrame: 1 });
await send('Page.enable');
await send('Runtime.enable');

const starts = [];
if (MODE === 'app') {
  const [BASE, PASSWORD, , BEATS] = args;
  const W = 432, H = 768, SCALE = 2.5;
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: SCALE, mobile: true });
  await send('Emulation.setTouchEmulationEnabled', { enabled: true });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }] });
  await send('Page.navigate', { url: `${BASE}/login.html` });
  await sleep(1200);
  await js(`fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:'talli.review',password:${JSON.stringify(PASSWORD)}})}).then(r=>r.ok)`);
  await send('Page.navigate', { url: `${BASE}/unified.html` });
  await waitFor(`document.body.innerText.includes('NEXT PAYMENT')`);
  await sleep(600);
  const click = (label) => js(`[...document.querySelectorAll('button')].find(b => b.textContent.trim().startsWith(${JSON.stringify(label)}))?.click()`);
  await screencast(W * SCALE, H * SCALE);
  // a navigation ends the screencast, so remount Home instead: the amount counts up on camera
  await click('Status');
  await sleep(120);
  for (const beat of JSON.parse(BEATS)) {
    const t = now();
    starts.push(t);
    if (beat.action === 'home') await click('Home');
    if (beat.action === 'messages') await click('Messages');
    if (beat.action === 'status') {
      await click('Status');
      await sleep(1100);
      await js(`(() => { const el = [...document.querySelectorAll('div')].find(d => getComputedStyle(d).overflowY === 'auto' && d.scrollHeight > d.clientHeight); if (el) el.scrollTo({top: el.scrollHeight * 0.16, behavior: 'smooth'}); })()`);
    }
    await sleep(Math.max(0, beat.hold * 1000 - (now() - t) * 1000));
  }
} else {
  const [URL, , PLAN] = args;
  await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: URL });
  await waitFor(`typeof window.start === 'function'`);
  await screencast(1920, 1080);
  js(`window.start(${PLAN})`);  // not awaited: the stage reports its own clock in window.__t0
  await waitFor(`!!window.__t0`, 30000);
  starts.push(await js('window.__t0'));
  await waitFor(`window.__done === true`, 120000);
}
await sleep(400);
const end = now();
await send('Page.stopScreencast');
ws.close();
chrome.kill();
try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
// a big JSON on stdout gets cut when the process exits mid-write, so it goes to a file
fs.writeFileSync(path.join(OUT, 'rec.json'), JSON.stringify({ frames, starts, end }));
process.exit(0);
