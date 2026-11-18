with open('templates/Principal.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('class="sidebar"')
if idx != -1:
    print(text[idx:idx+3500])
else:
    print("sidebar not found")
