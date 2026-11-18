with open('moduloTransaccional/forms.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of moduloTransaccional/forms.py:', len(text))
for line in text.split('\n'):
    if 'class ' in line or 'def ' in line:
        print(line)
