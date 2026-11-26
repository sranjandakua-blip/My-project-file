---
name: nxtjob-reel-edit
description: Edit a NxtJob.ai talking-head reel (9:16) about one of the 9 AI agents (Nova, Navigator, Tailor, Hunter, Networker, Pitcher, Influencer, Interviewer, Negotiator) — stitch intro from an Instagram reel, Instagram-Edits style highlighter captions, screen recording of the agent card from nxtjob.ai, stock B-roll, mouse-click + notification SFX. Use when the user shares a Drive folder / raw video + reference reel and asks to "edit this video like the reference".
---

# NxtJob agent reel edit

Done once already for the **Negotiator** reel (`examples/negotiator.json`). Every new video follows the same
recipe; usually only the config changes.

## The brief (from the creator's voice notes, Hindi)
1. **Stitch first.** A reel link is given with "Keep the clip till 0:MM". Download it and put its first ~MM seconds
   at the very start, untouched (it already has its own headline + card on black). Add a yellow
   `*Stitch incoming*` label under the card. End on a sentence boundary near MM (check with the transcript).
2. **Captions — default `"caption_style": "yellow_word"`** (client's choice from the Networker reel on): white
   DM Sans ExtraBold **56px** (bundled in `fonts/`, closest free match to the Instagram Edits font), 1–2 short lines
   centred **above the head** (`caption_top` ≈ 240, adjust per video), and the **word being spoken turns butter
   yellow `#FFE27A`** (client: "font thode chote rakho aur highlight butter yellow me" — was 64px / `#F7C61E`;
   override with `caption_size` / `caption_color` only if asked). Effect is **either a hard (unblurred) drop shadow OR a dark outline — never both** (client rule:
   "hard shadow hai to outline hata do"). Default `"caption_effect": "shadow"`; use `"outline"` only if asked.
   No captions on the stitch (it has its own) and none while the agent card overlay covers the screen.
   Proofread captions without rendering: `python3 -I S/captions.py W/edit.json --list`.
   Older look, only if a video asks for it: `"caption_style": "highlighter"` — slate Inter Bold 46px with a white
   highlighter box sweeping word by word (the Negotiator reel).
3. **Overlays + B-roll.**
   - Screen-record the agent being discussed from https://nxtjob.ai (the "Meet your 9 AI Agent Taskforce"
     carousel) and overlay it while the agent / its features are described.
   - **Show the agent card's COMPLETE demo** (creator's rule since the Networker reel): one full cycle of the
     card's animation, from its first stage to its last (e.g. Networker: search → "Identifying hiring
     managers" → suggested list → "Initiating message" → drafted message), not a 3 s slice. Record at least
     two loops (`record_agent.js ... 30`) so a full cycle starting at stage 1 is available, find the cycle
     start/length on a contact sheet, and play it as one continuous overlay over the agent explanation. If
     the spoken span is shorter than the loop, set `"speed"` on the insert (up to ~1.5) so it still finishes;
     if longer, extend the overlay or follow it with a second, different-stage overlay.
   - **Client-supplied B-roll** (Drive `Instructions/B rolls/`, `Instructions/Hook clip/`): when the folder has its
     own clips and images, use THEM (all of them where they fit) instead of stock, each placed on the words it
     illustrates; the hook clip is the stitch. Stills (agent art, logos, diagrams) go in as
     `"kind": "image"` cards over the talking head: `file` or `files` (stacked), `width`, `y` (centre),
     `"card": true` for logos on white; they pop in and fade out. See `examples/nxtjob_overview.json`.
   - Otherwise add 5–6 job-related stock B-rolls to break monotony, ~1.5–3 s each, never back-to-back. Mix full-screen
     9:16 crops and "16:9 card on black" (captions stay visible above the card).
4. **Only two sound effects:** a mouse click whenever an overlay/B-roll appears, and a notification ping where
   the creator says "link" at the end (hold the last frame ~0.8 s so the ping finishes).

Do not add extra transitions — the raw footage already contains light-leak flashes between takes.

## Workflow
Work in a scratch dir `W`. Scripts are in `scripts/` next to this file (`S`).

1. **Get inputs.** `pip install gdown yt-dlp faster-whisper`, then
   `python3 -m gdown --folder <drive url> -O W/drive` and `python3 -m yt_dlp -o W/ig/stitch.%(ext)s <reel url>`.
   The Drive folder usually has: the raw video, `reference/` (a finished reel in the same style — often the
   *same script*; if so, match its beat placements), `instructions/` (screen recording of WhatsApp voice notes).
2. **Transcribe** (word timestamps): `python3 -I S/transcribe.py <video> medium en words > W/src_tr.txt`.
   Use language `hi` for voice notes. (Loads audio via ffmpeg→numpy; the installed PyAV is incompatible with
   faster-whisper's own decoder.)
3. **Inspect the raw video**: scene cuts (`select='gt(scene,0.25)'`) and letterboxed takes (measure black bars
   per segment). Letterboxed takes get cropped to fill the frame (`parts[].crop` in the config).
4. **Record the agent card**: `node S/record_agent.js "<card prompt text>" W/rec 30` (≥2 loops) then
   `python3 -I S/frames_to_video.py W/rec W/rec/agent.mp4`. Card prompts start with the agent's name, e.g.
   `"Negotiator, they offered"`, `"Navigator, I've got 14 years"`, `"Hunter, find me"`, `"Interviewer, mock-interview"`.
   Make a contact sheet of `agent.mp4` to find the timestamps of each animation stage (the loop is ~11 s).
   Why the script is unusual: CDP screencast only gives CSS-pixel frames (430 px wide = blurry), so it slows the
   page clock 5× (JS timers/rAF + `Animation.setPlaybackRate`) and takes full-res (DPR 2.5) screenshots, then
   retimes them to real speed.
5. **B-roll**: pexels/pixabay return 403 from the cloud sandbox; **mixkit works**. Search pages:
   `https://mixkit.co/free-stock-video/<query>/` → preview `https://assets.mixkit.co/videos/<id>/<id>-360.mp4`,
   HD `…/<id>-720.mp4`. Good ones already used: 8909 handshake over paperwork, 46022 interview panel,
   6022 interview conversation, 15795 silhouette handshake at window, 46750 meeting/presentation room.
   Others: 30012/34138/46755 handshakes, 28362/23112 signing, 18296/45703 money, 22961/42644 meetings.
   Make a contact sheet before choosing crop x for 9:16 (`crop=405:720:X:0`).
6. **SFX** (mixkit): click `https://assets.mixkit.co/active_storage/sfx/2585/2585-preview.mp3`,
   notification `https://assets.mixkit.co/active_storage/sfx/2574/2574-preview.mp3`.
7. **Write the config** (copy `examples/negotiator.json`): all insert times are on the **raw-video timeline**
   (seconds, from the word timestamps). Place inserts on the words they illustrate.
8. **Build**: `python3 -I S/build_base.py W/edit.json` (≈2 min) then `python3 -I S/captions.py W/edit.json`
   (≈2 min) → `W/build/final.mp4`. Check a contact sheet of key moments and the caption chunk list it prints.
9. Deliver the mp4 (and loudness: both stitch and voice are normalised to −14 LUFS).
   **Export file name must include the date of the edit, as date-month-year** (client rule):
   `<Agent>_reel_<DD-MM-YYYY>.mp4`, e.g. `Tailor_reel_25-11-2026.mp4`; take the date from `date +%d-%m-%Y` on the
   day you render. For a revision of the same video on the same day add `_v2`, `_v3`
   (`Tailor_reel_25-11-2026_v2.mp4`).

## Gotchas
- `rm` with globs on relative dirs is blocked by the sandbox safety check — use fresh directories instead.
- Screenshots of a Framer page: hide the sticky bottom CTA bar (the record script does this).
- Channel logo on the stitch clip (e.g. "EI" on Raj Shamani clips): `stitch.delogo: [[x, y, w, h]]` in the clip's own pixels.
- Non-9:16 raw video is zoomed to fill, which moves the head up: set `caption_top` (e.g. 250) so captions stay above it.
- Misheard phrases / split tokens: `phrase_fix: [["heard words", "correct words"]]`.
- Caption text fixes go in the config `replace` list (e.g. Nextjob→NxtJob, merge ".ai", "Rs .199" → "rupees 199").
