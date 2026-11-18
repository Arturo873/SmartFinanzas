with open('moduloTransaccional/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'class CierreCajaCreateView' in l:
        for j in range(i, min(i+120, len(lines))):
            print(lines[j])
        break
