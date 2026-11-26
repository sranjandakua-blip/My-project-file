# Flatmate storytime reel ("never move in with your best friend")

Trial edit of `IMG_3133.MP4` (4K HLG, 16:9 picture letterboxed in a 9:16 frame, Hinglish talking head),
cut in the style of the client's **new reference** (Hinglish storytelling reel) and compared against the
**old reference** (their current edits: 16:9 on black, minimal serif text, meme cutaways).

Output: `Flatmate_storytime_reel_DD-MM-YYYY.mp4`, 1080x1920, 30 fps, 91.8 s, -14 LUFS / -1 dBTP.

## What the edit does
| Element | New reference | This edit |
|---|---|---|
| Frame | full-bleed 9:16 | letterbox removed, 9:16 crop per shot centred on the face (OpenCV face track), punch-ins on beats, slow push in every shot |
| Colour | SDR | HLG -> BT.709 primaries conversion + light contrast (natural skin, no blown whites) |
| Story visuals | AI stills, torn-paper blob reveals on white | 13 stock clips revealed with procedural torn-paper blobs on a paper-white background |
| Captions | stacked white Poppins + magenta serif emphasis | same: Poppins ExtraBold + Playfair Display (#FA2EEC), word-timed pop-in, hand-romanised Hinglish |
| Extras | — | MINE/HERS tape labels on the fridge, utility-bill cards, OTP notification, Kotak 811 punch + chime |
| End | FOLLOW FOR MORE + cover frame | same, cover = red duotone freeze "NEVER MOVE IN WITH YOUR BEST FRIEND!" |
| Audio | music bed + SFX | cleaned/levelled voice, Mixkit "Lo-Fi 02" bed (lifts on the end card), paper/pop/whoosh SFX |

Safe zones: captions centred at y=1380 (block stays between ~1250 and ~1510), inside x 130-950; nothing
important in the bottom 320 px or the right 120 px rail.

## Rebuild
Work dir `W` needs: `drive/IMG_3133.MP4`, `fonts/` (Poppins ExtraBold/SemiBold, PlayfairDisplay[wght], Anton,
PermanentMarker from github.com/google/fonts), `broll/<id>.mp4` (Mixkit `https://assets.mixkit.co/videos/<id>/<id>-720.mp4`,
ids in `INSERTS` in `code/edit.py`), `sfx/<id>.mp3` (Mixkit `.../active_storage/sfx/<id>/<id>-preview.mp3`),
`music/764.mp3` (`https://assets.mixkit.co/music/764/764.mp3`), plus `captions.txt` and `faces.json` from here.

```bash
# SDR intermediate of the letterboxed picture (x264 rounds 1215 -> 1214 rows)
ffmpeg -i drive/IMG_3133.MP4 -vf "crop=2160:1215:0:1312,zscale=tin=arib-std-b67:t=arib-std-b67:pin=bt2020:p=bt709:min=bt2020nc:m=bt709:rin=tv:r=tv,format=yuv420p,eq=contrast=1.06:gamma=0.94:saturation=1.08,fps=30" -an -c:v libx264 -crf 13 -preset veryfast sdr_inner.mp4
python3 -I code/edit.py $W preview 4.9 30.9 67.2   # stills in $W/prev
python3 -I code/edit.py $W render                  # $W/build/video.mp4 (~4 min)
python3 -I code/mix.py  $W                         # $W/build/mix.wav
ffmpeg -i build/video.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart out.mp4
```

## Notes
- Whisper with `language=en` translates Hinglish into English; with `hi` on the whole file it loops. Chunk the
  audio at the raw jump cuts (`code/tr_chunks.py`) and romanise by hand into `captions.txt`.
- "Kota Gate 11" in the transcript is the sponsor **Kotak 811** — confirm the exact brand styling with the client.
