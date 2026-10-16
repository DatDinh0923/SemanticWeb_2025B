const fs=require('fs'); eval(fs.readFileSync(__dirname+'/rdf.js','utf8')+';global.RDF=RDF;');
const files=process.argv.slice(2); let ok=0,bad=0;
for(const f of files){ const t=fs.readFileSync(f,'utf8'); const re=/```turtle( graph)?\s*\n([\s\S]*?)```/g; let m;
 while((m=re.exec(t))){ try{ const r=RDF.parse(m[2]); ok++; }catch(e){ bad++; if(m[1]||process.env.ALL) console.log((m[1]?'GRAPH ':'')+f.split(/[\/]/).pop()+': '+e.message+' :: '+m[2].slice(0,80).replace(/\n/g,' ')); } } }
console.log('ok',ok,'bad',bad);
