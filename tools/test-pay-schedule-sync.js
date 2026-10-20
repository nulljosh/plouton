// Every client copy of the cheque issue schedule must match src/pay-dates.js, the one checked against gov.bc.ca.
// The web dashboard's copy drifted once and showed Oct 28 when the cheque came Oct 21.
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { CHEQUE_ISSUE_DATES } = require('../src/pay-dates');

const want = {};
for (const d of CHEQUE_ISSUE_DATES) {
  const [y, m, day] = d.split('-').map(Number);
  (want[y] = want[y] || {})[m - 1] = day;
}
const read = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');

// web: 2026:{0:21,1:25,...}
const web = {};
for (const [, y, body] of read('web/unified.html').matchAll(/(\d{4}):\{([\d:,]+)\}/g))
  web[y] = Object.fromEntries(body.split(',').map((p) => p.split(':').map(Number)));
assert.deepStrictEqual(web, want, 'web/unified.html PAY_SCHEDULE');

// widgets: 2026: [0: 21, 1: 25, ...]
for (const f of ['widgets-ios/Models/WidgetAPI.swift', 'widgets-macos/Models/MacWidgetAPI.swift']) {
  const got = {};
  for (const [, y, body] of read(f).matchAll(/(\d{4}): \[([\d:, ]+)\]/g))
    got[y] = Object.fromEntries(body.split(',').map((p) => p.split(':').map((x) => Number(x.trim()))));
  assert.deepStrictEqual(got, want, f);
}
console.log('test-pay-schedule-sync: ok');
