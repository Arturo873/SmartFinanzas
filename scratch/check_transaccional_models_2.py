with open('moduloTransaccional/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for l in lines[65:190]:
    print(l)
