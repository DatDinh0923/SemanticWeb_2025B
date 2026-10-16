const fs = require('fs'); eval(fs.readFileSync(__dirname + '/rdf.js', 'utf8') + ';global.RDF=RDF;');
const src = '@prefix : <http://e/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n:a :p "2024-01-01"^^xsd:date , "x\\"y\\\\z" , 10 , 10.5 , true , "Hi"@en-US , :b , "dòng1\\ndòng2" .';
const r = RDF.parse(src);
const out = r.triples.map(t => RDF.ttlTerm(t.o, r.prefixes));
console.log(out.join(' | '));
// khứ hồi: Turtle sinh lại phải parse ra đúng các giá trị
const back = RDF.parse('@prefix : <http://e/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n:a :p ' + out.join(' , ') + ' .');
console.log(JSON.stringify(back.triples.map(t => t.o)) === JSON.stringify(r.triples.map(t => t.o)) ? 'ROUNDTRIP OK' : 'ROUNDTRIP FAIL');
