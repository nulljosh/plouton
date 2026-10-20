#!/usr/bin/env node
// Talli in the terminal. One file, no dependencies.
//   talli login      sign in once with BCeID; keeps only a read-only widget token
//   talli            next cheque: amount, date, days left
//   talli summary    the breakdown and counts (add --json for scripts)
//   talli tui        a live full-screen view: r refreshes, q quits
//   talli logout     forget the token
// The token is the same one the iPhone widgets use: it reads /api/summary and nothing else.
// TALLI_URL points it at another server (http://localhost:3000 for local work).
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const readline = require('readline');
const { nextPaymentDate } = require('../src/pay-dates');

const BASE = (process.env.TALLI_URL || 'https://talli.jaybulb.com').replace(/\/$/, '');
const TOKEN_FILE = path.join(os.homedir(), '.config', 'talli', 'token');
const tty = process.stdout.isTTY;
const c = (code) => (s) => (tty ? `\x1b[${code}m${s}\x1b[0m` : String(s));
const bold = c('1'), dim = c('2'), blue = c('38;2;91;155;213'), green = c('38;2;45;158;95');

const money = (n) => '$' + Number(n).toLocaleString('en-CA', { minimumFractionDigits: Number.isInteger(+n) ? 0 : 2, maximumFractionDigits: 2 });
const parseMoney = (s) => (s == null ? null : Number(String(s).replace(/[^0-9.]/g, '')) || null);

// Days from today to an ISO date, both read as local calendar days.
function daysUntil(iso, today = new Date()) {
  const [y, m, d] = iso.split('-').map(Number);
  const a = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return Math.round((Date.UTC(y, m - 1, d) - a) / 86400000);
}

function whenText(days) {
  return days === 0 ? 'today' : days === 1 ? 'tomorrow' : `in ${days} days`;
}

function longDate(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('en-CA', { weekday: 'short', month: 'short', day: 'numeric' });
}

// What every view shows, from a /api/summary body (or null when offline).
function view(summary, today = new Date()) {
  const date = nextPaymentDate(today);
  const days = daysUntil(date, today);
  const amount = parseMoney(summary?.payment?.total) ?? summary?.income?.totalMonthly ?? null;
  return {
    amount, date, days,
    when: whenText(days),
    pwd: summary?.income?.pwdMonthly ?? null,
    cdb: summary?.income?.cdbMonthly ?? null,
    messages: summary?.counts?.messages ?? null,
    updated: summary?.lastUpdated ?? null,
  };
}

function readToken() {
  try { return fs.readFileSync(TOKEN_FILE, 'utf8').trim() || null; } catch { return null; }
}

async function fetchSummary(token) {
  let r;
  try { r = await fetch(`${BASE}/api/summary`, { headers: { 'x-api-token': token } }); }
  catch { throw new Error(`Can't reach ${new URL(BASE).host}. Offline?`); }
  if (r.status === 401) throw new Error('Your sign-in expired. Run: talli login');
  if (!r.ok) throw new Error(`Talli answered ${r.status}`);
  return r.json();
}

function ask(question, hidden) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true });
    if (hidden) rl._writeToOutput = (s) => { if (s.includes(question)) process.stdout.write(s); };
    rl.question(question, (a) => { rl.close(); if (hidden) process.stdout.write('\n'); resolve(a.trim()); });
  });
}

async function login() {
  console.log(dim('BCeID locks after a few wrong passwords, so this tries once.'));
  const username = await ask('BCeID username: ');
  const password = await ask('Password: ', true);
  if (!username || !password) return fail('Nothing entered.');
  let r;
  try {
    r = await fetch(`${BASE}/api/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Origin: BASE },
      body: JSON.stringify({ username, password }),
    });
  } catch { return fail(`Can't reach ${new URL(BASE).host}. Offline?`); }
  const body = await r.json().catch(() => ({}));
  if (!r.ok || body.success === false) return fail(body.error || `Sign-in failed (${r.status}). Not retrying.`);
  const cookie = (r.headers.getSetCookie?.() || []).map((h) => h.split(';')[0]).join('; ');
  const t = await fetch(`${BASE}/api/widget-token`, { headers: { cookie } });
  const { token } = await t.json().catch(() => ({}));
  if (!token) return fail('Signed in, but no token came back.');
  fs.mkdirSync(path.dirname(TOKEN_FILE), { recursive: true, mode: 0o700 });
  fs.writeFileSync(TOKEN_FILE, token + '\n', { mode: 0o600 });
  console.log(green('Signed in.') + ' Your password was not saved.');
}

function fail(msg) {
  console.error(msg);
  process.exitCode = 1;
}

function printNext(v) {
  const amt = v.amount != null ? green('$') + bold(money(v.amount).slice(1)) : dim('amount unknown');
  console.log(`${amt}  ${blue(v.when)}  ${dim(longDate(v.date))}`);
}

function printSummary(v) {
  printNext(v);
  if (v.pwd != null) console.log(`  PWD assistance     ${money(v.pwd)}`);
  if (v.cdb != null) console.log(`  Disability Benefit ${money(v.cdb)}`);
  if (v.messages != null) console.log(`  Messages           ${v.messages}`);
  if (v.updated) console.log(dim(`  updated ${new Date(v.updated).toLocaleString('en-CA')}`));
}

// Full-screen view: the amount big and centred, like the dashboard's Home.
function tuiFrame(v, cols, rows, note) {
  const center = (s, raw = s) => ' '.repeat(Math.max(0, Math.floor((cols - raw.length) / 2))) + s;
  const amount = v.amount != null ? money(v.amount).slice(1) : '----';
  const lines = [
    center(dim('NEXT PAYMENT'), 'NEXT PAYMENT'), '',
    center(green('$') + bold(amount), '$' + amount), '',
    center(blue(v.when), v.when),
    center(dim(longDate(v.date)), longDate(v.date)), '',
  ];
  if (v.pwd != null) lines.push(center(`PWD ${money(v.pwd)}   CDB ${money(v.cdb ?? 0)}`));
  if (v.messages != null) lines.push(center(`${v.messages} message${v.messages === 1 ? '' : 's'}`));
  const top = Math.max(0, Math.floor((rows - lines.length - 2) / 2));
  const foot = center(dim(note || 'r refresh   q quit'), note || 'r refresh   q quit');
  return '\x1b[2J\x1b[H' + '\n'.repeat(top) + lines.join('\n') + '\n'.repeat(Math.max(1, rows - top - lines.length - 1)) + foot;
}

async function tui(token) {
  if (!tty) return fail('talli tui needs a terminal.');
  let v = view(null), note = 'loading';
  const draw = () => process.stdout.write(tuiFrame(v, process.stdout.columns, process.stdout.rows, note));
  const refresh = async () => {
    note = 'refreshing'; draw();
    try { v = view(await fetchSummary(token)); note = ''; } catch (e) { note = e.message; }
    draw();
  };
  process.stdout.write('\x1b[?25l');  // hide the cursor while the view is up
  const quit = () => { process.stdout.write('\x1b[?25h\x1b[2J\x1b[H'); process.exit(0); };
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.on('data', (k) => { const s = k.toString(); if (s === 'q' || s === '\x03') quit(); if (s === 'r') refresh(); });
  process.stdout.on('resize', draw);
  setInterval(refresh, 5 * 60 * 1000);
  await refresh();
}

async function main(argv) {
  const cmd = argv[0] || 'next';
  if (cmd === 'login') return login();
  if (cmd === 'logout') { try { fs.unlinkSync(TOKEN_FILE); } catch {} return console.log('Signed out.'); }
  if (cmd === 'help' || cmd === '--help' || cmd === '-h') {
    return console.log('talli [next|summary [--json]|tui|login|logout]');
  }
  const token = readToken();
  if (!token) {
    // The date needs no account: show it, and say how to get the amount.
    printNext(view(null));
    return console.log(dim('Run `talli login` once to see your amount.'));
  }
  if (cmd === 'tui') return tui(token);
  let summary = null;
  try { summary = await fetchSummary(token); } catch (e) { console.error(dim(e.message)); }
  const v = view(summary);
  if (cmd === 'summary' && argv.includes('--json')) return console.log(JSON.stringify(v, null, 2));
  if (cmd === 'summary') return printSummary(v);
  if (cmd === 'next') return printNext(v);
  fail(`Unknown command: ${cmd}. Try: talli help`);
}

if (require.main === module) main(process.argv.slice(2)).catch((e) => fail(e.message));

module.exports = { view, daysUntil, whenText, tuiFrame, money };
