with open('moduloTransaccional/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, l in enumerate(lines):
    if 'def form_valid' in l and i < 300:
        for j in range(i, min(i+80, len(lines))):
            print(lines[j])
        break
