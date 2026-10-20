// bin/talli.js: the views it prints, from good, partial and missing summaries.
const assert = require('assert');
const { view, daysUntil, whenText, tuiFrame, money } = require('../bin/talli');

const oct20 = new Date(2026, 9, 20);
assert.strictEqual(daysUntil('2026-10-21', oct20), 1);
assert.strictEqual(daysUntil('2026-10-20', oct20), 0);
assert.strictEqual(daysUntil('2026-11-25', oct20), 36);
assert.strictEqual(whenText(0), 'today');
assert.strictEqual(whenText(1), 'tomorrow');
assert.strictEqual(whenText(5), 'in 5 days');
assert.strictEqual(money(1260), '$1,260');
assert.strictEqual(money(1358.5), '$1,358.50');

// the portal amount wins over the derived monthly total
let v = view({ payment: { total: '$1,358.50' }, income: { pwdMonthly: 1060, cdbMonthly: 200, totalMonthly: 1260 }, counts: { messages: 3 } }, oct20);
assert.strictEqual(v.amount, 1358.5);
assert.strictEqual(v.date, '2026-10-21');
assert.strictEqual(v.when, 'tomorrow');
assert.strictEqual(v.messages, 3);

// no portal amount: fall back to the derived total
v = view({ payment: { total: null }, income: { totalMonthly: 1260 } }, oct20);
assert.strictEqual(v.amount, 1260);

// offline or signed out: the date still shows, nothing else is invented
v = view(null, oct20);
assert.strictEqual(v.amount, null);
assert.strictEqual(v.pwd, null);
assert.strictEqual(v.messages, null);
assert.ok(v.date);

// garbage in, no crash
v = view({ payment: { total: 'n/a' }, income: {}, counts: {} }, oct20);
assert.strictEqual(v.amount, null);

// the full-screen frame fits small and large terminals and never shows a fake amount
for (const [cols, rows] of [[40, 12], [120, 40]]) {
  const frame = tuiFrame(view(null, oct20), cols, rows, '');
  assert.ok(frame.includes('NEXT PAYMENT'));
  assert.ok(frame.includes('----'));
}
assert.ok(tuiFrame(view({ income: { totalMonthly: 1260, pwdMonthly: 1060, cdbMonthly: 200 } }, oct20), 80, 24).includes('1,260'));
console.log('test-cli: ok');
