import os
import re

TEMPLATE_DIR = '/home/arturo/Documentos/Repositorios/SmartFinanzas/erp/templates/erp/mantenedores/productos'

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace perishable and control_por_* with hs_code and landed_cost
    old_block = """                        <div class="col-md-4 mb-3 mt-2">
                            {{ form.perishable }} {{ form.perishable.label_tag }}
                        </div>

                        <div class="col-md-4 mb-3 mt-2">
                            {{ form.control_por_lote }} {{ form.control_por_lote.label_tag }}
                        </div>

                        <div class="col-md-4 mb-3 mt-2">
                            {{ form.control_por_serie }} {{ form.control_por_serie.label_tag }}
                        </div>"""

    new_block = """                        <div class="col-md-4 mb-3">
                            {{ form.hs_code.label_tag }} {{ form.hs_code }}
                        </div>

                        <div class="col-md-4 mb-3">
                            {{ form.landed_cost.label_tag }} {{ form.landed_cost }}
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
