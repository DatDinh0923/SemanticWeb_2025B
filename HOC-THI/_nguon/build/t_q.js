const {spawn} = require('child_process');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const p = spawn(CH, ['--headless=new', '--remote-debugging-port=9344', '--user-data-dir=' + process.env.TEMP + '/cdpq' + Date.now(), 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await sleep(2500);
  const tabs = await (await fetch('http://127.0.0.1:9344/json')).json();
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); let id = 0; const pend = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; } };
  await new Promise(r => ws.onopen = r);
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  const ev = async e => (await send('Runtime.evaluate', {expression: e, returnByValue: true})).result.value;
  await send('Page.navigate', {url: 'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html#D8'}); await sleep(3000);
  for (const bi of [2, 44]) console.log(bi, JSON.stringify(await ev(`(()=>{const b=[...document.querySelectorAll('#p-D8 .codebar button')][${bi}]; return b.closest('.codebar').previousElementSibling.textContent.slice(0,400)})()`)));
  ws.close(); p.kill(); process.exit(0);
})();
