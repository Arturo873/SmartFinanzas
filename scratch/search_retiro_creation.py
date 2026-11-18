import os
found = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('venv', '.git', '__pycache__')]
    for f in files:
        if f.endswith(('.py', '.html')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                c = fp.read()
                if 'PettyCashWithdrawal.objects.create' in c or 'PettyCashWithdrawal(' in c or 'retiro_crear' in c or 'RetiroCajaChica' in c:
                    found.append((p, [line.strip() for line in c.split('\n') if 'PettyCashWithdrawal' in line or 'Retiro' in line]))

for f, lines in found:
    print(f)
    for l in lines[:5]:
        print('  ', l[:120])
