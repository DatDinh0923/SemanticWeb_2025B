// Kiểm tra chức năng: selftest SPARQL/RDFS/Datalog, nút "Mở trong Playground", neo Đề cũ, Kiểm tra mệnh đề RDFS
const {spawn} = require('child_process');
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9343;
const p = spawn(CH, ['--headless=new', '--remote-debugging-port=' + PORT, '--user-data-dir=' + process.env.TEMP + '/cdpver' + Date.now(), '--window-size=1300,900', 'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const BASE = 'file:///C:/Users/hieunt15/SemanticWeb_OnTap/HOC-THI/index.html';
(async () => {
  await sleep(2500);
  const tabs = await (await fetch('http://127.0.0.1:' + PORT + '/json')).json();
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); let id = 0; const pend = {}; const logs = [];
  ws.onmessage = e => { const m = JSON.parse(e.data); if (pend[m.id]) { pend[m.id](m.result); delete pend[m.id]; } else if (m.method === 'Runtime.exceptionThrown') logs.push(JSON.stringify(m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description).slice(0, 200)); };
  await new Promise(r => ws.onopen = r);
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  const ev = async e => { const r = await send('Runtime.evaluate', {expression: e, returnByValue: true, awaitPromise: true}); return r.exceptionDetails ? 'EXC ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description) : r.result.value; };
  await send('Runtime.enable');

  // 1) selftest
  await send('Page.navigate', {url: BASE + '?selftest#HOME'});
  for (let k = 0; k < 120; k++) { await sleep(1000); if (await ev('document.title') === 'SELFTEST-DONE') break; }
  const sp = await ev(`document.documentElement.getAttribute('data-sparql')`) || '';
  const ok = (sp.match(/:OK/g) || []).length, fail = sp.split(' ; ').filter(x => !/:OK$/.test(x));
  console.log('SPARQL selftest', ok + '/' + sp.split(' ; ').length, fail.slice(0, 5));
  console.log('RDFS', await ev(`document.documentElement.getAttribute('data-rdfs')`));
  console.log('DL', (await ev(`document.documentElement.getAttribute('data-dl')`) || '').slice(0, 300));

  // 2) "Mở trong Playground" cho mọi truy vấn trên các trang dạng
  await send('Page.navigate', {url: BASE + '#D8'}); await sleep(3000);
  const pages = ['D8', 'D9', 'TRA', 'LUYEN1', 'LUYEN2', 'LUYEN3', 'D10', 'D11'];
  let tot = 0, rows = 0, zero = 0, note = 0, err = [];
  for (const pid of pages) {
    await ev(`location.hash='${pid}'`); await sleep(1200);
    const n = await ev(`document.querySelectorAll('#p-${pid} .codebar button').length`);
    const btns = await ev(`[...document.querySelectorAll('#p-${pid} .codebar button')].map((b,i)=>/Playground/.test(b.textContent)?i:-1).filter(i=>i>=0)`);
    for (const bi of btns) {
      tot++;
      await ev(`location.hash='${pid}'`); await sleep(300);
      await ev(`document.querySelectorAll('#p-${pid} .codebar button')[${bi}].click()`); await sleep(500);
      const task = await ev(`document.querySelector('#p-PLAY .ex-task').textContent`);
      if (/minh hoạ/.test(task)) { note++; continue; }
      await ev(`document.querySelector('#p-PLAY [data-a=run]').click()`);
      let r = '';
      for (let k = 0; k < 60; k++) { await sleep(150); r = await ev(`document.querySelector('#p-PLAY .result').textContent`); if (r) break; }
      if (/⚠/.test(r)) err.push(pid + '#' + bi + ': ' + r.slice(0, 140));
      else if (/0 kết quả/.test(r)) zero++; else rows++;
    }
  }
  console.log('PLAYGROUND buttons', {tot, rows, zero, note, err: err.length});
  err.slice(0, 12).forEach(e => console.log('  ', e));

  // 3) neo từ trang Đề cũ
  await ev(`location.hash='DECU'`); await sleep(1000);
  await ev(`document.querySelector('#p-DECU a[href*="/q-2022-1-c3"]').click()`); await sleep(1200);
  console.log('ANCHOR', await ev(`location.hash + ' visible=' + !document.getElementById('p-D6').hidden + ' top=' + Math.round(document.getElementById('q-2022-1-c3').getBoundingClientRect().top)`));

  // 4) Kiểm tra mệnh đề có blank node (D4)
  await ev(`location.hash='D4'`); await sleep(1500);
  await ev(`(()=>{const w=document.querySelector('#p-D4 .widget'); const s=w.querySelector('.pre'); s.value=s.options[1].value; s.dispatchEvent(new Event('change'));})()`);
  for (const stmt of [':Ann :hasParent [ a :Person ]', ':Carl a :Parent', ':Ann a :Child .', ':Ann :hasParent']) {
    await ev(`(()=>{const w=document.querySelector('#p-D4 .widget'); w.querySelector('.ask').value=${JSON.stringify(stmt)}; w.querySelector('[data-a=ask]').click();})()`); await sleep(300);
    console.log('ASK', stmt, '=>', (await ev(`document.querySelector('#p-D4 .widget .askout').textContent`)).slice(0, 110));
  }
  // 5) Back sau khi mở trang đầu
  await send('Page.navigate', {url: BASE}); await sleep(2500);
  await ev(`location.hash='D5'`); await sleep(600); await ev('history.back()'); await sleep(800);
  console.log('BACK', await ev('location.hash'));
  console.log('EXC', logs.length ? logs : 'none');
  ws.close(); p.kill(); process.exit(0);
})().catch(e => { console.log('ERR', e); p.kill(); process.exit(1); });
