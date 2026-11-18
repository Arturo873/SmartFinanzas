with open('moduloETL/tests.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of moduloETL/tests.py:', len(text))
for line in text.split('\n'):
    if 'def ' in line or 'class ' in line:
        print(line)
