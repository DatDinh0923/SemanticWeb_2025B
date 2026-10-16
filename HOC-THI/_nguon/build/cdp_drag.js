const {spawn} = require('child_process');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const p = spawn(CH, ['--headless=new', '--remote-debugging-port=9334', '--user-data-dir=' + process.env.TEMP + '/cdpd' + Date.now(), '--window-size=1300,900', 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await sleep(2500);
  const tabs = await (await fetch('http://127.0.0.1:9334/json')).json();
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); let id = 0; const pend = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; } };
  await new Promise(r => ws.onopen = r);
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  const ev = async e => { const r = await send('Runtime.evaluate', {expression: e, returnByValue: true}); return r.exceptionDetails ? 'EXC ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description) : r.result.value; };
  await send('Page.navigate', {url: 'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html#TQ'}); await sleep(3000);
  await ev(`[...document.querySelectorAll('#p-TQ .codebar button')].find(b=>/Bảng vẽ/.test(b.textContent)).click()`); await sleep(3500);
  await ev(`document.documentElement.style.scrollBehavior='auto'; document.querySelector('#p-VE .pad').scrollIntoView({block:'start'})`); await sleep(300);
  async function drag(label) {
    const pos = await ev(`(()=>{const w=document.querySelector('#p-VE .widget'); const n=w._net; const id=Object.keys(n.getPositions())[0]; const p=n.getPositions([id])[id]; const d=n.canvasToDOM(p); const b=w.querySelector('.pad canvas').getBoundingClientRect(); const X=b.x+d.x, Y=b.y+d.y; const t=document.elementFromPoint(X,Y); return {id, x:X, y:Y, before:p, top: t ? t.tagName : null, physics: n.physics.options.enabled}})()`);
    console.log(label, 'node', JSON.stringify(pos));
    await send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: pos.x, y: pos.y});
    await send('Input.dispatchMouseEvent', {type: 'mousePressed', x: pos.x, y: pos.y, button: 'left', buttons: 1, clickCount: 1});
    for (let k = 1; k <= 10; k++) { await send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: pos.x + k * 8, y: pos.y + k * 5, button: 'left', buttons: 1}); await sleep(30); }
    await send('Input.dispatchMouseEvent', {type: 'mouseReleased', x: pos.x + 80, y: pos.y + 50, button: 'left', buttons: 1, clickCount: 1});
    await sleep(1500);
    console.log(label, 'after', JSON.stringify(await ev(`document.querySelector('#p-VE .widget')._net.getPositions(['${pos.id}'])['${pos.id}']`)), 'mode', await ev(`document.querySelector('#p-VE .widget')._net.manipulation.inMode`));
  }
  await drag('1');
  await ev(`document.querySelector('#p-VE .widget [data-a=edge]').click()`); await sleep(200);
  console.log('mode after edge btn', await ev(`document.querySelector('#p-VE .widget')._net.manipulation.inMode`));
  await ev(`document.querySelector('#p-VE .widget [data-a=move]').click()`); await sleep(200);
  await drag('2');
  ws.close(); p.kill(); process.exit(0);
})().catch(e => { console.log('ERR', e); p.kill(); process.exit(1); });
