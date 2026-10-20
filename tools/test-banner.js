// The App Store header video script keeps the two fixes that made the glyphs render, stays under Apple's 500 MB
// cap, and every glyph it draws exists in web/art. Rendering takes minutes, so this checks the script, not the video.
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const root = path.join(__dirname, '..');
const file = path.join(root, 'launch/make_banner.sh');
const sh = fs.readFileSync(file, 'utf8').split('\n').filter((l) => !l.trim().startsWith('#')).join('\n');

execFileSync('sh', ['-n', file]);
assert(/rsvg-convert .*web\/art\/\$n\.svg/.test(sh), 'glyphs must go through rsvg (ImageMagick drops <mask>)');
assert(sh.includes('-compose DstIn'), 'glyph rules must composite with DstIn, not CopyOpacity');
assert(!sh.includes('CopyOpacity'), 'CopyOpacity paints the gaps between rules black');
assert(/-maxrate \d+M/.test(sh), 'bitrate cap keeps the video under 500 MB');
for (const n of sh.match(/for n in ([a-z ]+);/)[1].trim().split(' '))
  assert(fs.existsSync(path.join(root, `web/art/${n}.svg`)), `web/art/${n}.svg missing`);
console.log('banner: ok');
