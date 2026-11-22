#!/bin/bash
# Build one episode end to end:  bash build.sh ep01-grid
#   voice (Kokoro, free, local) -> word timing -> check -> sound cues -> mix -> review sheet -> MP4 + cover
set -e
cd "$(dirname "$0")"
EP="${1:?usage: bash build.sh <episode-folder>}"
PY="${PY:-$HOME/.faceless-shorts/venv/bin/python}"
export CHROME="${CHROME:-$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome 2>/dev/null | head -1)}"
"$PY" -I scripts/voice.py "$EP"
"$PY" -I scripts/words.py "$EP"
cd "$EP"
node tools/capture.mjs check
node tools/capture.mjs cues
"$PY" tools/mix.py .
node tools/capture.mjs sheet review/all.jpg 0.5 6
node tools/capture.mjs video "renders/$EP.mp4"
echo "done: $EP/renders/$EP.mp4  (look at $EP/review/all.jpg before posting)"
