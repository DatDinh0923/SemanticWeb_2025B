const {spawn} = require('child_process');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const p = spawn(CH, ['--headless=new', '--remote-debugging-port=9345', '--user-data-dir=' + process.env.TEMP + '/cdpc' + Date.now(), '--window-size=1300,900', 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await sleep(2500);
  const tabs = await (await fetch('http://127.0.0.1:9345/json')).json();
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); let id = 0; const pend = {}; let answer = null;
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; }
    else if (m.method === 'Page.javascriptDialogOpening') send('Page.handleJavaScriptDialog', answer === null ? {accept: false} : {accept: true, promptText: answer}); };
  await new Promise(r => ws.onopen = r);
  const ev = async e => (await send('Runtime.evaluate', {expression: e, returnByValue: true})).result.value;
  await send('Page.enable');
  await send('Page.navigate', {url: 'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html#VE'}); await sleep(3000);
  await ev(`document.querySelector('#p-VE [data-a=clear]').click(); document.documentElement.style.scrollBehavior='auto'; document.querySelector('#p-VE .pad').scrollIntoView({block:'center'})`); await sleep(300);
  const b = await ev(`(()=>{const r=document.querySelector('#p-VE .pad canvas').getBoundingClientRect(); return {x:r.x+r.width/2, y:r.y+r.height/2}})()`);
  const clickAt = async (x, y) => { for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', {type, x, y, button: 'left', buttons: 1, clickCount: 1}); };
  // huỷ prompt
  await ev(`document.querySelector('#p-VE [data-a=iri]').click()`); await sleep(200); answer = null; await clickAt(b.x, b.y); await sleep(800);
  console.log('after cancel:', await ev(`document.querySelector('#p-VE .mode').textContent`), '| mode', await ev(`document.querySelector('#p-VE .widget')._net.manipulation.inMode`));
  // thêm literal có kiểu
  await ev(`document.querySelector('#p-VE [data-a=iri]').click()`); await sleep(200); answer = ':book'; await clickAt(b.x - 150, b.y); await sleep(600);
  await ev(`document.querySelector('#p-VE [data-a=lit]').click()`); await sleep(200); answer = '"2024-01-01"^^xsd:date'; await clickAt(b.x + 150, b.y); await sleep(600);
  await ev(`(()=>{const n=document.querySelector('#p-VE .widget')._net; const ids=n.body.nodeIndices; n.body.data.edges.add({from:ids[0], to:ids[1], label:'dc:date'}); })()`);
  await ev(`document.querySelector('#p-VE [data-a=move]').click()`); await sleep(300);
  console.log('nodes', await ev(`document.querySelector('#p-VE .widget')._net.body.nodeIndices.length`));
  ws.close(); p.kill(); process.exit(0);
})().catch(e => { console.log('ERR', e); p.kill(); process.exit(1); });
