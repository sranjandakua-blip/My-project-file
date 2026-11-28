#!/bin/bash
S=/tmp/claude-0/-home-user-My-project-file/b8f68f35-e422-5be6-8710-30ffbc413c24/scratchpad; cd $S/edit
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i concat.txt -c copy video.mp4
OUT=/home/user/My-project-file/Shruti_Sood_Showreel_9x16_$(date +%d-%m-%Y).mp4
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -i audio.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -maxrate 25M -bufsize 50M -profile:v high -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart -shortest $OUT
ls -la $OUT
