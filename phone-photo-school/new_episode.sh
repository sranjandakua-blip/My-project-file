#!/bin/bash
# Start a new episode from the latest finished one:  bash new_episode.sh ep02-tap-to-focus [ep01-grid]
# Copies the engine + kit (not the timing, audio, renders or review frames). Then edit script.json and src/shots.js.
set -e
cd "$(dirname "$0")"
NEW="$1"; SRC="${2:-ep01-grid}"
[ -z "$NEW" ] && { echo "usage: bash new_episode.sh <epNN-name> [source-episode]"; exit 1; }
[ -e "$NEW" ] && { echo "$NEW already exists"; exit 1; }
mkdir -p "$NEW/data"
cp -r "$SRC"/{index.html,fonts,src,tools,script.json} "$NEW"/
echo "created $NEW (from $SRC). Next: edit $NEW/script.json and $NEW/src/shots.js"
