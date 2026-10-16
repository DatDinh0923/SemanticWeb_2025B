const {spawn} = require('child_process'); const fs = require('fs');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const p = spawn(CH, ['--headless=new', '--remote-debugging-port=9342', '--user-data-dir=' + process.env.TEMP + '/cdpmm' + Date.now(), '--window-size=1300,900', 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await sleep(2500);
  const tabs = await (await fetch('http://127.0.0.1:9342/json')).json();
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); let id = 0; const pend = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; } };
  await new Promise(r => ws.onopen = r);
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  const ev = async e => { const r = await send('Runtime.evaluate', {expression: e, returnByValue: true}); return r.result && r.result.value; };
  const [pid, idx] = process.argv.slice(2);
  await send('Page.navigate', {url: 'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html#' + pid}); await sleep(3000);
  await ev(`document.querySelectorAll('#p-${pid} details').forEach(d=>d.open=true)`); await sleep(4000);
  await ev(`document.querySelectorAll('#p-${pid} .mm-box')[${idx||0}].scrollIntoView({block:'start'}); window.scrollBy(0,-70)`); await sleep(500);
  const s = await send('Page.captureScreenshot', {format: 'png'}); fs.writeFileSync(__dirname + '/../shot_mm.png', Buffer.from(s.data, 'base64'));
  ws.close(); p.kill(); process.exit(0);
})();
