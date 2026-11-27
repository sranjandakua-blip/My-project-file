# Project notes for Claude

## Client feedback log

### 2026-11-27 — Flatmate storytime reel (`output/Flatmate_storytime_edit_v1.mp4`)
Client reviewed draft 1 and said it had **too much editing**; she wants a **lighter edit**.
No changes were requested on this video. Apply the lesson to future edits.

What v1 had (read as "too much"):
- 11 background changes (corduroy, gingham, grid, notebook, dots), one per story beat
- 3–5 animated header elements per beat (pills, stars, emoji stickers, strike-through gag, her/me lists)
- Word-by-word captions with italic-serif keyword emphasis
- Pop SFX on every header, whoosh on every background change, card "bump" on cuts

Default for this client going forward (lighter edit):
- **One background** for the whole video (or two max: one for the hook, one for the body). No per-beat changes.
- **Keep the raw ratio**: footage stays an uncropped 16:9 card inside the 9:16 frame (client asked for this explicitly).
- **Captions are the main graphic layer**: one word or a short phrase at a time, in the caption-reference style. Use emphasis sparingly (a few key words, not every beat).
- **Text headers only where they earn it**: the hook title at the start and the CTA at the end, plus at most 1–2 key moments (e.g. the punchline or quote). No emoji sticker lists or decorative stars on every beat.
- **Let the raw's existing inserts carry the visuals**; don't stack extra graphics on top of B-roll.
- **Minimal SFX**: a soft whoosh on the few real transitions; no pop on every text element.
- Before a full render, share 2–3 stills or a 10-second style test and confirm the intensity with the client.

## Workflow notes
- Raw/reference footage usually arrives in a Google Drive folder (raw clip plus "Design reference" and "Caption reference" subfolders).
- Hinglish audio: transcribe with faster-whisper `large-v3`, `language="hi"`, in short chunks for messy stretches, then romanise the captions by hand.
