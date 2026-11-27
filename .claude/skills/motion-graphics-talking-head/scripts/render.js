const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{
 const FPS=30;const TL=JSON.parse(require('fs').readFileSync(__dirname+'/timeline.json'));const NF=Math.round(TL.total*FPS);
 const ff=spawn('ffmpeg',['-v','error','-y','-i',__dirname+'/base.mp4','-f','image2pipe','-framerate','30','-c:v','png','-i','-',
   '-filter_complex','[0:v][1:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]','-map','[v]','-c:v','libx264','-preset','slow','-crf','16','-r','30',__dirname+'/video_noaudio.mp4'],{stdio:['pipe','inherit','inherit']});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/overlay.html');await p.evaluate(()=>window.ready);
 for(let i=0;i<NF;i++){
   await p.evaluate(t=>seek(t),i/FPS);
   const buf=await p.screenshot({omitBackground:true,type:'png'});
   if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
   if(i%150===0) console.log('frame',i);
 }
 ff.stdin.end();await b.close();
 ff.on('close',c=>console.log('ffmpeg exit',c));
})();
