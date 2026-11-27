const {chromium}=require('playwright');
(async()=>{
 require('fs').mkdirSync(__dirname+'/pv',{recursive:true});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('console',m=>console.log('console',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/overlay.html');await p.evaluate(()=>window.ready);
 const ts=process.argv.slice(2).map(Number);
 for(const t of ts){await p.evaluate(t=>seek(t),t);await p.screenshot({path:`${__dirname}/pv/o_${t.toFixed(2).padStart(6,'0')}.png`,omitBackground:true});}
 await b.close();})();
