with open('templates/moduloETL/carga_datos.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of carga_datos.html:', len(text))
for line in text.split('\n'):
    if any(k in line.lower() for k in ['no utilizado', 'prueba ácida', 'razón de caja', 'cobertura', 'altman', 'z\'\'em', 'referencia']):
        print(line.strip()[:140])
