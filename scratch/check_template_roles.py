with open('templates/Principal.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'\{%\s*if[^\n]*role[^\n]*%\}', text)
print('Role if matches:', matches)
matches_all_if = re.findall(r'\{%\s*if[^\n]*%\}', text)
for m in matches_all_if:
    if 'user' in m or 'perm' in m:
        print(m)
