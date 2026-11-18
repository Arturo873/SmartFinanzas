with open('templates/usuarios/login.html', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for l in lines:
    if 'button' in l or 'input' in l or 'form' in l:
        print(l.strip()[:100])
