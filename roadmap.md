# Talli Roadmap

Talli is free and stays free. The job is accuracy: what lands, when, and what you are allowed to earn. History lives in git. Store state comes from `asc versions list --app 6782366555`, never from this file.

## Now (4.0.x)
- [ ] iOS 4.0.1: build 202610201345 uploaded. Attach, new iPhone screenshots, animated header, URLs, submit.
- [ ] Mac 4.0.0: rebuild from main (Settings tab), attach, four-tab desktop shots, submit.
- [ ] Flip the GitHub 4.0.0 release to Latest once Mac is approved (#62).
- [ ] Verify the account contribution figures against the real account (#57, Joshua's login).
- [ ] Joshua's call: delete the dead `src/session-store.js` and `tools/test-session-store.js` (nothing imports them).

## 5.0 Every platform, every tool
- [ ] Web-only tools on iPhone and Mac: federal-only mode, open data, benefit finder, job calculator.
- [ ] fr, zh and pa strings complete in the String Catalog, checked by a test.
- [ ] Watch shows the next amount and date with no phone nearby.
- [ ] Widgets read the shared pay table, tested against `src/pay-dates.js`.
- [ ] Real-device pass: reminders fire on the day, Watch handoff, vault encryption.

## 6.0 Android
- [ ] Ship `kmp/` as a signed APK on the GitHub release, same API, same four tabs.
- [ ] Google Play listing, free.

## 7.0 More provinces
- [ ] Alberta AISH and Ontario ODSP as first-class programs: cheque dates, earnings exemptions, report windows.
- [ ] Province picked at sign-in, rules tested per province like BC.

## 8.0 Reminders that matter
- [ ] Monthly report reminder on day 1, nudge on day 4 if not done.
- [ ] Earnings tracker warns before the annual exemption runs out.
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
