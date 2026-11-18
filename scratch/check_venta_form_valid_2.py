with open('moduloTransaccional/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for l in lines[255:370]:
    print(l)
