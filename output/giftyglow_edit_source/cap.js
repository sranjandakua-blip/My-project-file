const { chromium } = require('playwright');
const O='cap/';
async function clean(p){
  await p.waitForTimeout(2500);
  await p.evaluate(()=>{
    // remove modal popups/overlays that are fixed & cover the screen
    for (const el of document.querySelectorAll('body *')){
      const cs=getComputedStyle(el);
      if((cs.position==='fixed')&&el.offsetWidth>300&&el.offsetHeight>500) el.remove();
    }
    document.body.style.overflow='auto';document.documentElement.style.overflow='auto';
  });
  await p.waitForTimeout(500);
}
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:540,height:960},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const p=await ctx.newPage();
 const go=async u=>{await p.goto('https://giftyglow.com/'+u,{waitUntil:'networkidle',timeout:60000}).catch(e=>console.log(e.message)); await clean(p);};
 await go('');
 // scroll through to trigger lazy images
 for(let y=0;y<12000;y+=600){await p.evaluate(y=>window.scrollTo(0,y),y);await p.waitForTimeout(150);}
 await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(1200);
 await p.screenshot({path:O+'home_top.png'});
 await p.screenshot({path:O+'home_full.png',fullPage:true});
 for (const u of ['birthday-lamps','couple-lamps','festival-religious','couple-lamps/happy-wedding-day-couple','couple-lamps/calendar-couple','custom-design']){
   await go(u);
   for(let y=0;y<3000;y+=500){await p.evaluate(y=>window.scrollTo(0,y),y);await p.waitForTimeout(150);}
   await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(800);
   await p.screenshot({path:O+u.replace(/\//g,'_')+'.png',fullPage:true});
 }
 await go('couple-lamps/ballon-heart-couple');
 await p.screenshot({path:O+'prod_full.png',fullPage:true});
 // customise flow
 const btn=p.getByText('Customise Your Lamp').first();
 await btn.scrollIntoViewIfNeeded(); await p.evaluate(()=>window.scrollBy(0,-250)); await p.waitForTimeout(400);
 await p.screenshot({path:O+'cust_00.png'});
 await btn.click(); await p.waitForTimeout(1200);
 await p.screenshot({path:O+'cust_01.png'});
 const i1=p.locator('input[placeholder="e.g. Aryan"]').first(), i2=p.locator('input[placeholder="e.g. Priya"]').first();
 let k=2;
 await i1.click();
 for(const ch of 'Aryan'){await i1.pressSequentially(ch);await p.waitForTimeout(80);await p.screenshot({path:O+`cust_${String(k++).padStart(2,'0')}.png`});}
 await i2.click();
 for(const ch of 'Priya'){await i2.pressSequentially(ch);await p.waitForTimeout(80);await p.screenshot({path:O+`cust_${String(k++).padStart(2,'0')}.png`});}
 await p.keyboard.press('Tab').catch(()=>{});await p.waitForTimeout(300);
 await p.screenshot({path:O+`cust_${String(k++).padStart(2,'0')}.png`});
 console.log('cust frames',k);
 await b.close();
})();
