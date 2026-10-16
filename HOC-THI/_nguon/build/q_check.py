import re, json
h = open(r'C:\Users\hieunt15\SemanticWeb_OnTap\HOC-THI\index.html', encoding='utf-8').read()
m = re.search(r'window\.SW_QUIZ=(\[.*?\]);\n', h, re.S)
q = json.loads(m.group(1).replace('<\/', '</'))
from collections import Counter
print(Counter(x['a'] for x in q))
print('Dich' , '*Dịch:*' in h or 'Dịch:' in h, '| xem A7', 'xem A7' in h)
