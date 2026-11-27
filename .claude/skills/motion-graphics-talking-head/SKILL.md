---
name: motion-graphics-talking-head
description: Edit a raw 9:16 talking-head video into a premium sub-60s reel with motion graphics. Picks the best take of each line, cuts every pause, and adds letter-by-letter typed gradient captions with soft keyboard ticks, Apple emojis that pop and wobble, full-screen motion-graphic cutaways and chapter cards, and speed-curved punch-ins with clean hard cuts. Also does a neutral-bright grade with a subtle vignette, SFX from the user's pack, and a speed-ramped slow-mo outro with curved "Byeeee" text. Use when the user shares a raw talking-head video (usually a Drive folder with a reference reel and an SFX pack) and asks to edit it like the reference, cut silences, bring it under a minute, add motion graphics, or says "motion graphics talking head".
---

# Motion-graphics talking-head reel

Built and iterated with the client over 5 rounds on the "3 things I'd check before posting" reel (Nov 2026).
The client signed off on v5. `examples/` holds that project's timeline, overlay and EDL. Reuse the pipeline and
the **style rules** below, and rewrite the cues, captions and scenes for each new script.

## Style rules (client feedback, do not regress)
- **≤ 60 s**, tight. Pick the cleanest take of each line, cut every pause > ~0.13 s, then speed voice + video
  together to **1.08×** (pitch preserved). Drop filler words at take starts (e.g. "or"); `silence_edl.py`'s 4th
  takes field sets an exact start for that.
- **Edit only, never a raw/edit comparison layout**, even when the reference reel is a comparison ad.
- **Clean hard cuts** for take changes, cutaways and chapter cards. No colour flashes, slide or blur transitions.
  Motion lives inside shots:
  - punch-in zoom ramps (fast start, soft land, 0.24 s)
  - post-cutaway "settle" (+12% easing out over 0.4 s)
  - fast-slow-fast scale on graphics (`rampIn`/`rampOut`)
- **Captions:** reference "than ever" look.
  - **Big line:** Inter Display Bold 116 px, tracking −0.06em, lowercase. Horizontal gradient across the whole
    phrase (white → #C9C9C9 → #B4B4B4), set per character with `background-size` = line width and
    `background-position` = −char offset. Soft drop shadow.
  - **Accent words:** white → #EBCBB3 → #DDB08E.
  - **Small line:** above the big line, Inter Display 600, 52 px, white.
  - **Reveal:** letter by letter at word time. Sits at y ≈ 1190 (lower chest).
- **Typing SFX:** the soft synthesized "tock" (`make_ticks.py`, ~1.5 kHz centroid).
  - The bright clicky version was "irritating to the ear".
  - Density: **1 tick per small word, 2 per big word**, plus every word start or third letter of typed graphic titles.
  - Gain: big words −19 dB, small words −22 dB, titles −20 dB (±1.5 dB random), using one of 4 variants at random.
- **Apple emojis only** (never Noto/Android, including inside HTML text, e.g. 💬 → `<img>`).
  - One emoji per caption group, tied to its keyword, alternating left and right of the big line.
  - Motion: spring pop with spin-in, wobble, bob, squash-and-stretch pulse, then a quick shrink exit.
  - Bursts of 7 mini copies on 💯 🔥 ❤️‍🔥 🎉, flying in the upper half only so captions stay clear.
- **Hide awkward expressions** (eye-rolls, looking down) with a **full-screen** graphic over those words,
  not a small overlay. On this reel that was "are people engaging with your posts?" → post-card scene.
- **Grade:** neutral-clean, a bit brighter than raw, only a hint of warmth (`make_grade.py`).
  - A warm teal/orange matte grade was rejected as "yellowish and darker".
  - Vignette max 13% at the far corners.
- **Voice:** keep it close to the raw. Mono → `atempo` → 60 Hz HPF → 1.8:1 gentle comp → static gain to
  −15 LUFS. **No** `afftdn`, no EQ, no dynamic `loudnorm`, no stereo `rubberband` (smeared the phase and the
  client heard the quality drop). Mix limiter at 0.94 and AAC at 320k.
- **Ending must complete.** After "follow me" add a ~2.3 s outro:
  - the footage speed-ramps 1.08× → 0.22× slow-mo on the wave (motion-interpolated), then holds with a slow push
  - a Follow button pops, a cursor glides in and clicks, an orange ripple goes out, and it flips to "Following ✓"
  - 🎉 🙌 pop in
  - **"Byeeeee"** flows in along a wavy SVG path in the theme gradient (Montserrat 900, 196 px), letters bobbing
- **Hook:** the first ~0.9 s shows the video in a rounded card on a peach gradient with 4 "thinking" emojis
  (🤔 🧐 😬 🫣) around it. The card then whips open to full frame.
- **SFX from the user's pack:**
  - cinematic whooshes (timed so the **peak** lands on the cut)
  - sub-drops on chapter-card cuts
  - clicks and UI selects on pops
  - bells for "working", "Wrong" for "not working", Notification for "save"
  - Peak-normalise each file, then apply gain.

## Workspace layout
```
WS/                      (scratchpad)
  dl/raw.mp4 ref.mp4     downloads (Drive public: drive.usercontent.google.com/download?id=..&export=download&confirm=t;
                         private files: Google Drive connector download_file_content → saved .bin in tool-results)
  work/a16.wav tx.json   16 kHz mono s16 of raw + full transcript
  sfx/*.wav              pack files you use (whoosh01.., subdrop01.., click02.., select01.., bells, wrong, notification, hud01) + tick0..3
  apple/sheet_<code>.png Apple emojis 180 px + meta.json
  build/                 copy scripts/* + examples here, run everything from here
```

## Pipeline (run from `build/`)
1. **Study the reference.** Make a contact sheet (`ffmpeg -vf fps=2,scale=240:-1,tile=8x6`) and note its caption
   style, cutaway types and SFX moments.
2. **Find the takes.**
   - `ffmpeg -i ../dl/raw.mp4 -ac 1 -ar 16000 ../work/a16.wav`
   - `python3 transcribe.py ../work/a16.wav ../work/tx.json`
   - Pick the best take of each line. Write `takes.json` as `[["hook",71.6,77.4],...]`, with a 4th value to force
     a start that drops a filler word.
3. `python3 silence_edl.py takes.json` writes `edl.json`. Check the energy profile if a soft first word might clip.
4. `python3 align.py` writes `words.json` (word indices printed per take), then `python3 faces.py`.
5. Write `timeline.py` (start from `examples/timeline_example.py`):
   - cues `C` anchored to `W(take,i)`
   - zoom keys `Z` (`cut`/`ramp`/`settle`)
   - caption groups `G` = (take, small-word range, big-word range, accent, emoji)
   - typed graphic titles, scene emojis `E`, bursts, SFX
   - `C['tail']` for the outro
   - Then run `python3 timeline.py` to write `timeline.json`, `timeline.js` and `sfx.json`.
6. Prepare assets:
   - `python3 make_grade.py`, `python3 make_ticks.py`, `python3 apple_emoji.py`
   - Copy the pack SFX into `../sfx/`.
7. `python3 base.py` writes `base.mp4`. It takes a few minutes, so run it as a **background job**. Don't
   `&` it inside a shell, or it gets killed when that shell exits.
8. Build `overlay.html` from `examples/overlay_example.html`:
   - The scenes are all driven by `window.TL` and a deterministic `seek(t)`.
   - Preview with `node preview.js 2.4 9.0 ...` (writes `pv/`), and overlay the PNGs on `base.mp4` frames in a
     contact sheet to check.
9. Audio and final render:
   - `python3 audio.py` writes `mix.wav`. Check it's about −14.5 LUFS with a peak around −1 dBFS.
   - `node render.js` writes `video_noaudio.mp4` (Playwright screenshots piped into ffmpeg; ~1,400 frames in about 6 min).
   - Mux: `ffmpeg -i video_noaudio.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart out.mp4`
10. QA:
    - `python3 contact_sheet.py out.mp4 sheet.png <times>` across every scene and the ending.
    - Re-transcribe the cut to confirm the script reads cleanly.
    - Send the file to the user (SendUserFile) and commit it to `output/` on the session branch.

## Scene library (in `examples/overlay_example.html`)
| id | use for | notes |
|---|---|---|
| `prof` | "your Instagram account" | profile card with post grid, pops at a tilt |
| `chips` | "3 things" | numbered circles pop in |
| `ch1` | chapter card, dark | spotlight beam sweeps onto audience icons; typed title |
| `feed` | "stop scrolling" | phone feed fast-scrolls then brakes; highlighted post shakes |
| `ch2` | chapter card, orange split | band drops, letters rise, script word wipes on, swinging price tag |
| `scr` | key phrase | script line wipes on, big typed word, underline draws |
| `ch3` | chapter card, cream | 3×3 post grid flies in, magnifier sweeps, weak tiles dim |
| `wk` | working vs not working | two cards slide in, check/cross draw, bar charts grow/fall |
| `engF` | engagement (full screen) | post card, double-tap heart, counters, rising hearts |
| `rch` | small stat chip | "Reach −38%" pill |
| `ana` | "right now" / analytics | dark dashboard, line draws, LIVE dot, KPIs count up |
| `sav` | "save this" | bookmark fills + "Saved to collection" toast |
| `fol` + `byeS` | outro | Follow → click ripple → Following ✓; curved "Byeeeee" |

Rules for scenes:
- Every full-screen scene is shown only inside its `[a,b)` window: a clean cut in and out, with `sceneWrap`
  applying the speed-curve scale.
- Captions get a hard stop at each cutaway start (`STOPS` in the timeline).
- Typed titles use the `typedAt` helper. Wrap each word in a `nowrap` span, otherwise titles break mid-word.

## Gotchas
- faster-whisper on Python 3.13 with a new PyAV: pass a numpy array, not a path, or `av.open(...metadata_errors)` fails.
- `cv2.CascadeClassifier` is missing in OpenCV 5. Use `pip install "opencv-python-headless<5"`.
- Phone footage is often HEVC with a rotation flag. ffmpeg auto-rotates, so `faces.py` reads the decoded frame size.
- Whisper word times drift on long clips. `align.py` re-transcribes each kept take separately, which keeps it tight.
- In the hook card, clamp the card scale to ≤ 1, or numpy broadcasting crashes at the end of the expansion.
- The Apple emoji CDN sometimes returns 403. Retry, or use the Emojipedia URL `em-content.zobj.net/source/apple/391/<name>_<code>.png`.
- Don't `rm` with globs in relative dirs; the sandbox blocks it.
- Placeholder data in graphics (@yourbrand, follower counts, stats) must be flagged to the user every time.
