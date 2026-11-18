with open('moduloTransaccional/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if any(k in l.lower() for k in ['petty', 'retiro', 'caja chica']):
        print(f'{i+1}: {l.strip()[:120]}')
