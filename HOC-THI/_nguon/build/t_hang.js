const fs=require('fs'); eval(fs.readFileSync(__dirname+'/rdf.js','utf8')+';global.RDF=RDF;');
for (const src of [':a :p <http://x .', '"x"^^<http://x', ':a :p "x"@ .', ':a :p "abc', ':a :p :b', ':a :p :b .\n:c :q', '@prefix : <http://e/> .\n:a :p "x"^^xsd:date ; :q 10.5 , ( :x :y ) ; :r [ :s "t"@en ] .', 'Ann knows Bob .']) {
  try { const r=RDF.parse(src); console.log('OK', r.triples.length); } catch(e) { console.log('ERR', e.message); }
}
