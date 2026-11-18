with open('templates/moduloTransaccional/venta_form.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of venta_form.html:', len(text))
for line in text.split('\n'):
    if any(k in line.lower() for k in ['porcentaje', 'descuento', 'recalcul', 'script']):
        print(line.strip()[:140])
