with open('moduloTransaccional/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'def ' in l or 'class ' in l:
        print(f'{i+1}: {l}')
