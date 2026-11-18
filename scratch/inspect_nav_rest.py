with open('templates/Principal.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('class="sidebar"')
if idx != -1:
    print(text[idx+2000:idx+5500])
