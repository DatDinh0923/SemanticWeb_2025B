// Kiểm tra tự động toàn bộ web: node audit.js [shot1,shot2,...]
const {spawn} = require('child_process');
const fs = require('fs');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9341;
const p = spawn(CH, ['--headless=new', '--remote-debugging-port=' + PORT, '--user-data-dir=' + process.env.TEMP + '/cdpaudit' + Date.now(), '--window-size=1300,900', 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const shots = (process.argv[2] || '').split(',').filter(Boolean);
(async () => {
  await sleep(2500);
  const tabs = await (await fetch('http://127.0.0.1:' + PORT + '/json')).json();
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); let id = 0; const pend = {}; const logs = [];
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; }
    else if (m.method === 'Runtime.exceptionThrown') logs.push('EXC ' + JSON.stringify(m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text).slice(0, 300));
    else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') logs.push('CONSOLE ' + JSON.stringify(m.params.args.map(a => a.value || a.description)).slice(0, 300)); };
  await new Promise(r => ws.onopen = r);
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  const ev = async e => { const r = await send('Runtime.evaluate', {expression: e, returnByValue: true, awaitPromise: true}); return r.exceptionDetails ? 'EXC ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description) : r.result.value; };
  await send('Runtime.enable');
  await send('Page.navigate', {url: 'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html#HOME'}); await sleep(3000);
  const ids = await ev(`[...document.querySelectorAll('section.page')].map(s=>s.id.slice(2))`);
  const bad = [];
  for (const pid of ids) {
    await ev(`location.hash='${pid}'`); await sleep(1200);
    await ev(`document.querySelectorAll('#p-${pid} details').forEach(d=>d.open=true)`); await sleep(1500);
    // chờ mermaid vẽ xong
    for (let k = 0; k < 20; k++) { const left = await ev(`[...document.querySelectorAll('#p-${pid} .mm-box')].filter(b=>!b.querySelector('svg') && !b.querySelector('.err')).length`); if (!left) break; await sleep(500); }
    const r = await ev(`(()=>{const p=document.getElementById('p-${pid}');
      const txt=p.innerText;
      const mm=[...p.querySelectorAll('.mm-box')]; const mmErr=mm.filter(b=>!b.querySelector('svg')).length;
      const gerr=[...p.querySelectorAll('.graph-box.err')].filter(g=>!g.closest('.work')).map(g=>g.textContent.slice(0,80));
      const rawBox=[...p.querySelectorAll('li')].filter(li=>/^\\s*\\[[ xX]\\]/.test(li.textContent)).length;
      const dead=(txt.match(/files\\/|\\b0\\d-[\\w-]+\\.md|rdfs_closure|run_queries/g)||[]);
      const dcode=(txt.match(/\\(D\\d+\\)\\s*:/g)||[]);
      const h2=[...p.querySelectorAll(':scope > h2')].map(h=>h.textContent.slice(0,40));
      return {chars:txt.length, h2, mm:mm.length, mmErr, gerr, rawBox, barem:p.querySelectorAll('input.barem').length, work:p.querySelectorAll('.work').length, dead:dead.slice(0,5), dcode:dcode.slice(0,5), next:!!p.querySelector('.nextpage')};})()`);
    console.log(pid, JSON.stringify(r));
    if (r.mmErr || r.gerr.length || r.rawBox || r.dead.length || r.dcode.length) bad.push(pid);
    if (shots.includes(pid)) {
      await ev(`document.querySelectorAll('#p-${pid} details').forEach(d=>d.open=false); window.scrollTo(0,0)`); await sleep(400);
      const s = await send('Page.captureScreenshot', {format: 'png'}); fs.writeFileSync(__dirname + '/../shot_' + pid + '.png', Buffer.from(s.data, 'base64'));
    }
  }
  console.log('JSERR', await ev(`document.documentElement.getAttribute('data-jserr')`));
  console.log('LOGS', logs.length ? logs.join('\n') : 'none');
  console.log('BAD', bad.join(',') || 'none');
  ws.close(); p.kill(); process.exit(0);
})().catch(e => { console.log('ERR', e); p.kill(); process.exit(1); });
