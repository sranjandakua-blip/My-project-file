# Phone Photo School

An Instagram series that teaches phone photography step by step, from the basics to Pro mode, shot on the S26 Ultra.
Each post is a **15-second 9:16 flat-2D animated reel** with an AI voiceover, word-synced captions, sound effects and a quiet music bed.
Everything is generated in code and costs nothing. No AI images, and no paid APIs.

Sample: [`ep01-grid/renders/ep01-grid.mp4`](ep01-grid/renders/ep01-grid.mp4), *Lesson 01: The Grid*.

## Format of every episode (keep it consistent)
| beat | time | what |
|---|---|---|
| Hook | 0–2 s | a question, phone rises with the camera app open |
| Lesson card | 2–3.5 s | `LESSON 0N` + the topic pill |
| How | ~3 s | where the setting is, shown on a phone screen (tap, slide, toggle) |
| Rule / demo | ~3 s | the big viewfinder showing the idea |
| Wrong vs right | ~3 s | red X on the mistake, then the fixed shot with a green check |
| End card | ~3 s | + FOLLOW and the NEXT lesson teaser |

Script: **~38–42 words** (≈15 s at voice speed 1.08), one line per cut, written the way you'd say it out loud.

## Make the next episode
```bash
bash new_episode.sh ep02-tap-to-focus      # copies the engine + kit from ep01
# edit ep02-tap-to-focus/script.json  (lines + caps: "|" splits captions, "*" marks the one yellow word)
# edit ep02-tap-to-focus/src/shots.js (one shot per line; set LESSON = 2)
bash build.sh ep02-tap-to-focus            # voice → timing → mix → review sheet → MP4
```
First time on a new machine: `python3 -m venv ~/.faceless-shorts/venv && ~/.faceless-shorts/venv/bin/pip install numpy scipy kokoro-onnx faster-whisper`
(the Kokoro voice model, about 340 MB, downloads automatically). You also need Node 22+, ffmpeg and Chrome (set `CHROME=/path/to/chrome`).

**Voice:** `af_heart` (warm US female). Other options: `am_michael` (steady male), `bm_george` (UK documentary), `af_bella` (bright).
Change `"voice"` in script.json. To use your own voice instead, record it and run `scripts/words.py <ep> --audio my_take.m4a`.

**Kit** (`src/core/kit.js`): `studio` background · `phone` + `cameraApp` (viewfinder, zoom chips, modes, shutter) · `settings`
screen with `toggle` · `scene` landscape + `tree` subject · `grid` · `hotspot` · `tap` ripple · `redX` · `check` · `pill` · `print`
(photo print) · `flash` · `aperture` (series motif) · `seriesBadge`. Add new components there in the same flat look:
teal = camera UI, yellow = the one key thing, red = wrong, green = right.

**Sound cues:** `whoosh pop tap shutter slide sparkle slam thud tock zip …` (see `tools/mix.py`).

## Suggested lesson roadmap
1. The Grid (rule of thirds) ✅
2. Tap to focus + brightness slider
3. Clean your lens (seriously)
4. Zoom lenses: .6 / 1x / 3x / 5x, when to use each
5. Leading lines
6. Shoot in the golden hour
7. Portrait mode and background blur
8. Night mode: hold still
9. HDR and backlit subjects
10. RAW vs JPEG (Expert RAW)
11. Pro mode 1: ISO
12. Pro mode 2: shutter speed
13. Pro mode 3: white balance
14. Pro mode 4: manual focus
15. Long exposure light trails
16. Editing basics in the gallery app

Built on the engine from `faceless-shorts-skill.zip` (Inside Out style), restyled for photography.
