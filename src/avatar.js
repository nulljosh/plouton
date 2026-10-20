'use strict';
// Everyone gets a real Greek-god portrait: public domain or CC0 sculpture photos from Wikimedia
// Commons (web/avatars/CREDITS.md), cropped square and dithered into the landing page's two blues.
// 24 statues plus a mirrored copy of each. Same user, same face; regenerate steps to the next one.

const FILES = [
  '01-athena-venice.png',
  '02-athena-armored.png',
  '03-athena-head.png',
  '04-athena-helmet.png',
  '06-athena-bust.png',
  '07-zeus-bearded.png',
  '09-dionysus.png',
  '10-antinous.png',
  '11-ares.png',
  '12-asclepius.png',
  '13-asclepius-bust.png',
  '14-asklepios.png',
  '15-hera-ludovisi.png',
  '16-aphrodite-cnidus.png',
  '17-goddess.png',
  '18-artemis-istanbul.png',
  '19-artemis-lykosoura.png',
  '26-dionysiac-a.png',
  '27-dionysiac-b.png',
  '28-helios-rhodes.png',
  '31-zeus-head.png',
  '32-zeus-otricoli.png',
  '33-apollo-head.png',
  '35-apollo-met.png',
  '01-athena-venice-m.png',
  '02-athena-armored-m.png',
  '03-athena-head-m.png',
  '04-athena-helmet-m.png',
  '06-athena-bust-m.png',
  '07-zeus-bearded-m.png',
  '09-dionysus-m.png',
  '10-antinous-m.png',
  '11-ares-m.png',
  '12-asclepius-m.png',
  '13-asclepius-bust-m.png',
  '14-asklepios-m.png',
  '15-hera-ludovisi-m.png',
  '16-aphrodite-cnidus-m.png',
  '17-goddess-m.png',
  '18-artemis-istanbul-m.png',
  '19-artemis-lykosoura-m.png',
  '26-dionysiac-a-m.png',
  '27-dionysiac-b-m.png',
  '28-helios-rhodes-m.png',
  '31-zeus-head-m.png',
  '32-zeus-otricoli-m.png',
  '33-apollo-head-m.png',
  '35-apollo-met-m.png'
];

function hash(str) {
  let h = 2166136261;
  for (const ch of String(str)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
  return h >>> 0;
}

// `n` is bumped each time they tap regenerate; consecutive picks are different statues.
const avatarFor = (userId, n = 0) => `/avatars/${FILES[(hash(userId) + n) % FILES.length]}`;

module.exports = { avatarFor, FILES };
