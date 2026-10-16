const {spawn}=require('child_process');
const CH='C:/Program Files/Google/Chrome/Application/chrome.exe';
const W=+(process.argv[2]||1366);
const p=spawn(CH,['--headless=new','--remote-debugging-port=9333','--user-data-dir='+process.env.TEMP+'/cdpprof'+Date.now(),'--window-size='+W+',800','--host-resolver-rules=MAP * 10.255.255.1','about:blank']);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 await sleep(2500);
 const tabs=await (await fetch('http://127.0.0.1:9333/json')).json();
 const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl); let id=0; const pend={};
 ws.onmessage=e=>{const m=JSON.parse(e.data); if(pend[m.id]){pend[m.id](m.result);delete pend[m.id];}};
 await new Promise(r=>ws.onopen=r);
 const send=(method,params={})=>new Promise(r=>{const i=++id; pend[i]=r; ws.send(JSON.stringify({id:i,method,params}));});
 const ev=async e=>(await send('Runtime.evaluate',{expression:e,returnByValue:true})).result.value;
 await send('Page.navigate',{url:'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html'}); await sleep(5000);
 async function click(sel){
   const r=await ev(`(()=>{const e=document.querySelector('${sel}'); if(!e) return null; e.scrollIntoView({block:'center'}); const b=e.getBoundingClientRect(); const x=b.x+b.width/2,y=b.y+b.height/2; const top=document.elementFromPoint(x,y); return {x,y,top: top? top.tagName+'.'+top.className+'#'+top.id : null}})()`);
   if(!r) return console.log(sel,'NOT FOUND');
   for(const type of ['mousePressed','mouseReleased']) await send('Input.dispatchMouseEvent',{type,x:r.x,y:r.y,button:'left',clickCount:1});
   await sleep(1500);
   const vis=await ev(`[...document.querySelectorAll('section.page')].filter(s=>!s.hidden).map(s=>s.id).join(',')+' hash='+location.hash+' err='+(document.documentElement.getAttribute('data-jserr')||'')`);
   console.log(sel,'| topElem:',r.top,'| visible:',vis);
 }
 console.log('start:', await ev(`[...document.querySelectorAll('section.page')].filter(s=>!s.hidden).map(s=>s.id).join(',')+' err='+(document.documentElement.getAttribute('data-jserr')||'')`));
 await click('.step-row[data-go="D8"]');
 await click('#nav a[href="#D1"]');
 await click('#nav a[href="#D7"]');
 await click('#qrefBtn');
 await click('#nav a[href="#HOME"]');
 ws.close(); p.kill(); process.exit(0);
})().catch(e=>{console.log('ERR',e);p.kill();process.exit(1)});
