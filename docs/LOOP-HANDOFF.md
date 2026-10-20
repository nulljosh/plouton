# Talli loop handoff (2026-10-20, morning)

## What the loop is

Talli is a BC disability benefits tracker on web, iPhone and Mac at talli.jaybulb.com. The loop is driving native 4.0.0, the first store release with everything since 3.6.2. The name stays Talli everywhere. Keep the UI simple: every tool is one folded line that opens on tap, and Home is one number, one line and one action. A git push deploys nothing; ship the web with `npm run deploy`.

## Where things stand

- The cheque table was wrong: the dashboard and both widget sets showed the 2026 dates wrong and said the next payment was October 28, when BC issues it on the 21st. The dashboard now uses the server's official date, the tables match gov.bc.ca for 2026 and 2027, and a test fails if any copy drifts.
- The site's CSP now allows the Cloudflare Web Analytics beacon, which was blocked on every page.
- iOS: Settings and Sign Out are reachable again, since each tab owns its own NavigationStack. Liquid Glass and Jony Ive pass: no redundant tab titles, Home built around one number with a full-width 48 pt glass action, money tiles, calendar and Details; Status is one inset grouped list; one radius set. Mac has a native sidebar instead of a phone-style tab bar.
- Landing page in the Hermes style (thin caps, grainy blue bands, public domain halftone art, engraved glyph footer). Brand kit at /brand. The tally icon was redone in Icon Composer and centred, and the iOS app target uses Talli.icon.
- Versions: iOS 4.0.0 is being archived and submitted. Mac 3.6.1's review was pulled, and that build was relabelled 4.0.0 and is also being submitted. Waiting for Review on either is not yet confirmed.
- QA 2026-10-20: npm test passes. The live API on talli.jaybulb.com returns 200 with a session and 401 without on every path the iOS app calls. Landing, privacy, manifest, robots and sitemap are 200.
- Open in roadmap.md: verify the contribution figures against the real account; confirm the store build on the phone; flip the GitHub release when Apple approves the Mac build.

## Next, in order

1. Confirm both 4.0.0 builds reach Waiting for Review (`asc versions list --app 6782366555` for the real state). If either is rejected, read the reason, fix it in the loop and resubmit.
2. When Apple approves, flip the GitHub release for 4.0.0 from pre-release to Latest (check `gh release list` first).
3. Joshua checks the new build on his phone with his real login: Home loads, Settings opens from the avatar, Sign Out works. The earlier blank-home report came from the old build calling the lapsed host; 3.6.2 already carries the fix.
4. Real-account read-only checks and real-device checks (reminders, Watch handoff, vault encryption) are Joshua's to do. List them here, do not wait on them.
5. Then pick the 5.0.0 candidates from ~/.claude/loops/talli.md, bugs first.

## Restart prompt

```
/loop Talli: read ~/.claude/loops/talli.md and docs/LOOP-HANDOFF.md, run the next iteration toward native 4.0.0 (real versions from `asc versions list`), then re-arm.
```
