# Talli loop handoff (2026-10-16, 15:40, STOPPED at goal)

## What the loop is

Roadmap 3.7 to 10.0 complete; payday push dropped. Version 10.0.0 was a planning milestone and was never shipped to the stores. The native builds are now iOS 3.6.2 and Mac 3.6.1, both submitted and Waiting for Review at Apple. The GitHub release v3.6.2 stays a pre-release until Apple approves. Loop stopped at goal reached. Keep the UI super simple: every tool is one folded line that opens on tap.

## Where things stand

Eighteen releases shipped (roadmap sections 3.7.0 through 3.21.0): report from notification, Watch app, year-in-review CSV, four languages, benefit finder, RDSP tracker, supplements calendar, missed-payment alert, simplified UI (one-line folds), document vault, reconsideration helper, message replies, service requests, household tracker, trusted helper, what-if job calculator, simpler Status tab (2064px to 1026px), turning 65 or moving out of BC, budget against paydays, six new entitlements, provinces as data files (Alberta AISH, Ontario ODSP), open data API at /api/open, federal-only mode at /api/federal-finder. Ministry rate tables and earnings limits now live in code. Alberta and Ontario figures checked against public guides and official links, flagged on screen. GitHub tests green. Status tab tools all fold to one-line. Sections 7.0 and 8.0 complete. Payday push (4.0) dropped. App Store still has 3.6.0 (native features since 3.7.0 not in users' hands).

Since then: the landing, login, lawyers and privacy pages use plain white and off-white surfaces instead of the Jaybulb cream (an override in `web/tokens.css`), and the hero's ghost-number wall is dimmed behind a stronger scrim. Deployed to talli.jaybulb.com. Two dead CSS files (`web/design-tokens.css`, `web/css/styles.css`) are still on disk and listed as an open roadmap item. Also since then: the app is three tabs everywhere (Home, Status, Messages). Web dropped Calendar and Legal; iOS folds Reports and Benefits into Status and moved Settings behind the avatar; macOS has a gear button for Settings. Home on web, iOS and macOS shows one number, one line and one action, with the rest under a collapsed Details row. A brand kit lives in `brand/` (tokens.css and index.html, system font, Apple spacing and type scale). A new app icon (lighter strokes, steeper tally) is in the repo but not in any build yet. iOS and macOS compile clean. iOS 3.6.2 and Mac 3.6.1 are in Apple review. GitHub release v3.6.2 is a pre-release to flip to Latest when Apple approves. The web Status tab now uses the server's real income, so Home and Status agree.

## Next steps

1. Real-account test: Joshua runs a one-line login (saves cookie jar to scratchpad), read-only checks on real data (household vs cheque, missed-payment alert, budget, finder prefill, helper view). Claude never types BCeID password.
2. Fresh native build to App Store review: asc workflow, update review notes with exact steps to reach new tools. First native release since 3.6.0.
3. Real-device checks: reminders firing, Watch token handoff, vault encryption on real phone.
4. Note: federal-only mode and open data API are web only.
5. Flip GitHub release v3.6.2 from pre-release to Latest once Apple approves. Verify the contribution figures against the real account.

Payday push dropped.

## Restart prompt (when resuming from STOPPED)

When 3.6.0 clears App Store review:

```
/loop Talli: real-account test with cookie jar (Joshua logs in from .env, reads real cheque, checks household/alert/budget/finder/helper/RDSP/supplements), create the next App Store version (iOS 3.6.2 and Mac 3.6.1 are already in review), attach TestFlight build, write review notes (steps: open app, tap Money tools, tap What If), write App Privacy for vault, submit iPhone and Mac, run read-only checks from asc web UI, real-device checks (reminders, Watch, vault). Payday push dropped. Keep UI super simple.
```

## Release cadence

Latest: 3.21.0 shipped 2026-10-02. Next: fresh native build to App Store (all features since 3.7.0 included).
