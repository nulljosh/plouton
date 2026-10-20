const assert = require('assert');
const { PROVINCES, getProvince, listProvinces, nextPayDate, monthlyDeduction, describeRule } = require('../src/programs/provinces');
const { deriveWhatIf } = require('../src/programs/whatif');

let passed = 0, failed = 0;
const test = (name, fn) => { try { fn(); console.log(`  [OK] ${name}`); passed++; } catch (e) { console.log(`  [FAIL] ${name}: ${e.message}`); failed++; } };
const now = new Date(2026, 9, 2);
const opts = { base: 1, household: 'single', now };

test('every province file is complete and its tiers make sense', () => {
  for (const p of Object.values(PROVINCES)) {
    assert.ok(p.code && p.name && p.program && p.monthlySingle > 0 && /^https:\/\//.test(p.apply), p.code);
    assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(p.asOf), p.code);
    if (p.earnings.kind === 'monthly') {
      for (const tiers of [p.earnings.tiers, p.earnings.familyTiers].filter(Boolean)) {
        assert.strictEqual(tiers.at(-1).upTo, null, `${p.code} last tier is open ended`);
        tiers.forEach((t, i) => { assert.ok(t.keep >= 0 && t.keep <= 1); if (i) assert.ok(tiers[i - 1].upTo < (t.upTo ?? Infinity), `${p.code} tiers ascend`); });
      }
    }
    assert.ok(!JSON.stringify(p).includes('—'), `${p.code} has an em dash`);
    for (const url of p.sources) assert.ok(url.startsWith('https://'));
  }
});

test('AB and ON pay dates are official issue dates: ISO, ascending, on weekdays', () => {
  for (const code of ['ab', 'on']) {
    const dates = PROVINCES[code].payDates;
    assert.ok(dates.length >= 12, code);
    dates.forEach((d, i) => {
      assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(d), `${code} ${d}`);
      if (i) assert.ok(dates[i - 1] < d, `${code} ascends at ${d}`);
      const day = new Date(`${d}T12:00:00`).getDay();
      assert.ok(day > 0 && day < 6, `${code} ${d} is a weekday`);
    });
  }
});

test('nextPayDate finds the next issue date per province, and null past the list', () => {
  assert.strictEqual(nextPayDate('ab', now), '2026-10-27');
  assert.strictEqual(nextPayDate('ON', now), '2026-10-30');
  assert.strictEqual(nextPayDate('bc', now), '2026-10-21');
  assert.strictEqual(nextPayDate('on', new Date(2026, 9, 30)), '2026-10-30', 'payday itself counts');
  assert.strictEqual(nextPayDate('on', new Date(2026, 11, 1)), null, 'ODSP December 2026 is not published yet');
  assert.strictEqual(nextPayDate('xx', now), null);
  const listed = listProvinces(now).find((p) => p.code === 'ab');
  assert.strictEqual(listed.nextPayDate, '2026-10-27');
  assert.strictEqual(listed.payDates.length, PROVINCES.ab.payDates.length);
});

test('getProvince is forgiving about case and strict about unknowns', () => {
  assert.strictEqual(getProvince('AB').code, 'ab');
  assert.strictEqual(getProvince('xx'), null);
  assert.strictEqual(getProvince(undefined), null);
});

test('monthly deductions: Alberta $350 then dollar for dollar, Ontario 25 cents', () => {
  const ab = PROVINCES.ab.earnings.tiers, on = PROVINCES.on.earnings.tiers;
  assert.strictEqual(monthlyDeduction(ab, 350), 0);
  assert.strictEqual(monthlyDeduction(ab, 1000), 650);             // AISH since July 2, 2026: every dollar over 350
  assert.strictEqual(monthlyDeduction(ab, 2500), 2150);
  assert.strictEqual(monthlyDeduction(on, 1000), 0);
  assert.strictEqual(monthlyDeduction(on, 1500), 375);            // 75 cents of each dollar over 1,000
  assert.strictEqual(monthlyDeduction(on, 0), 0);
});

test('AISH has one $350 rule for singles and families since July 2026', () => {
  const single = deriveWhatIf({ wage: 15, hours: 10, start: '2026-11', province: 'ab' }, opts);
  const family = deriveWhatIf({ wage: 15, hours: 10, start: '2026-11', province: 'ab' }, { ...opts, household: 'couple_one' });
  assert.strictEqual(family.rows[0].reduction, single.rows[0].reduction);
  assert.strictEqual(single.rows[0].reduction, 300);                // $650 a month, $300 over the $350
});

test('what-if in Alberta: $25 at 30 hours earns past the whole cheque', () => {
  const d = deriveWhatIf({ wage: 25, hours: 30, start: '2026-11', province: 'ab' }, opts);
  assert.strictEqual(d.base, 1940);
  assert.deepStrictEqual([d.rows[0].reduction, d.rows[0].assistance], [1940, 0]);
  assert.strictEqual(d.province.code, 'ab');
  assert.ok(d.rule.includes('$350'));
});

test('what-if in Ontario: $20 at 20 hours loses $550 a month; room is the first $1,000', () => {
  const d = deriveWhatIf({ wage: 20, hours: 20, start: '2026-11', province: 'on' }, opts);
  assert.deepStrictEqual([d.base, d.rows[0].reduction, d.rows[0].assistance, d.room], [1436, 550, 886, 1000]);
  assert.strictEqual(d.safeHours, 11.54);
  assert.strictEqual(d.monthlyRule, true);
});

test('a small job under the first tier costs nothing in either province', () => {
  for (const [province, hours] of [['ab', 5], ['on', 10]]) {
    const d = deriveWhatIf({ wage: 15, hours, start: '2026-11', province }, opts);   // about $325 and $650 a month
    assert.strictEqual(d.totalReduction, 0, province);
    assert.strictEqual(d.firstClawback, null);
  }
});

test('an unknown province falls back to BC', () => {
  const d = deriveWhatIf({ wage: 20, hours: 20, start: '2026-11', province: 'zz' }, { ...opts, base: 1483.5 });
  assert.strictEqual(d.input.province, 'bc');
});

test('listProvinces gives the screen everything it needs, in plain words', () => {
  const list = listProvinces();
  assert.deepStrictEqual(list.map((p) => p.code), ['bc', 'ab', 'on']);
  assert.ok(list.find((p) => p.code === 'on').rule.includes('25 cents'));
  assert.ok(describeRule(PROVINCES.bc).includes('yearly limit'));
});

test('report windows come from the official pages: Ontario by the 7th, Alberta as it happens', () => {
  const list = listProvinces(now);
  const on = list.find((p) => p.code === 'on').report, ab = list.find((p) => p.code === 'ab').report;
  assert.strictEqual(on.dueDay, 7);
  assert.ok(on.text.includes('$0') && on.source.startsWith('https://www.ontario.ca/'));
  assert.strictEqual(ab.dueDay, null);
  assert.ok(ab.source.startsWith('https://manuals.alberta.ca/'));
  assert.ok(list.find((p) => p.code === 'ab').earningsNote.includes('$700'));
  assert.strictEqual(list.find((p) => p.code === 'bc').report, null);
});

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
