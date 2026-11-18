with open('templates/moduloETL/carga_datos.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
ths = re.findall(r'<th[^>]*>(.*?)</th>', text, re.I)
for th in ths:
    print(th.strip()[:100])
