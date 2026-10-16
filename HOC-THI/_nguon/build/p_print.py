from pathlib import Path
H = Path(__file__).parent
p = H / "build.py"; s = p.read_text(encoding="utf-8")
def rep(a, b, n=1):
    global s
    assert a in s, a[:60]; s = s.replace(a, b, n)
rep("    if(i>=list.length){document.title='READY';window.__ready=true;return;}",
    "    if(i>=list.length){mm();return;}")
rep("  if(window.vis) next(); else {document.title='READY';}",
    """  function done(){document.title='READY';window.__ready=true;}
  function mm(){
    var codes=[].slice.call(document.querySelectorAll('pre > code.language-mermaid'));
    if(!window.mermaid||!codes.length){done();return;}
    mermaid.initialize({startOnLoad:false,theme:'neutral',securityLevel:'loose',flowchart:{htmlLabels:false,useMaxWidth:true}});
    var k=0;
    (function one(){
      if(k>=codes.length){done();return;}
      var c=codes[k++], pre=c.parentNode;
      mermaid.render('pm'+k, c.textContent).then(function(r){var fig=document.createElement('div'); fig.className='gfig mmfig'; fig.innerHTML=r.svg; pre.parentNode.replaceChild(fig, pre); one();}).catch(function(){one();});
    })();
  }
  if(window.vis) next(); else mm();""")
rep('<script src="lib/vis-network.min.js"></script><script>{read(HERE / "rdf.js")}</script><script>{PRINT_JS}</script></body></html>"""\n    (OUT / "in-thi.html")',
    '<script src="lib/vis-network.min.js"></script><script src="lib/mermaid.min.js"></script><script>{read(HERE / "rdf.js")}</script><script>{PRINT_JS}</script></body></html>"""\n    (OUT / "in-thi.html")')
rep('<div class="cols">{bw(render(rest))}</div>\n<script src="lib/vis-network.min.js"></script>',
    '<div class="cols">{bw(render(rest))}</div>\n<script src="lib/vis-network.min.js"></script><script src="lib/mermaid.min.js"></script>')
rep(".gfig{text-align:center;margin:2pt 0;break-inside:avoid}.gfig svg{max-height:62mm;max-width:100%}",
    ".gfig{text-align:center;margin:2pt 0;break-inside:avoid}.gfig svg{max-height:62mm;max-width:100%}.mmfig svg{filter:grayscale(1)}")
p.write_text(s, encoding="utf-8")
c = H / "print.css"; t = c.read_text(encoding="utf-8")
t += "\n.mmfig{text-align:center;break-inside:avoid;margin:4pt 0}.mmfig svg{max-width:100%;height:auto;filter:grayscale(1)}\n"
c.write_text(t, encoding="utf-8")
print("ok")
