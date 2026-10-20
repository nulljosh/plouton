# Talli loop handoff (2026-10-20, afternoon)

## What the loop is

Talli is a BC disability benefits tracker on web, iPhone and Mac at talli.jaybulb.com. The loop runs forever toward native 5.0, then 10, 50 and 100, one theme per major, per roadmap.md. The name stays Talli everywhere. Keep the UI simple: every tool is one folded line that opens on tap, and Home is one number, one line and one action. A git push deploys nothing; ship the web with `npm run deploy`.

## Where things stand

- iOS 4.0.0 is live on the App Store.
- iOS 4.0.1 is ready to submit: build 202610201345 attached, six new iPhone screenshots, What's New, support and marketing URLs set. Waiting only on the animated header video.
- The header video (`launch/make_banner.sh`) renders Talli's six glyphs in scanlines on the landing blue. Glyphs go through rsvg because ImageMagick's own SVG reader drops masks, and the rules composite with DstIn so the gaps stay clear. `tools/test-banner.js` guards both.
- Mac 4.0.0 is still Prepare for Submission. Its attached build predates the Settings tab, so it gets rebuilt from main before submitting.
- Login and lawyers pages carry the landing wordmark top left. The privacy page names cookieless Cloudflare Web Analytics.

## Next, in order

1. Upload the header video to the iOS 4.0.1 product page, run `asc validate`, submit 4.0.1.
2. `asc workflow run ship-mac VERSION:4.0.0`, attach the new build, upload the four-tab desktop shots, submit.
3. When Mac is approved, flip the GitHub 4.0.0 release to Latest (#62).
4. Then 5.0 from roadmap.md, bugs first.

## For Joshua

- Check the contribution figures against your real account (#57).
- Say the word and the dead `src/session-store.js` and `tools/test-session-store.js` get deleted (nothing imports them).
- Real-device checks only you can do: reminders fire on the day, Watch handoff, vault encryption.

## Restart prompt

```
/loop Talli to v5, 10, 50, 100, forever: read ~/.claude/loops/talli.md, docs/LOOP-HANDOFF.md and roadmap.md, scan the repo for gaps, run the next item, then re-arm. Never stop.
```
