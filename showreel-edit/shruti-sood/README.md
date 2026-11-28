# Shruti Sood – live showreel (9:16, ~45s)

Beat-synced live-gig reel cut from the 4K vertical camera clips (B00xx.MP4) in the
"Sample videos showreel" Drive folder, styled after the two reference reels.

- **Music:** live camera audio from B0013, 78.88s → 123.62s (~143.6 BPM), loudnorm -14 LUFS.
- **Cuts:** snapped to tracked beats (`plan.json` → `shots`, timeline seconds + source in-points).
  Shots marked `SYNC` in `plan.py` are B0013 itself, so lip-sync matches the audio.
- **FX:** punch-ins / slow push-ins, B&W accents, white flash on hits, grain + vignette,
  "Shruti Sood · LIVE" title (`title.png`) and end card (`endcard.png`).

## Re-render
1. Put the raw clips in `<scratch>/raw/` and B0013 beat times in `<scratch>/b13_beats.npy`
   (paths are set at the top of each script).
2. `python3 plan.py` → `plan.json`
3. `python3 render.py` (or `python3 render.py 4 28` for single shots)
4. Build `audio.wav` from B0013 (see README timings) and run `./assemble.sh`.

Output goes to `videos/` (git-ignored; the master is >100 MB).
