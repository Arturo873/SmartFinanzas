"""
Generador de la Guía Oficial de Instalación, Configuración y Despliegue Local de SmartFinanzas (.docx).
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

HEX_NAVY = "1E3A8A"       # Azul Marino Principal
HEX_BLUE = "2563EB"       # Azul Acento
HEX_SLATE = "1E293B"      # Texto Oscuro
HEX_MUTED = "64748B"      # Texto Secundario
HEX_LIGHT_BG = "F8FAFC"   # Fondo Tablas
HEX_CODE_BG = "F1F5F9"    # Fondo Cajas de Código
HEX_CALLOUT_INFO = "EFF6FF"# Fondo Callout Info
HEX_CALLOUT_WARN = "FEF3C7"# Fondo Callout Warning
HEX_CALLOUT_SUCC = "F0FDF4"# Fondo Callout Exito
HEX_BORDER = "CBD5E1"     # Borde sutil
HEX_GREEN = "16A34A"      # Verde
HEX_AMBER = "D97706"      # Ámbar
HEX_RED = "DC2626"        # Rojo

COLOR_NAVY = RGBColor(30, 58, 138)
COLOR_BLUE = RGBColor(37, 99, 235)
COLOR_SLATE = RGBColor(30, 41, 59)
COLOR_MUTED = RGBColor(100, 116, 139)
COLOR_GREEN = RGBColor(22, 163, 74)
COLOR_AMBER = RGBColor(217, 119, 6)
COLOR_RED = RGBColor(220, 38, 38)
COLOR_CODE = RGBColor(15, 23, 42)

def set_cell_background(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    cell._tc.get_or_add_tcPr().append(tcMar)

def set_table_borders(table, border_color=HEX_BORDER):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_NAVY}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
        </w:tcBorders>
    ''')
    cell._tc.get_or_add_tcPr().append(tcBorders)
    
    lines = code_text.strip().split('\n')
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(9.0)
        run.font.color.rgb = COLOR_CODE
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def add_callout(doc, text, title="NOTA INFORMATIVA", kind="info"):
    colors = {
        "info": (HEX_CALLOUT_INFO, HEX_BLUE, COLOR_BLUE),
        "warn": (HEX_CALLOUT_WARN, HEX_AMBER, COLOR_AMBER),
        "succ": (HEX_CALLOUT_SUCC, HEX_GREEN, COLOR_GREEN),
        "danger": ("FEF2F2", HEX_RED, COLOR_RED),
    }
    bg_hex, border_hex, title_col = colors.get(kind, colors["info"])
    
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=130, bottom=130, left=180, right=180)
    
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="36" w:space="0" w:color="{border_hex}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    cell._tc.get_or_add_tcPr().append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"[{title}]")
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.name = "Calibri"
    run_t.font.color.rgb = title_col
    
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.15
    run_body = p2.add_run(text)
    run_body.font.size = Pt(10)
    run_body.font.name = "Calibri"
    run_body.font.color.rgb = COLOR_SLATE
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def add_heading_styled(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Calibri"
    if level == 1:
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(16)
        run.bold = True
        run.font.color.rgb = COLOR_NAVY
    elif level == 2:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(13)
        run.bold = True
        run.font.color.rgb = COLOR_BLUE
    elif level == 3:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
        run.font.size = Pt(11)
        run.bold = True
        run.font.color.rgb = COLOR_SLATE
    return h

def add_paragraph_styled(doc, text, bold_prefix="", space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = COLOR_SLATE
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10.5)
    r_text.font.color.rgb = COLOR_SLATE
    return p

def add_bullet_styled(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10)
        r_pre.font.color.rgb = COLOR_SLATE
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = COLOR_SLATE
    return p

def add_screenshot_figure(doc, img_rel_path, fig_num, caption_text, width=Inches(6.0)):
    full_path = os.path.abspath(img_rel_path)
    if not os.path.exists(full_path):
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(10)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    
    run_img = p_img.add_run()
    run_img.add_picture(full_path, width=width)
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(12)
    p_cap.paragraph_format.keep_with_next = False
    
    r_num = p_cap.add_run(f"Figura {fig_num}: ")
    r_num.bold = True
    r_num.font.name = "Calibri"
    r_num.font.size = Pt(9.5)
    r_num.font.color.rgb = COLOR_NAVY
    
    r_cap = p_cap.add_run(caption_text)
    r_cap.italic = True
    r_cap.font.name = "Calibri"
    r_cap.font.size = Pt(9.5)
    r_cap.font.color.rgb = COLOR_MUTED

def style_table_header(table, col_widths, headers):
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        cell = hdr_cells[i]
        cell.width = col_widths[i]
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

def add_table_row(table, col_widths, data, is_even=False):
    row_cells = table.add_row().cells
    bg = HEX_LIGHT_BG if is_even else "FFFFFF"
    for i, val in enumerate(data):
        cell = row_cells[i]
        cell.width = col_widths[i]
        set_cell_background(cell, bg)
        set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(str(val))
        run.font.name = "Calibri"
        run.font.size = Pt(9)
        run.font.color.rgb = COLOR_SLATE

def build_deployment_guide():
    print("Iniciando la construcción de la Guía de Despliegue Local...")
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("SmartFinanzas | Guía Técnica de Despliegue Local | v1.0")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # PORTADA CORPORATIVA
    # -------------------------------------------------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("MANUAL DE DESPLIEGUE TÉCNICO Y ENTORNO DE DESARROLLO")
    r_pre.font.name = "Calibri"
    r_pre.font.size = Pt(12)
    r_pre.font.bold = True
    r_pre.font.color.rgb = COLOR_BLUE

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("SMARTFINANZAS")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(30)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(28)
    r_sub = p_sub.add_run("Guía Paso a Paso para la Instalación, Configuración de Base de Datos y Ejecución en Local")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13.5)
    r_sub.font.color.rgb = COLOR_SLATE

    tbl_meta = doc.add_table(rows=1, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    col_w = [Inches(2.3), Inches(4.2)]
    
    style_table_header(tbl_meta, col_w, ["Parámetro Técnico", "Especificación del Entorno"])
    meta_rows = [
        ("Framework Base:", "Django 4.2 LTS (Python Web Framework)"),
        ("Versión de Python:", "Python 3.10 / 3.11 / 3.12 (Recomendado 3.11+)"),
        ("Motor de Base de Datos:", "MySQL 8.0+ / MariaDB 10.4+ (Soporte nativo XAMPP)"),
        ("Bibliotecas Analíticas:", "Scikit-Learn, LightGBM, SHAP, Pandas, NumPy"),
        ("Generación de Documentos:", "ReportLab, xhtml2pdf (PDF), python-docx (Word)"),
        ("Sistemas Operativos:", "Windows 10/11, Linux (Ubuntu/Debian), macOS"),
        ("Tiempo Estimado de Setup:", "Aproximadamente 5 a 10 minutos"),
        ("Fecha de Publicación:", "Noviembre 2026")
    ]
    for i, row in enumerate(meta_rows):
        add_table_row(tbl_meta, col_w, row, is_even=(i%2==0))
    set_table_borders(tbl_meta)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_after = Pt(30)

    add_callout(
        doc,
        "Esta guía técnica está dirigida a desarrolladores, ingenieros de software, evaluadores y administradores de sistemas que requieran clonar, instalar dependencias, inicializar la base de datos MySQL, migrar esquemas, poblar usuarios de prueba y levantar el servidor local de desarrollo de SmartFinanzas sin fricción.",
        title="OBJETIVO DE LA GUÍA",
        kind="info"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # ÍNDICE GENERAL
    # -------------------------------------------------------------
    add_heading_styled(doc, "Índice de la Guía de Despliegue", level=1)
    
    toc_items = [
        ("Capítulo 1: Prerrequisitos del Sistema", "Herramientas de software obligatorias y versiones compatibles."),
        ("Capítulo 2: Arquitectura del Repositorio", "Estructura modular de Django: aplicaciones, modelos ML y templates."),
        ("Capítulo 3: Configuración del Entorno Virtual", "Creación, activación de venv e instalación de librerías."),
        ("Capítulo 4: Configuración de la Base de Datos", "Puesta en marcha de MySQL (XAMPP), creación de base de datos y .env."),
        ("Capítulo 5: Migraciones y Semilla de Datos (Seeding)", "Construcción de tablas, roles iniciales y creación de usuarios demo."),
        ("Capítulo 6: Artefactos de Machine Learning", "Verificación de modelos serializados (.joblib) en capaAnalitica."),
        ("Capítulo 7: Ejecución del Servidor y Verificación", "Comando runserver, acceso al navegador y batería de tests unitarios."),
        ("Capítulo 8: Solución de Problemas Frecuentes", "Resolución de errores de conexión MySQL, PowerShell y mysqlclient."),
        ("Capítulo 9: Hoja de Referencia Rápida (Cheat Sheet)", "Secuencia comprimida de comandos para despliegue en 5 minutos.")
    ]
    
    tbl_toc = doc.add_table(rows=1, cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_toc = [Inches(2.5), Inches(4.0)]
    style_table_header(tbl_toc, col_w_toc, ["Capítulo", "Resumen de Contenido"])
    for i, item in enumerate(toc_items):
        add_table_row(tbl_toc, col_w_toc, item, is_even=(i%2==0))
    set_table_borders(tbl_toc)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 1: PRERREQUISITOS DEL SISTEMA
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 1: Prerrequisitos del Sistema", level=1)
    
    add_paragraph_styled(
        doc,
        "Antes de comenzar la instalación de SmartFinanzas en su máquina local, asegúrese de contar con el siguiente software instalado y accesible en su PATH:"
    )

    tbl_reqs = doc.add_table(rows=1, cols=4)
    tbl_reqs.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_r = [Inches(1.5), Inches(1.4), Inches(2.2), Inches(1.4)]
    style_table_header(tbl_reqs, col_w_r, ["Software", "Versión Requerida", "Propósito en el Sistema", "Verificación en Terminal"])
    
    reqs_data = [
        ("Python", "3.10 a 3.12 (64-bit)", "Entorno de ejecución del framework y ML", "python --version"),
        ("Git", "2.30 o superior", "Clonación y sincronización de código fuente", "git --version"),
        ("MySQL / MariaDB", "MySQL 8.0+ / MariaDB 10.4+", "Base de datos relacional (vía XAMPP o nativo)", "mysql --version"),
        ("XAMPP (Opcional)", "XAMPP 8.1+ con MySQL", "Gestión simplificada del servicio de base de datos", "Panel XAMPP Control"),
        ("Navegador Web", "Chrome / Edge / Firefox", "Visualización de la aplicación y dashboards", "Instalado en OS")
    ]
    for i, r in enumerate(reqs_data):
        add_table_row(tbl_reqs, col_w_r, r, is_even=(i%2==0))
    set_table_borders(tbl_reqs)

    add_callout(
        doc,
        "RECOMENDACIÓN PARA WINDOWS: Si utiliza XAMPP para gestionar MySQL, asegúrese de que el servicio 'MySQL' esté iniciado en el panel de control verde y escuchando en el puerto estándar 3306. No es obligatorio iniciar Apache si sólo utilizará Django como servidor web.",
        title="CONSEJO DE ENTORNO LOCAL",
        kind="info"
    )

    # -------------------------------------------------------------
    # CAPÍTULO 2: ARQUITECTURA DEL REPOSITORIO
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 2: Arquitectura del Repositorio", level=1)
    
    add_paragraph_styled(
        doc,
        "El código fuente de SmartFinanzas está estructurado como un proyecto modular de Django, donde cada área de negocio reside en una aplicación independiente:"
    )

    add_bullet_styled(doc, "Directorio raíz de configuración central de Django. Contiene settings.py (variables, base de datos y middlewares), urls.py (enrutamiento general) y wsgi.py.", "SmartFinanzas/: ")
    add_bullet_styled(doc, "Gestión de identidad corporativa. Contiene el modelo de usuario personalizado (User), modelo de empresas (Company), roles (Role) y la lógica de inicio de sesión y sincronización RBAC.", "usuarios/: ")
    add_bullet_styled(doc, "Módulo de caja y ventas. Contiene la lógica del Punto de Venta (POS), clientes, productos, comisiones de adquirencia con tarjeta, retiros y el formulario de arqueo de gaveta.", "moduloTransaccional/: ")
    add_bullet_styled(doc, "Tubería de extracción, transformación y carga contable. Procesa balances en Excel/CSV, genera plantillas IFRS, calcula la matriz de los 7 ratios financieros (V1 a V7) y audita valores atípicos (outliers).", "moduloETL/: ")
    add_bullet_styled(doc, "Núcleo de inteligencia predictiva. Alberga los modelos serializados de Machine Learning (.joblib), el algoritmo de explicabilidad SHAP y el catálogo de recomendaciones financieras prescriptivas.", "capaAnalitica/: ")
    add_bullet_styled(doc, "Capa de presentación ejecutiva para la alta gerencia. Consolida tacómetros del Semáforo de Riesgo, gráficos temporales de evolución del Score y la exportación del informe PDF.", "dashboard/: ")
    add_bullet_styled(doc, "Plantillas HTML comunes, vistas base y modelos de apoyo de perfil de usuario.", "AppWeb/ y templates/: ")
    add_bullet_styled(doc, "Archivos estáticos (hojas de estilo CSS, scripts interactivos JavaScript e imágenes del sistema).", "static/: ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 3: CONFIGURACIÓN DEL ENTORNO VIRTUAL
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 3: Configuración del Entorno Virtual de Python", level=1)
    
    add_paragraph_styled(
        doc,
        "Es una buena práctica de ingeniería de software aislar las dependencias del proyecto dentro de un entorno virtual (virtualenv) para evitar colisiones con librerías globales del sistema operativo."
    )

    add_heading_styled(doc, "3.1 Clonar el Proyecto y Ubicarse en el Directorio", level=2)
    add_paragraph_styled(doc, "Abra su terminal (PowerShell en Windows o Bash en Linux/macOS) y ejecute:")
    add_code_block(
        doc,
        "# Clonar el repositorio desde GitHub / GitLab\n"
        "git clone https://github.com/usuario/SmartFinanzas.git\n\n"
        "# Ingresar a la carpeta principal del proyecto\n"
        "cd SmartFinanzas"
    )

    add_heading_styled(doc, "3.2 Creación del Entorno Virtual (venv)", level=2)
    add_paragraph_styled(doc, "Cree el entorno virtual ejecutando el módulo 'venv' de Python:")
    add_code_block(
        doc,
        "# Crear la carpeta venv aislada\n"
        "python -m venv venv"
    )

    add_heading_styled(doc, "3.3 Activación del Entorno Virtual", level=2)
    add_paragraph_styled(doc, "Active el entorno según el sistema operativo y la consola que esté utilizando:")
    add_code_block(
        doc,
        "# En Windows (PowerShell):\n"
        ".\\venv\\Scripts\\Activate.ps1\n\n"
        "# Si PowerShell muestra error de permisos de script, ejecute antes:\n"
        "# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass\n\n"
        "# En Windows (Símbolo del Sistema / CMD):\n"
        ".\\venv\\Scripts\\activate.bat\n\n"
        "# En Linux o macOS (Bash / Zsh):\n"
        "source venv/bin/activate"
    )
    add_paragraph_styled(doc, "Al activarse correctamente, el prefijo '(venv)' aparecerá al inicio de la línea de comandos.")

    add_heading_styled(doc, "3.4 Instalación de Dependencias", level=2)
    add_paragraph_styled(
        doc,
        "Actualice el gestor 'pip' a su última versión e instale las librerías necesarias especificadas en requirements.txt:"
    )
    add_code_block(
        doc,
        "# 1. Actualizar pip a la versión más reciente\n"
        "python -m pip install --upgrade pip\n\n"
        "# 2. Instalar el conjunto completo de dependencias\n"
        "pip install -r requirements.txt"
    )

    add_paragraph_styled(
        doc,
        "El archivo requirements.txt instalará de forma automática:",
        bold_prefix="Paquetes Principales: "
    )
    add_bullet_styled(doc, "Framework web robusto para el backend y ORM.", "Django (>=4.2,<4.3): ")
    add_bullet_styled(doc, "Manipulación de datos tabulares y lectura de balances en planillas Excel.", "pandas, numpy, openpyxl: ")
    add_bullet_styled(doc, "Carga de pipelines de Machine Learning e inferencia del Score de insolvencia.", "scikit-learn, joblib, imbalanced-learn: ")
    add_bullet_styled(doc, "Cálculo de explicabilidad matemática y valores Shapley para el Top 3.", "shap: ")
    add_bullet_styled(doc, "Motor de renderizado de reportes ejecutivos en PDF descargables.", "reportlab, xhtml2pdf: ")
    add_bullet_styled(doc, "Driver de alta velocidad para conectar Django con MySQL/MariaDB y lector de variables .env.", "mysqlclient, python-dotenv: ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 4: CONFIGURACIÓN DE LA BASE DE DATOS
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 4: Configuración de la Base de Datos (MySQL / XAMPP)", level=1)
    
    add_heading_styled(doc, "4.1 Iniciar el Servicio de MySQL", level=2)
    add_paragraph_styled(
        doc,
        "SmartFinanzas requiere una base de datos MySQL o MariaDB activa. Si utiliza XAMPP, abra el 'XAMPP Control Panel' y haga clic en 'Start' en la fila correspondiente a 'MySQL'. Alternativamente, puede iniciarlo desde la consola de Windows:"
    )
    add_code_block(
        doc,
        "# Iniciar mysqld en modo standalone (si XAMPP está instalado en C:\\xampp)\n"
        "C:\\xampp\\mysql\\bin\\mysqld.exe --defaults-file=C:\\xampp\\mysql\\bin\\my.ini --standalone"
    )

    add_heading_styled(doc, "4.2 Crear la Base de Datos en MySQL", level=2)
    add_paragraph_styled(
        doc,
        "Ingrese a phpMyAdmin (http://localhost/phpmyadmin) o acceda al cliente de consola de MySQL para crear la base de datos con codificación utf8mb4:"
    )
    add_code_block(
        doc,
        "-- Conectarse al cliente MySQL (como usuario root sin contraseña en XAMPP):\n"
        "mysql -u root\n\n"
        "-- Crear la base de datos del proyecto con soporte completo de caracteres y emojis:\n"
        "CREATE DATABASE smartfinanzasingles2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n\n"
        "-- Verificar que la base de datos fue creada:\n"
        "SHOW DATABASES;\n\n"
        "EXIT;"
    )

    add_heading_styled(doc, "4.3 Configuración del Archivo de Entorno (.env)", level=2)
    add_paragraph_styled(
        doc,
        "En la raíz del proyecto existe una plantilla llamada '.env.example'. Debe crear una copia denominada '.env' y ajustar las credenciales de conexión:"
    )
    add_code_block(
        doc,
        "# En Windows (PowerShell):\n"
        "Copy-Item .env.example .env\n\n"
        "# En Linux / macOS:\n"
        "cp .env.example .env"
    )
    add_paragraph_styled(doc, "Abra el archivo '.env' y verifique que contenga los siguientes valores para desarrollo local:")
    add_code_block(
        doc,
        "# Archivo .env para Entorno Local de Desarrollo\n"
        "DEBUG=True\n"
        "SECRET_KEY=django-insecure-tx!@obs@8uu=6h(uftth-8%=$7v4_xlu5pvq6(qv)kjj4uscv$\n\n"
        "# Parámetros de Conexión a Base de Datos\n"
        "DB_ENGINE=django.db.backends.mysql\n"
        "DB_NAME=smartfinanzasingles2\n"
        "DB_USER=root\n"
        "DB_PASSWORD=\n"
        "DB_HOST=127.0.0.1\n"
        "DB_PORT=3306"
    )

    add_callout(
        doc,
        "IMPORTANTE: En XAMPP, el usuario por defecto es 'root' y la contraseña viene vacía (''). Si su instalación de MySQL cuenta con una contraseña personalizada, ingrésela en el parámetro DB_PASSWORD=su_clave.",
        title="CREDENCIALES DE MYSQL",
        kind="warn"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 5: MIGRACIONES Y SEMILLA DE DATOS (SEEDING)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 5: Migraciones y Poblado Inicial de Datos (Data Seeding)", level=1)
    
    add_heading_styled(doc, "5.1 Aplicación de Migraciones de Base de Datos", level=2)
    add_paragraph_styled(
        doc,
        "Django creará automáticamente todas las tablas relacionales del sistema (usuarios, empresas, roles, transacciones, ratios y predicciones) al ejecutar el comando de migración:"
    )
    add_code_block(
        doc,
        "# Ejecutar las migraciones en la base de datos configurada\n"
        "python manage.py migrate"
    )
    add_paragraph_styled(doc, "Observará cómo la terminal procesa secuencialmente las migraciones de todas las aplicaciones (usuarios, moduloTransaccional, moduloETL, capaAnalitica, dashboard, etc.) hasta mostrar el estado [OK].")

    add_heading_styled(doc, "5.2 Creación de Roles y Usuarios de Prueba (Data Seeding)", level=2)
    add_paragraph_styled(
        doc,
        "Para comenzar a operar el sistema de inmediato sin tener que registrar empresas manualmente, puede inicializar los datos maestros y los 4 roles principales mediante el siguiente script de semilla en Python:"
    )
    add_code_block(
        doc,
        "# Iniciar la consola interactiva de Django o ejecutar el script de seed:\n"
        "python manage.py shell\n\n"
        "# Dentro de la consola shell, pegue el siguiente bloque de código:\n"
        "from usuarios.models import Role, Company, User\n"
        "from django.contrib.auth.models import User as AuthUser\n"
        "from AppWeb.models import UserProfile\n\n"
        "# 1. Crear los 4 roles del sistema\n"
        "for r_name in ['Trabajador', 'Dueño', 'Contador', 'Administrador']:\n"
        "    Role.objects.get_or_create(name=r_name)\n\n"
        "# 2. Crear Empresa de Prueba (COAGRA S.A.)\n"
        "empresa, _ = Company.objects.get_or_create(\n"
        "    tax_id='76.999.888-K',\n"
        "    defaults={'business_name': 'COAGRA S.A.', 'business_sector': 'Agrícola / Comercial'}\n"
        ")\n\n"
        "# 3. Crear Usuarios de Prueba para cada Rol\n"
        "pass_demo = 'SmartFinanzas2026!'\n"
        "roles = {r.name: r for r in Role.objects.all()}\n"
        "demo_data = [\n"
        "    ('dueno_coagra', 'Dueño', 'dueno@coagra.cl'),\n"
        "    ('contador_coagra', 'Contador', 'contador@coagra.cl'),\n"
        "    ('trabajador_coagra', 'Trabajador', 'trabajador@coagra.cl'),\n"
        "    ('coagra', 'Administrador', 'admin@coagra.cl'),\n"
        "]\n\n"
        "for usr, rol, mail in demo_data:\n"
        "    u_db, _ = User.objects.get_or_create(\n"
        "        username=usr, defaults={'company': empresa, 'email': mail, 'role': roles[rol]}\n"
        "    )\n"
        "    u_db.set_password(pass_demo)\n"
        "    u_db.save()\n"
        "    auth_u, _ = AuthUser.objects.get_or_create(username=usr, defaults={'email': mail})\n"
        "    auth_u.set_password(pass_demo)\n"
        "    auth_u.save()\n"
        "    UserProfile.objects.update_or_create(user=auth_u, defaults={'role': rol})\n\n"
        "print('¡Usuarios demo y roles configurados con éxito!')\n"
        "exit()"
    )

    add_paragraph_styled(
        doc,
        "Tras ejecutar este paso, dispondrá de cuatro credenciales activas con la contraseña estándar 'SmartFinanzas2026!':",
        bold_prefix="Cuentas Demo Listas para Pruebas: "
    )
    add_bullet_styled(doc, "dueno@coagra.cl (Acceso total al Dashboard, Semáforo de Riesgo y Cierre de Caja).", "Dueño: ")
    add_bullet_styled(doc, "contador@coagra.cl (Acceso al Módulo ETL, carga de balances y matriz de ratios).", "Contador: ")
    add_bullet_styled(doc, "trabajador@coagra.cl (Acceso operativo al Punto de Venta - POS).", "Trabajador: ")
    add_bullet_styled(doc, "admin@coagra.cl (Acceso a administración de usuarios y configuraciones).", "Administrador: ")

    add_heading_styled(doc, "5.3 Creación de un Superusuario de Django (Opcional)", level=2)
    add_paragraph_styled(
        doc,
        "Si desea acceder al panel de administración nativo de Django (/admin/), cree un superusuario con el comando:"
    )
    add_code_block(
        doc,
        "python manage.py createsuperuser"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 6: ARTEFACTOS DE MACHINE LEARNING
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 6: Artefactos de Machine Learning y Capa Analítica", level=1)
    
    add_paragraph_styled(
        doc,
        "Uno de los mayores atractivos del proyecto SmartFinanzas es que el modelo predictivo de Gradient Boosting (LightGBM / Random Forest) ya viene pre-entrenado y serializado dentro del repositorio, ubicado en la carpeta capaAnalitica/modelo/:"
    )

    tbl_models = doc.add_table(rows=1, cols=3)
    tbl_models.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_m = [Inches(2.5), Inches(1.3), Inches(2.7)]
    style_table_header(tbl_models, col_w_m, ["Archivo Serializado", "Tamaño Aprox.", "Función en el Sistema"])
    
    models_data = [
        ("ModeloSmartfinanzas.joblib", "~5.7 MB", "Pipeline principal de inferencia predictiva y clasificación de riesgo."),
        ("modelo_riesgo_trimestral_optimizado.joblib", "~5.7 MB", "Modelo calibrado para predicción trimestral con horizonte Qt+1."),
        ("metricas_trimestral_optimizado.joblib", "< 1 KB", "Metadatos y métricas de desempeño del modelo (AUC, F1-Score, Precisión)."),
        ("catalogo_recomendaciones.py", "~48 KB", "Matriz de reglas de negocio prescriptivas vinculadas a los factores SHAP.")
    ]
    for i, m in enumerate(models_data):
        add_table_row(tbl_models, col_w_m, m, is_even=(i%2==0))
    set_table_borders(tbl_models)

    add_callout(
        doc,
        "NO SE REQUIERE RE-ENTRENAMIENTO: Al levantar el proyecto en local, la capa analítica cargará los archivos .joblib automáticamente en memoria mediante 'joblib.load()'. No es necesario disponer de datasets masivos ni GPU para ejecutar la predicción.",
        title="EFICIENCIA DE DESPLIEGUE",
        kind="succ"
    )

    # -------------------------------------------------------------
    # CAPÍTULO 7: EJECUCIÓN DEL SERVIDOR Y VERIFICACIÓN
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 7: Ejecución del Servidor y Verificación", level=1)
    
    add_heading_styled(doc, "7.1 Iniciar el Servidor de Desarrollo", level=2)
    add_paragraph_styled(doc, "Con la base de datos MySQL activa y las migraciones aplicadas, inicie el servidor de desarrollo:")
    add_code_block(
        doc,
        "# Iniciar el servidor local en el puerto estándar 8000\n"
        "python manage.py runserver 127.0.0.1:8000"
    )
    add_paragraph_styled(doc, "En su terminal se desplegará el mensaje confirmando que el servidor está escuchando peticiones:")
    add_code_block(
        doc,
        "Django version 4.2.30, using settings 'SmartFinanzas.settings'\n"
        "Starting development server at http://127.0.0.1:8000/\n"
        "Quit the server with CTRL-BREAK."
    )

    add_heading_styled(doc, "7.2 Acceso Web en el Navegador", level=2)
    add_paragraph_styled(
        doc,
        "Abra su navegador de preferencia y diríjase a la URL oficial local: http://127.0.0.1:8000/. La plataforma cargará la pantalla de inicio de sesión de SmartFinanzas."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/01_login.png",
        "7.1",
        "Pantalla de Inicio de Sesión de SmartFinanzas levantada exitosamente en entorno local (http://127.0.0.1:8000/)."
    )

    add_heading_styled(doc, "7.3 Ejecución de la Batería de Pruebas Unitarias", level=2)
    add_paragraph_styled(
        doc,
        "Para validar que todos los módulos (autenticación, cálculo de ratios, detección de anomalías y generación de reportes) funcionen con normalidad en su entorno, ejecute la suite de tests de Django:"
    )
    add_code_block(
        doc,
        "# Correr todos los tests unitarios del proyecto\n"
        "python manage.py test\n\n"
        "# O probar una aplicación específica (ejemplo: capaAnalitica o moduloETL):\n"
        "python manage.py test capaAnalitica\n"
        "python manage.py test moduloETL"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 8: SOLUCIÓN DE PROBLEMAS FRECUENTES
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 8: Solución de Problemas Frecuentes (Troubleshooting)", level=1)
    
    troubles = [
        (
            "Problema 1: Error al conectarse a MySQL: 'Can't connect to MySQL server on '127.0.0.1' (10061)'",
            "Causa: El servicio de MySQL no se encuentra en ejecución o está operando en un puerto distinto al 3306.\n"
            "Solución: Abra el panel de control de XAMPP y presione 'Start' en MySQL. Si el puerto 3306 está ocupado por otra instancia (como un servicio nativo de Windows), cambie el puerto en my.ini o ajuste el parámetro DB_PORT en su archivo .env."
        ),
        (
            "Problema 2: Error de Base de Datos Desconocida: 'Unknown database 'smartfinanzasingles2' (1049)'",
            "Causa: Django intentó conectarse a una base de datos que no ha sido creada previamente en MySQL.\n"
            "Solución: Abra phpMyAdmin o la consola MySQL y ejecute: CREATE DATABASE smartfinanzasingles2 CHARACTER SET utf8mb4; luego vuelva a correr 'python manage.py migrate'."
        ),
        (
            "Problema 3: Error de instalación de mysqlclient en Windows ('Microsoft Visual C++ 14.0 is required')",
            "Causa: En algunas versiones de Python en Windows, compilar mysqlclient desde el código fuente requiere las herramientas de compilación C++.\n"
            "Solución: Asegúrese de usar Python 3.10, 3.11 o 3.12 (64-bit) y ejecutar 'python -m pip install --upgrade pip' antes de instalar requirements.txt, lo que permitirá a pip descargar el binario precompilado (.whl). Alternativamente, puede instalar Microsoft C++ Build Tools."
        ),
        (
            "Problema 4: Error en PowerShell: 'La ejecución de scripts está deshabilitada en este sistema'",
            "Causa: Política de seguridad por defecto de Windows PowerShell (Restricted Execution Policy).\n"
            "Solución: Abra PowerShell y ejecute: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; luego vuelva a ejecutar '.\\venv\\Scripts\\Activate.ps1'."
        ),
        (
            "Problema 5: Error 403 o Redirección inesperada al navegar a /dashboard/ o /etl/carga/",
            "Causa: El usuario autenticado no posee el rol RBAC necesario (ejemplo: usuario con rol 'Trabajador' intentando ver balances contables).\n"
            "Solución: Cierre sesión navegando a /logout/ e inicie sesión con una cuenta autorizada, como dueno@coagra.cl o contador@coagra.cl."
        )
    ]

    for title, desc in troubles:
        add_paragraph_styled(doc, title, bold_prefix="", space_after=2)
        add_paragraph_styled(doc, desc, bold_prefix="", space_after=10)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 9: HOJA DE REFERENCIA RÁPIDA (CHEAT SHEET)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 9: Hoja de Referencia Rápida (Cheat Sheet)", level=1)
    
    add_paragraph_styled(
        doc,
        "Si ya cuenta con MySQL y Python instalados, puede desplegar el proyecto completo en menos de 5 minutos ejecutando la siguiente secuencia resumida de comandos en PowerShell:"
    )

    add_code_block(
        doc,
        "# ================================================================\n"
        "# GUÍA ULTRA-RÁPIDA DE DESPLIEGUE EN 5 MINUTOS (POWERSHELL)\n"
        "# ================================================================\n\n"
        "# 1. Clonar y entrar al repositorio\n"
        "cd C:\\Users\\artur\\Documents\\Repositorios\\SmartFinanzas\n\n"
        "# 2. Crear y activar el entorno virtual\n"
        "python -m venv venv\n"
        ".\\venv\\Scripts\\Activate.ps1\n\n"
        "# 3. Instalar librerías del proyecto\n"
        "python -m pip install --upgrade pip\n"
        "pip install -r requirements.txt\n\n"
        "# 4. Iniciar MySQL (XAMPP) y crear la base de datos\n"
        "mysql -u root -e \"CREATE DATABASE IF NOT EXISTS smartfinanzasingles2 CHARACTER SET utf8mb4;\"\n\n"
        "# 5. Configurar archivo .env\n"
        "if (!(Test-Path .env)) { Copy-Item .env.example .env }\n\n"
        "# 6. Ejecutar migraciones\n"
        "python manage.py migrate\n\n"
        "# 7. Iniciar el servidor local\n"
        "python manage.py runserver 127.0.0.1:8000\n\n"
        "# 8. Abrir en el navegador: http://127.0.0.1:8000/\n"
        "# Credenciales de prueba: dueno@coagra.cl / SmartFinanzas2026!"
    )

    add_callout(
        doc,
        "¡PROYECTO DESPLEGADO CON ÉXITO! Siguiendo esta secuencia, su instancia local de SmartFinanzas estará 100% operativa con conexión a base de datos, módulos transaccionales, tuberías ETL y modelos de inteligencia artificial listos para su uso y desarrollo.",
        title="DESPLIEGUE EXITOSO",
        kind="succ"
    )

    # Guardar documento
    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Guia_Despliegue_Local_SmartFinanzas.docx")
    doc.save(output_path)
    print(f"Guía de Despliegue Local generada con éxito en: {output_path}")
    print(f"Tamaño final del archivo: {os.path.getsize(output_path):,} bytes")

if __name__ == "__main__":
    build_deployment_guide()
