# Phone Photo School

An Instagram series that teaches phone photography step by step, from the basics to Pro mode, shot on the S26 Ultra.
Each post is a **~25-second 9:16 flat-2D animated reel** with an AI voiceover, word-synced captions, sound effects and a quiet music bed.
Everything is generated in code and costs nothing. No AI images, and no paid APIs.

Every end card shows the creator avatar (a flat cartoon drawn from the profile photo, `avatar()` in kit.js) above @the_linse_art (`HANDLE` in kit.js). Finished: Lessons 01–05 (`epNN-*/renders/*.mp4`, each with a cover JPG). Instagram captions and hashtags are in [POSTS.md](POSTS.md).

## Format of every episode (keep it consistent)
| beat | time | what |
|---|---|---|
| Hook | 0–2 s | a question, phone rises with the camera app open |
| Lesson card | 2–4 s | `LESSON 0N` + the topic pill |
| Why / how | ~6 s | what goes wrong + where the setting is (tap, slide, toggle) |
| Demo | ~6 s | the big viewfinder showing the idea |
| Wrong vs right + pro tip | ~5 s | red X on the mistake, the extra tip, green check |
| End card | ~3 s | cartoon avatar, @the_linse_art, + FOLLOW, NEXT lesson |

Script: **~65–70 words** (≈24–26 s at voice speed 1.08), 9–10 lines, one line per cut, written the way you'd say it out loud.

## Make the next episode
```bash
bash new_episode.sh ep02-tap-to-focus      # copies the engine + kit from ep01
# edit ep06-golden-hour/script.json  (lines + caps: "|" splits captions, "*" marks the one yellow word)
# edit ep06-golden-hour/src/shots.js (one shot per line; set LESSON = 6)
bash build.sh ep06-golden-hour            # voice → timing → mix → review sheet → MP4
```
First time on a new machine: `python3 -m venv ~/.faceless-shorts/venv && ~/.faceless-shorts/venv/bin/pip install numpy scipy kokoro-onnx faster-whisper`
(the Kokoro voice model, about 340 MB, downloads automatically). You also need Node 22+, ffmpeg and Chrome (set `CHROME=/path/to/chrome`).

**Voice:** `af_heart` (warm US female). Other options: `am_michael` (steady male), `bm_george` (UK documentary), `af_bella` (bright).
Change `"voice"` in script.json. To use your own voice instead, record it and run `scripts/words.py <ep> --audio my_take.m4a`.

**The creator's photos:** `brand/photos/*.jpg` (copied into each episode's `assets/photos/`), drawn with `photoFinder()`, `photoPrint()` and `photo()` in kit.js
(cover-fit with a focus point, plus simulated blur / exposure / smudge haze / pixel crop) and tagged with `shotTag()` ("SHOT ON S26 ULTRA").
**The camera UI** (`cameraApp()`, `settings()`) is drawn from the creator's own One UI screenshots: top icons, 3:4 viewfinder with grid + level reticle,
zoom row .6 · 1× · 2 · 3 · 5 · 10 · 100 with the ⁘ button, quick-settings bar (gear, flash, timer, 3:4, 12M), white shutter, PORTRAIT · PHOTO · VIDEO · MORE,
and Camera settings › General › Composition guide (Grid lines and level).

**Brand:** `brand/logo-mark.png` (SR monogram, shown in the series badge) and the same monogram as the closing logo sting (last ~1.9 s, `logoSting()` in kit.js; no name or tagline text). `brand/logo-full.png` is kept for other uses are copied into each episode's `assets/`. Episodes use `"outro": 3.0` so the end card and the sting both fit.

**The creator's phone:** `phoneBack()` is drawn after the S26 Ultra (navy, raised 3-lens pill island, 5x lens + flash + sensor column, no logo); `{ inCase: true }` draws the light-blue case with the camera slider. Front edges use the navy frame colours in `lib.js`.

**Kit** (`src/core/kit.js`, the same in every episode): `finder` big viewfinder · `lessonCard` · `endCard` · `focusRing` · `sunSlider` · `phoneBack` + `lens` · `finger` · `cloth` · `shirt` · `leadArrows` · `scene` options (zoom, blur, bright, haze, flower, person, balloon, road) · `studio` background · `phone` + `cameraApp` (viewfinder, zoom chips, modes, shutter) · `settings`
screen with `toggle` · `scene` landscape + `tree` subject · `grid` · `hotspot` · `tap` ripple · `redX` · `check` · `pill` · `print`
(photo print) · `flash` · `aperture` (series motif) · `seriesBadge`. Add new components there in the same flat look:
teal = camera UI, yellow = the one key thing, red = wrong, green = right.

**Sound cues:** `whoosh pop tap shutter slide sparkle slam thud tock zip …` (see `tools/mix.py`).

## Suggested lesson roadmap
1. The Grid (rule of thirds) ✅
2. Tap to focus + brightness slider ✅
3. Clean your lens (seriously) ✅
4. Zoom lenses: .6 / 1x / 3x / 5x, when to use each ✅
5. Leading lines ✅
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
