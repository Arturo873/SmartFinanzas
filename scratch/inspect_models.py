import os
for app in ['moduloTransaccional', 'moduloETL', 'capaAnalitica', 'usuarios', 'AppWeb']:
    p = os.path.join(app, 'models.py')
    if os.path.exists(p):
        print('='*50)
        print(p)
        print('='*50)
        with open(p, 'r', encoding='utf-8') as f:
            for line in f:
                if 'class ' in line or 'ForeignKey(' in line or 'DateTimeField(' in line or 'created' in line.lower() or 'user' in line.lower() or 'usuario' in line.lower():
                    print(line.strip())
