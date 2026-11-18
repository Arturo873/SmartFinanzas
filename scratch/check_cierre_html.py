with open('templates/moduloTransaccional/cierre_caja_form.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of cierre_caja_form.html:', len(text))
for line in text.split('\n'):
    if any(k in line.lower() for k in ['retiro', 'caja chica', 'petty']):
        print(line.strip()[:140])
