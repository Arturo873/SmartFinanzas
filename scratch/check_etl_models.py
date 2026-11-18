with open('moduloETL/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of moduloETL/models.py:', len(text))
for line in text.split('\n'):
    if 'models.' in line:
        print(line.strip())
