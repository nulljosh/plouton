# Talli loop handoff (2026-10-20, afternoon)

## What the loop is

Talli is a BC disability benefits tracker on web, iPhone and Mac at talli.jaybulb.com. The loop runs forever toward native 5.0, then 10, 50 and 100, one theme per major, per roadmap.md. The name stays Talli everywhere. Keep the UI simple: every tool is one folded line that opens on tap, and Home is one number, one line and one action. A git push deploys nothing; ship the web with `npm run deploy`.

## Where things stand

- iOS 4.0.0 is live. iOS 4.0.1 has build 202610201345, six iPhone screenshots and the header video placed; the search results video is processing, then it gets submitted.
- Mac 4.0.0 (build 202610201455, with the federal finder link) is Waiting for Review, with three desktop shots at 1280x800.
- The header and search videos come from `launch/make_banner.sh`: Talli's six glyphs in scanlines on the landing blue. `asc asset-library videos upload` prints `videoId`, then `asc localizations placements create` puts it on the localization.
- Sign-in on iPhone and Mac opens the federal-only finder with no account; a UI test taps through it.

## Next, in order

1. Place the search video on iOS 4.0.1 and submit it.
2. When Mac is approved, flip the GitHub 4.0.0 release to Latest (#62).
3. 5.0: open data on iPhone and Mac, zh and pa strings (reviewed, not machine), real-device pass.
4. Retake the Mac Settings shot (snapshot mode now signs in as your.username) and add it as the fourth desktop shot.

## For Joshua

- Check the contribution figures against your real account (#57).
- Say the word and the dead `src/session-store.js` and `tools/test-session-store.js` get deleted (nothing imports them).
- Real-device checks only you can do: reminders fire on the day, Watch handoff, vault encryption.

## Restart prompt

```
/loop Talli to v5, 10, 50, 100, forever: read ~/.claude/loops/talli.md, docs/LOOP-HANDOFF.md and roadmap.md, scan the repo for gaps, run the next item, then re-arm. Never stop.
```
