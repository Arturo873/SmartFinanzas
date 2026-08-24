import os
import re

TEMPLATE_DIR = '/home/arturo/Documentos/Repositorios/SmartFinanzas/erp/templates/erp/mantenedores/proveedores'

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the block for moneda and append incoterm_defecto
    old_block = """            <div class="col-md-3 mb-3">
                {{ form.moneda.label_tag }}
                {{ form.moneda }}
                {% for error in form.moneda.errors %}
                    <p class="text-warning small fw-bold">{{ error }}</p>
                {% endfor %}
            </div>"""

    new_block = """            <div class="col-md-3 mb-3">
                {{ form.moneda.label_tag }}
                {{ form.moneda }}
                {% for error in form.moneda.errors %}
                    <p class="text-warning small fw-bold">{{ error }}</p>
                {% endfor %}
            </div>

            <div class="col-md-3 mb-3">
                {{ form.incoterm_defecto.label_tag }}
                {{ form.incoterm_defecto }}
                {% for error in form.incoterm_defecto.errors %}
                    <p class="text-warning small fw-bold">{{ error }}</p>
                {% endfor %}
            </div>"""

    new_content = content.replace(old_block, new_block)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

for root, dirs, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            fix_file(os.path.join(root, file))

print("Templates fixed.")
