---
name: talking-head-reel-edit
description: Edit a Hinglish talking-head course reel (9:16) for the AI/ML-course creator (blue-wall / red-kurta presenter) "like the reference" - keyword typography (small white Mali + big yellow Poppins) placed BEHIND the subject via a person matte, B-roll, generated screen recordings, logo/icon pops, synthesized music + SFX, WhatsApp phone-number CTA card, teal end card. Use when the user shares a Drive folder of raw videos + a reference reel / script doc and asks to edit them, add B-roll, or make text go behind the subject.
---

# Talking-head reel edit (AI/ML course creator)

First done Nov 2026 for "YouTube vs Real-World AI/ML" and "CIBIL Score Se Aage" (`examples/*.json`).

## Client rules (always apply)
1. **Under a minute.** Every export < 60 s (`reel.py` refuses >= 59.5 s unless `--allow-long`). Remove retakes/false
   starts and long pauses first; keep the end section short.
2. **Phone-number CTA, 2-3 s, BEFORE the final CTA frame.** WhatsApp pill `+91-8177988081` (black circle + WhatsApp
   logo, white pill, like the client's screenshot). Show `phone_card.png` as its own end-card state for 2-3 s, then the
   actual CTA frame (ENROLL NOW / COMMENT "COURSE" ...), which may repeat the pill underneath. `reel.py` warns if the
   end card has no `phone_card` state. Example end block:
   `"end": {"dur": 4.8, "states": [["phone_card.png", 0.0], ["end_x_2.png", 2.6], ["end_x_4.png", 3.2]]}`
3. **No text over the subject.** On talking-head shots all text / tiles / chips are drawn BEHIND her (person matte).
   Small text must stay fully clear of her; a big yellow keyword may tuck behind her head only with its lower 40%.
   Chips/buttons that would sit on her body go on B-roll/screen inserts or into free wall space instead.
4. Export name includes the edit date: `<Topic>_reel_<DD-MM-YYYY>.mp4` (`date +%d-%m-%Y`), revisions `_v2`, `_v3`.
5. Don't invent a brand: if the script names no institute, no logo on the end card (ask for one).

## Style (from the reference reel)
- Kinetic captions at the top: small white **Mali SemiBold 60px** connector words + big yellow `#FFE234`
  **Poppins Bold 140px** keywords, word-by-word char fade/rise, soft dark shadow; lines in Roman Hinglish, verbatim.
- App-icon tiles with labels pop (overshoot) when a tool/field is named; script's on-screen text as yellow/dark chips.
- Punch-in zooms at cuts (anchor zoom near the head top so the top band stays free), whip-blur between sections,
  warm light-leak on the last section change, shake + buzz on "error/rejected" moments, flash + bass hit on drops.
- Teal radial end card (Anton yellow/white); music bed ducked under voice, voice at -14 LUFS.

## Workflow (scratch dir `W`, scripts `S` = this skill's `scripts/`)
1. **Inputs**: `pip install gdown faster-whisper scikit-learn opencv-python-headless onnxruntime`;
   `python3 -m gdown --folder <url> -O W/drive` (Drive MCP can't download big files; gdown works for link-shared
   folders). Read the script doc (docx -> unzip word/document.xml).
2. **Transcribe** with `../nxtjob-reel-edit/scripts/transcribe.py <video> medium hi words`. Whisper word times run up
   to ~0.25 s late -> `word_lead`. **Find retakes**: look for digital-silence gaps (RMS < -60 dB = editor cut) and
   re-transcribe each speech island separately (no initial_prompt - it hallucinates). Cut the first take.
3. **Fonts** (Google Fonts CSS with an old UA returns TTF): Mali 600/700, Poppins 600/700/800, Inter 400/600/800,
   JetBrains Mono 400/700, Anton -> `W/fonts`. Icons: simple-icons + lucide-static via cdn.jsdelivr.net -> `W/icons`.
4. **B-roll**: Coverr works from the sandbox (`https://coverr.co/s?q=<query>` -> `cdn.coverr.co/videos/<slug>/1080p.mp4`,
   free license, skip `premium` slugs). Mixkit search is behind Cloudflare - don't try to get around it; mixkit asset
   CDN URLs still work for known IDs. Pexels/Pixabay 403. Contact-sheet clips before picking `ss`/`crop_x`; lift dark
   clips with `"eq"`. Avoid off-context clips (USD/crypto screens for an Indian finance reel).
5. **Generated screen recordings / graphics**: copy `examples/gen_assets_example.py` (+ `ml_example.py` to train a real
   small sklearn model so notebook numbers, confusion matrix and app output are genuine), render with
   `node S/shoot.js W/assets/jobs.json` (local HTML -> PNG via Playwright). Emoji don't render (no emoji font);
   Poppins has no arrow glyph (reel.py draws arrows with DejaVu).
6. **SFX/music**: `python3 -I S/audio_synth.py sfx W/sfx` (whoosh, pop, boom, buzz, typing, riser, chime) + mixkit
   click `2585` / ping `2574`. Music bed is synthesized per edit by reel.py (`music.full_from`, `drops`, `lufs` -25).
7. **Config** (copy an example): `keeps` (source-time cuts), `zooms` `[t, z, cy]`, `inserts` (video/image/seq),
   `dataflow`, `overlays` (pop/chips/states), `cards` (runs `[style, text, t, size_mul, [word times]]`), `fx`, `sfx`,
   `sfx_out` (output-time, end card), `music`, `end`. All times are raw-video seconds unless noted.
8. **Matte**: `python3 -I S/matte.py W/<vid>/edit.json W/models/modnet.onnx` (MODNet ONNX from
   `huggingface.co/Xenova/modnet/resolve/main/onnx/model.onnx`, ~0.4 s/frame on 4 CPUs). Re-run after changing `keeps`.
9. **Check layout**: `python3 -I S/reel.py edit.json --check` (card placement + subject occlusion per overlay; fix any
   `WARN` by splitting long cards into shorter ones or moving overlays), `--cards` (timeline), `--stills 1.5,7.2`.
10. **Render**: `python3 -I S/reel.py edit.json` (~3 min / 40 s reel). Audio-only tweak: `--audio-only` (remux).
    Verify with a contact sheet + `ebur128` (-14 LUFS, peak <= -1 dBTP).
11. **Deliver** via SendUserFile. Drive MCP uploads are capped (~3 MB per request) - full reels can't go to Drive from
    here; the client's shared folder is usually owned by another account and read-only.
