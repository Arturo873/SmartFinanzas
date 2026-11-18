with open('templates/moduloETL/ratios_financieros.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of ratios_financieros.html:', len(text))
for line in text.split('\n'):
    if any(k in line.lower() for k in ['no utilizado', 'prueba ácida', 'razón de caja', 'cobertura', 'altman', 'z\'\'em', 'v1', 'v7', 'volatilidad']):
        print(line.strip()[:140])
