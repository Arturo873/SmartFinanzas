with open('moduloETL/services.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of services.py:', len(text))
for line in text.split('\n'):
    if 'def ' in line or 'class ' in line or 'volatilidad' in line.lower() or 'cierre' in line.lower():
        print(line[:120])
