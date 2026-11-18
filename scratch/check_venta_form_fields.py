with open('moduloTransaccional/forms.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'class VentaForm' in l:
        for j in range(i, min(i+70, len(lines))):
            print(lines[j])
        break
