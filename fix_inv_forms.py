import re

filepath = '/home/arturo/Documentos/Repositorios/SmartFinanzas/erp/inventario/forms.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace manejo_vencimiento
content = re.sub(r'    manejo_vencimiento = forms\.BooleanField\(required=False, label="Perecible \(vencimiento\)"\)\n', '', content)

# Remove fecha_vencimiento definition
content = re.sub(r'    fecha_vencimiento = forms\.DateField\([\s\S]*?    \)\n\n', '', content)

# Remove fecha_vencimiento from Meta fields
content = content.replace('            "manejo_vencimiento",\n', '')
content = content.replace('            "fecha_vencimiento",\n', '')

# Remove clean_fecha_vencimiento method
content = re.sub(r'    def clean_fecha_vencimiento\(self\):[\s\S]*?return fecha\n\n', '', content)

# Remove manejo_vencimiento and fecha_vencimiento variables in clean()
content = content.replace('        manejo_vencimiento = cleaned_data.get("manejo_vencimiento")\n', '')
content = content.replace('        fecha_vencimiento = cleaned_data.get("fecha_vencimiento")\n', '')

# Remove validation block in clean()
content = re.sub(r'        # Si manejo VENCIMIENTO está activo y no hay fecha, error \(refuerzo\)[\s\S]*?\)\n', '', content)

with open(filepath, 'w') as f:
    f.write(content)
