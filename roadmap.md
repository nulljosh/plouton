# Talli Roadmap

Talli is free and stays free. The job is accuracy: what lands, when, and what you are allowed to earn. History lives in git. Store state comes from `asc versions list --app 6782366555`, never from this file.

## Now (4.0.x)
- [x] iOS 4.0.1: header and search videos, new iPhone shots, submitted 2026-10-20.
- [x] Mac 4.0.0: build 202610201455 from main, desktop shots, submitted 2026-10-20.
- [ ] Flip the GitHub 4.0.0 release to Latest once Mac is approved (#62).
- [ ] Verify the account contribution figures against the real account (#57, Joshua's login).
- [ ] Joshua's call: delete the dead `src/session-store.js` and `tools/test-session-store.js` (nothing imports them).

## 5.0 Every platform, every tool
- [x] Benefit finder, job calculator and federal-only mode (sign-in screen, no account) on iPhone and Mac.
- [ ] fr, zh and pa strings complete in the String Catalog, checked by a test. fr done; zh and pa have every plain string, the 20 benefit strings marked `review` each need a human or DeepL pass.
- [ ] Watch shows the next amount and date with no phone nearby. Built: it calls `/api/summary` with its own token and caches the last result; needs the real-device check below.
- [x] Widgets read the shared pay table, tested against `src/pay-dates.js` (`tools/test-pay-schedule-sync.js`).
- [ ] Real-device pass: reminders fire on the day, Watch handoff, vault encryption.

## 6.0 Android
- [ ] Ship `kmp/` as a signed APK on the GitHub release, same API, same four tabs.
- [ ] Google Play listing, free.

## 7.0 More provinces
- [ ] Alberta AISH and Ontario ODSP as first-class programs. In, from official pages: 2026 cheque dates, earnings rules (AISH $350 since July 2, 2026; ODSP $1,000 then 25 cents) and report windows (ODSP by the 7th, AISH as it happens), on `/api/provinces` and open data. Left: ADAP's progressive deduction has no published rate, so the what-if covers AISH only.
- [ ] Province picked at sign-in, rules tested per province like BC. In: "Alberta or Ontario? See your rules" on the iPhone and Mac sign-in screens (next cheque, earnings, reporting, no account). Left: a per-province Home once an AB or ON account source exists.

## 8.0 Reminders that matter
- [x] Monthly report reminder on day 1, nudge on day 4 if not marked filed (iPhone and Mac, under the reporting reminder toggle).
- [x] Earnings tracker warns before the annual exemption runs out: once at 80 percent, once if over, each a year (iPhone and Mac, own toggle).
- [ ] Cheque-landed notification when Self-Serve shows the payment.

## 9.0 Helpers
- [ ] Shared read-only view for a support worker or family member, revocable.
- [ ] Printable one-page summary for appointments.

## 10.0 Offline first
- [ ] Every screen works from the last sync with no network; sync state shown in one line.

## 11 to 20: depth
- Benefits checker for every federal and BC program a person might be missing.
- RDSP planner: grants and bonds by year, what to put in to get the most.
- Housing and shelter rates, moving and crisis supplement guides.
- Appeals helper: dates, forms, and what to say, reviewed by an advocate.
- Accessibility audit each major: VoiceOver, Dynamic Type at the largest size, contrast.

## 21 to 50: reach
- Every Canadian province and territory.
- Advocate and legal clinic directory by city.
- Plain-language mode for every screen.
- Community-maintained rule tables with a test for every change.

## 51 to 100: the standard
- The default place anyone on assistance in Canada checks their money.
- Open data on cheque dates and rates for any app to use.
- Partnerships with advocacy groups, still free, still no ads.
- Each major is one theme, shipped on every platform, tested, and documented.
