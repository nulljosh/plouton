// Talli Display ships everywhere it is used: the web woff2 with its @font-face and preload, the Apple TTF in both
// Xcode projects, and the OFL beside each copy. scripts/gen_font.py --check covers the glyphs; this runs in CI.
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const read = (f) => fs.readFileSync(path.join(root, f));

const woff2 = read('web/fonts/TalliDisplay-Semibold.woff2');
assert.strictEqual(woff2.subarray(0, 4).toString('latin1'), 'wOF2', 'web font is not WOFF2');
const ttf = read('fonts/TalliDisplay-Semibold.ttf');
assert.strictEqual(ttf.readUInt32BE(0), 0x00010000, 'Apple font is not a TrueType file');
assert(ttf.includes(Buffer.from('Talli Display', 'utf16le').swap16()), 'Apple font is not named Talli Display');
for (const f of ['web/fonts/OFL.txt', 'fonts/OFL.txt']) assert(/Open Font License/.test(read(f)), `${f} missing`);

const html = read('web/unified.html').toString();
assert(html.includes("src:url('/fonts/TalliDisplay-Semibold.woff2')"), 'unified.html has no @font-face for Talli Display');
assert(html.includes('rel="preload" href="/fonts/TalliDisplay-Semibold.woff2"'), 'unified.html does not preload the font');
for (const f of ['ios/project.yml', 'macos/project.yml'])
  assert(read(f).toString().includes('../fonts/TalliDisplay-Semibold.ttf'), `${f} does not bundle the font`);

// the web hero's advance table: every figure, comma and point, and proportional (a 1 is narrower than a 0)
const table = JSON.parse(html.match(/const TD_ADVANCE = (\{[^}]+\})/)[1].replace(/'/g, '"'));
for (const c of '0123456789,.') assert(table[c] > 0, `TD_ADVANCE has no ${c}`);
assert(table['1'] < table['0'], 'figures are not proportional');
console.log('test-font: ok');
