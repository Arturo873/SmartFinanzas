"""
Generador completo del Manual de Usuario Oficial de SmartFinanzas (.docx).
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

HEX_NAVY = "1E3A8A"       # Azul Marino Principal
HEX_BLUE = "2563EB"       # Azul Acento
HEX_SLATE = "1E293B"      # Texto Oscuro
HEX_MUTED = "64748B"      # Texto Secundario
HEX_LIGHT_BG = "F8FAFC"   # Fondo Tablas
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
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
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

def add_screenshot_figure(doc, img_rel_path, fig_num, caption_text, width=Inches(6.1)):
    full_path = os.path.abspath(img_rel_path)
    if not os.path.exists(full_path):
        p_err = doc.add_paragraph()
        r_err = p_err.add_run(f"[Imagen no encontrada: {img_rel_path}]")
        r_err.font.color.rgb = COLOR_RED
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

def build_manual():
    print("Iniciando la construcción del Manual de Usuario SmartFinanzas...")
    doc = Document()
    
    # Configuración de márgenes estándar de 1 pulgada (2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Encabezado y pie de página
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("SmartFinanzas SaaS | Manual de Usuario Oficial | Confidencial")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # PORTADA CORPORATIVA
    # -------------------------------------------------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("SISTEMA DE GESTIÓN Y ALERTA TEMPRANA FINANCIERA")
    r_pre.font.name = "Calibri"
    r_pre.font.size = Pt(12)
    r_pre.font.bold = True
    r_pre.font.color.rgb = COLOR_BLUE

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("SMARTFINANZAS")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(32)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(28)
    r_sub = p_sub.add_run("Manual Integral de Usuario, Guía de Operaciones y Referencia de Inteligencia Predictiva")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = COLOR_SLATE

    # Tabla de metadatos de portada
    tbl_meta = doc.add_table(rows=1, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    col_w = [Inches(2.2), Inches(4.3)]
    
    style_table_header(tbl_meta, col_w, ["Parámetro del Documento", "Detalle de Emisión"])
    meta_rows = [
        ("Versión del Sistema:", "SmartFinanzas Cloud v1.0 (Producción)"),
        ("Tipo de Documento:", "Manual de Operación y Manual de Usuario por Roles"),
        ("Empresa / Caso de Estudio:", "COAGRA S.A. / Red de Pequeñas y Medianas Empresas"),
        ("Perfiles Cubiertos:", "Trabajador (POS), Dueño (Gerencia), Contador (ETL), Administrador"),
        ("Motor Analítico:", "Machine Learning (LightGBM) + Explicabilidad XAI (SHAP)"),
        ("Horizonte Predictivo:", "Alerta Temprana a 90 Días (Trimestre Qt+1)"),
        ("Fecha de Publicación:", "Noviembre 2026"),
        ("Estado de Aprobación:", "Vigente - Control de Calidad Aprobado")
    ]
    for i, row in enumerate(meta_rows):
        add_table_row(tbl_meta, col_w, row, is_even=(i%2==0))
    set_table_borders(tbl_meta)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_after = Pt(40)

    add_callout(
        doc,
        "Este manual describe los procedimientos operativos estándar para cada rol del sistema, los mecanismos de integración de datos contables (ETL), el control transaccional del Punto de Venta (POS) y la correcta interpretación del Semáforo de Riesgo y el modelo SHAP.",
        title="DOCUMENTO OFICIAL DE ADIESTRAMIENTO",
        kind="info"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CONTROL DE VERSIONES Y FIRMAS
    # -------------------------------------------------------------
    add_heading_styled(doc, "Control de Versiones y Aprobaciones", level=1)
    
    p_vdesc = doc.add_paragraph()
    p_vdesc.add_run("El presente documento es auditado y actualizado periódicamente con cada nueva versión del sistema.")
    
    tbl_vers = doc.add_table(rows=1, cols=5)
    tbl_vers.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_v = [Inches(0.8), Inches(1.1), Inches(1.5), Inches(1.8), Inches(1.3)]
    style_table_header(tbl_vers, col_w_v, ["Versión", "Fecha", "Autor", "Descripción del Cambio", "Aprobador"])
    vers_data = [
        ("v1.0", "17/11/2026", "Equipo SmartFinanzas", "Emisión inicial completa con capturas reales", "Gerencia General"),
        ("v1.1", "17/11/2026", "Área de QA y Finanzas", "Validación de fórmulas V1-V7 y flujo RBAC", "Comité de Auditoría")
    ]
    for i, r in enumerate(vers_data):
        add_table_row(tbl_vers, col_w_v, r, is_even=(i%2==0))
    set_table_borders(tbl_vers)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # TABLA DE CONTENIDOS (ÍNDICE FORMAL)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Índice General de Contenidos", level=1)
    
    toc_items = [
        ("Capítulo 1: Introducción y Propósito del Sistema", "1.1 Visión General | 1.2 Objetivos Estratégicos | 1.3 Arquitectura y Módulos"),
        ("Capítulo 2: Modelo de Seguridad y Roles de Usuario (RBAC)", "2.1 Filosofía de Control de Acceso | 2.2 Perfiles Operativos | 2.3 Matriz de Permisos"),
        ("Capítulo 3: Acceso al Sistema y Registro de Empresas", "3.1 Autenticación (Login) | 3.2 Registro de Empresas y Administradores"),
        ("Capítulo 4: Manual del Trabajador (Punto de Venta - POS)", "4.1 Entorno POS | 4.2 Registro de Ventas | 4.3 Descuentos | 4.4 Comisiones | 4.5 Bloqueo por Cierre"),
        ("Capítulo 5: Manual del Dueño (Gestión de Flujo y Dashboard)", "5.1 Arqueo de Caja | 5.2 Historial | 5.3 Semáforo de Riesgo | 5.4 SHAP | 5.5 Tendencias | 5.6 Recomendaciones | 5.7 Predictivo | 5.8 Exportar PDF"),
        ("Capítulo 6: Manual del Contador (Módulo ETL y Validación)", "6.1 Ingesta IFRS | 6.2 Matriz Ratios V1-V7 | 6.3 Outliers | 6.4 Ejecutar Análisis | 6.5 Auditoría"),
        ("Capítulo 7: Glosario de Indicadores Financieros y Fórmulas", "7.1 Los 7 Ratios Críticos (V1 a V7) | 7.2 Ratios Complementarios"),
        ("Capítulo 8: Solución de Problemas y Preguntas Frecuentes (FAQ)", "8.1 Errores Comunes de Operación | 8.2 Soporte Técnico y Asistencia")
    ]
    
    tbl_toc = doc.add_table(rows=1, cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_toc = [Inches(2.5), Inches(4.0)]
    style_table_header(tbl_toc, col_w_toc, ["Capítulo", "Subsecciones y Temas Abordados"])
    for i, item in enumerate(toc_items):
        add_table_row(tbl_toc, col_w_toc, item, is_even=(i%2==0))
    set_table_borders(tbl_toc)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 1: INTRODUCCIÓN Y PROPÓSITO DEL SISTEMA
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 1: Introducción y Propósito del Sistema", level=1)
    
    add_heading_styled(doc, "1.1 Visión General del Negocio", level=2)
    add_paragraph_styled(
        doc,
        "Las pequeñas y medianas empresas (PYMEs) en Chile y Latinoamérica enfrentan un entorno económico volátil, donde la principal causa de cierre no radica en la falta de rentabilidad contable, sino en la asfixia del flujo de caja (insolvencia por liquidez). Tradicionalmente, los informes contables se emiten de forma tardía, semanas o meses después de ocurridos los hechos, impidiendo que el dueño del negocio reaccione a tiempo."
    )
    add_paragraph_styled(
        doc,
        "SmartFinanzas nace como una plataforma integral de software como servicio (SaaS) diseñada para resolver esta asimetría, combinando el control transaccional diario (Punto de Venta y Arqueo de Caja) con un motor avanzado de Machine Learning que anticipa el riesgo de insolvencia con 90 días de antelación (horizonte Qt+1)."
    )

    add_heading_styled(doc, "1.2 Objetivos Estratégicos", level=2)
    add_bullet_styled(doc, "Proveer un sistema ágil para la facturación diaria, cálculo de IVA, descuentos comerciales y deducción automática de comisiones de adquirencia bancaria (Transbank, Redelcom).", "Control Operativo Diario: ")
    add_bullet_styled(doc, "Garantizar la disciplina de caja mediante el conteo físico de gaveta, registrando sobrantes, faltantes y justificaciones obligatorias.", "Integridad de Flujo de Efectivo: ")
    add_bullet_styled(doc, "Facilitar la carga masiva de balances contables estandarizados bajo norma IFRS, calculando instantáneamente los 7 ratios financieros clave (V1 a V7).", "Normalización Contable (ETL): ")
    add_bullet_styled(doc, "Evaluar la probabilidad de insolvencia y clasificar el riesgo en un Semáforo visual intuitivo (Verde, Amarillo, Rojo).", "Alerta Temprana de Insolvencia: ")
    add_bullet_styled(doc, "Eliminar la 'caja negra' de la Inteligencia Artificial mediante valores SHAP (SHapley Additive exPlanations), indicando exactamente qué 3 variables amenazan la estabilidad de la empresa.", "Explicabilidad Transparente (XAI): ")

    add_heading_styled(doc, "1.3 Arquitectura General de la Solución", level=2)
    add_paragraph_styled(
        doc,
        "La plataforma se compone de cuatro grandes capas interconectadas:",
        bold_prefix="Módulos Fundamentales: "
    )
    add_bullet_styled(doc, "Gestiona el catálogo de productos, clientes, emisión de comprobantes y cierre diario de caja.", "1. Módulo Transaccional: ")
    add_bullet_styled(doc, "Procesa archivos Excel/CSV de balance, realiza limpieza de datos, detecta valores atípicos (outliers) y persiste los ratios financieros.", "2. Módulo ETL (Extract, Transform, Load): ")
    add_bullet_styled(doc, "Aplica modelos entrenados de Gradient Boosting (LightGBM) para estimar el Score Crediticio (0 a 100) y calcular las contribuciones marginales de SHAP.", "3. Capa Analítica y Predictiva: ")
    add_bullet_styled(doc, "Panel centralizado para la alta gerencia que consolida tacómetros, curvas de tendencia, recomendaciones accionables y reportes ejecutivos en PDF.", "4. Dashboard Directivo: ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 2: MODELO DE SEGURIDAD Y ROLES DE USUARIO (RBAC)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 2: Modelo de Seguridad y Roles de Usuario (RBAC)", level=1)
    
    add_heading_styled(doc, "2.1 Filosofía de Control de Acceso", level=2)
    add_paragraph_styled(
        doc,
        "SmartFinanzas implementa un estricto esquema de Control de Acceso Basado en Roles (RBAC - Role-Based Access Control) acoplado a un aislamiento multi-inquilino (multi-tenant). Esto garantiza dos principios vitales de seguridad:"
    )
    add_bullet_styled(doc, "Cada empresa opera en un silo lógico completamente hermético. Los datos financieros, clientes y transacciones de una empresa son estrictamente invisibles para cualquier otra organización.", "Aislamiento por Empresa: ")
    add_bullet_styled(doc, "Los usuarios acceden exclusivamente a las funciones requeridas para su labor operativa, previniendo alteraciones contables indebidas o fuga de información confidencial.", "Separación de Funciones: ")

    add_heading_styled(doc, "2.2 Definición de los Cuatro Perfiles de Usuario", level=2)
    add_paragraph_styled(
        doc,
        "El sistema distingue cuatro niveles de acceso con responsabilidades bien delimitadas:"
    )
    add_bullet_styled(doc, "Diseñado para cajeros, vendedores y personal de mostrador. Su acceso está restringido al Punto de Venta (POS) para emitir ventas durante la jornada laboral. No puede ver balances contables, ni modificar ratios, ni visualizar el Dashboard Gerencial ni ejecutar el cierre de caja.", "1. Perfil Trabajador: ")
    add_bullet_styled(doc, "Diseñado para gerentes generales, socios y directores de la empresa. Dispone de acceso al Dashboard Ejecutivo, semáforo de riesgo, explicabilidad SHAP, proyecciones a 90 días, aprobación y ejecución del arqueo diario de caja, consulta de historiales y descarga de reportes PDF.", "2. Perfil Dueño: ")
    add_bullet_styled(doc, "Diseñado para contadores internos, auditores y analistas financieros. Tiene control exclusivo sobre el Módulo ETL: descarga de plantillas IFRS, carga de balances, auditoría de anomalías y outliers, cálculo de la matriz V1-V7 y ejecución del reentrenamiento predictivo.", "3. Perfil Contador: ")
    add_bullet_styled(doc, "Superusuario administrativo encargado de gestionar los colaboradores de la empresa, asignar roles, restablecer contraseñas y mantener la configuración corporativa.", "4. Perfil Administrador: ")

    add_heading_styled(doc, "2.3 Matriz de Permisos por Módulo", level=2)
    tbl_rbac = doc.add_table(rows=1, cols=5)
    tbl_rbac.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_rbac = [Inches(2.5), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0)]
    style_table_header(tbl_rbac, col_w_rbac, ["Módulo / Funcionalidad", "Trabajador", "Dueño", "Contador", "Administrador"])
    
    rbac_rows = [
        ("Punto de Venta (Emisión de Ventas)", "Sí", "Sí", "No", "Sí"),
        ("Aplicación de Descuentos Manuales", "Sí", "Sí", "No", "Sí"),
        ("Ejecución de Arqueo y Cierre de Caja", "No", "Sí", "No", "Sí"),
        ("Historial de Cierres Diarios", "No", "Sí", "No", "Sí"),
        ("Dashboard y Tacómetro de Riesgo", "No", "Sí", "Lectura", "Sí"),
        ("Explicabilidad SHAP (Top 3)", "No", "Sí", "Lectura", "Sí"),
        ("Proyección Predictiva a 90 Días", "No", "Sí", "Lectura", "Sí"),
        ("Descarga de Informes en PDF", "No", "Sí", "Lectura", "Sí"),
        ("Carga de Balances IFRS (ETL)", "No", "No", "Sí", "Sí"),
        ("Matriz de Ratios Financieros V1-V7", "No", "No", "Sí", "Sí"),
        ("Auditoría y Gestión de Outliers", "No", "No", "Sí", "Sí"),
        ("Gestión de Usuarios y Roles", "No", "No", "No", "Sí"),
    ]
    for i, r in enumerate(rbac_rows):
        add_table_row(tbl_rbac, col_w_rbac, r, is_even=(i%2==0))
    set_table_borders(tbl_rbac)

    add_callout(
        doc,
        "Si un usuario con perfil 'Trabajador' intenta navegar directamente a las URL del Dashboard (/dashboard/) o del Módulo ETL (/etl/carga/), el sistema bloqueará la petición mediante el middleware de seguridad RBAC, redireccionándolo a su pantalla asignada con un mensaje de acceso denegado.",
        title="REGLA DE SEGURIDAD CRÍTICA",
        kind="warn"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 3: ACCESO AL SISTEMA Y REGISTRO DE EMPRESAS
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 3: Acceso al Sistema y Registro de Empresas", level=1)
    
    add_heading_styled(doc, "3.1 Proceso de Inicio de Sesión (Login)", level=2)
    add_paragraph_styled(
        doc,
        "Para ingresar a la plataforma SmartFinanzas, el usuario debe abrir un navegador web moderno (Google Chrome, Microsoft Edge, Mozilla Firefox o Safari) y dirigirse a la dirección asignada del servidor (por ejemplo, http://127.0.0.1:8000/login/ o el dominio corporativo)."
    )
    add_paragraph_styled(
        doc,
        "El formulario de autenticación solicita dos credenciales obligatorias:",
        bold_prefix="Campos requeridos: "
    )
    add_bullet_styled(doc, "Dirección de correo electrónico registrada del usuario (por ejemplo, dueno@coagra.cl o contador@coagra.cl).", "Correo Electrónico: ")
    add_bullet_styled(doc, "Clave secreta definida durante el registro o asignada por el administrador corporativo.", "Contraseña: ")

    add_screenshot_figure(
        doc,
        "docs/capturas/01_login.png",
        "3.1",
        "Pantalla de Inicio de Sesión en SmartFinanzas con validación de credenciales corporativas."
    )

    add_paragraph_styled(
        doc,
        "Una vez presionado el botón 'Iniciar Sesión', el motor de autenticación valida las credenciales y redirige automáticamente al usuario según su rol predeterminado: los dueños y contadores son dirigidos al Dashboard Gerencial, mientras que los trabajadores son guiados directamente a la pantalla de Punto de Venta."
    )

    add_heading_styled(doc, "3.2 Registro de Nuevas Empresas y Administradores", level=2)
    add_paragraph_styled(
        doc,
        "Si una empresa aún no cuenta con una cuenta institucional en SmartFinanzas, el representante o administrador puede registrar la entidad desde el enlace 'Registrarse' ubicado en la pantalla de bienvenida."
    )
    add_paragraph_styled(
        doc,
        "El formulario de registro solicita datos corporativos indispensables:",
        bold_prefix="Información requerida de la Empresa: "
    )
    add_bullet_styled(doc, "Identificador tributario oficial con dígito verificador (por ejemplo, 76.123.456-7).", "RUT de la Empresa: ")
    add_bullet_styled(doc, "Nombre legal de la compañía registrado ante el Servicio de Impuestos Internos.", "Razón Social: ")
    add_bullet_styled(doc, "Clasificación de actividad económica (Agrícola, Comercio minorista, Servicios, etc.).", "Giro Comercial: ")
    add_bullet_styled(doc, "Nombre y correo del usuario maestro con rol 'Administrador'.", "Usuario Administrador: ")
    add_bullet_styled(doc, "Mínimo 8 caracteres, combinando mayúsculas, números y símbolos.", "Contraseña Segura: ")

    add_screenshot_figure(
        doc,
        "docs/capturas/02_registro.png",
        "3.2",
        "Formulario de Registro de Nueva Empresa y creación del usuario Administrador en la plataforma."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 4: MANUAL DEL TRABAJADOR (PUNTO DE VENTA - POS)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 4: Manual del Trabajador (Punto de Venta - POS)", level=1)
    
    add_heading_styled(doc, "4.1 Entorno del Punto de Venta (POS)", level=2)
    add_paragraph_styled(
        doc,
        "El módulo de Punto de Venta está optimizado para la agilidad en la atención a clientes en mesón, sucursales o canales de venta directa. Su interfaz intuitiva permite registrar comprobantes mercantiles en segundos, calculando automáticamente impuestos y deducciones bancarias."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/10_punto_de_venta.png",
        "4.1",
        "Interfaz del Punto de Venta (POS) con selección de productos, cliente, método de pago y desglose financiero en vivo."
    )

    add_heading_styled(doc, "4.2 Procedimiento Paso a Paso para Registrar una Venta", level=2)
    add_paragraph_styled(
        doc,
        "Para emitir una transacción comercial válida, el cajero debe completar las siguientes etapas:"
    )
    add_bullet_styled(doc, "Elegir de la lista desplegable el cliente registrado o seleccionar 'Cliente Ocasional / Boleta'.", "Paso 1: Selección del Cliente: ")
    add_bullet_styled(doc, "Seleccionar el ítem a comercializar. El sistema cargará de inmediato el precio unitario oficial de lista.", "Paso 2: Selección del Producto: ")
    add_bullet_styled(doc, "Digitar el número de unidades vendidas. El subtotal se actualizará inmediatamente.", "Paso 3: Definición de Cantidad: ")
    add_bullet_styled(doc, "En caso de promociones autorizadas, ingresar el porcentaje de rebaja (por ejemplo, 5%). El sistema recalculará la base neta y el IVA (19%).", "Paso 4: Aplicación de Descuento: ")
    add_bullet_styled(doc, "Elegir entre Efectivo, Tarjeta de Débito, Tarjeta de Crédito o Transferencia Electrónica.", "Paso 5: Medio de Pago: ")
    add_bullet_styled(doc, "Hacer clic en 'Confirmar y Guardar Venta'. El comprobante quedará registrado y se actualizará el stock.", "Paso 6: Finalización: ")

    add_heading_styled(doc, "4.3 Tratamiento de Descuentos Comerciales y Comisiones de Adquirencia", level=2)
    add_paragraph_styled(
        doc,
        "Una de las mayores ventajas de SmartFinanzas frente a los sistemas POS convencionales es su desglose financiero transparente:",
        bold_prefix="Transparencia Financiera en Tiempo Real: "
    )
    add_bullet_styled(doc, "El cajero visualiza exactamente el ahorro otorgado al cliente y cómo impacta en la base gravable del IVA.", "Descuentos en Vivo: ")
    add_bullet_styled(doc, "Cuando se selecciona pago con Tarjeta de Débito o Crédito, el sistema aplica la tasa de comisión bancaria pactada (ej. 1.5% o 2.5%). Esto permite que la empresa conozca con total precisión el monto líquido real que ingresará a la cuenta corriente, aislando el gasto de intermediación financiera.", "Comisión de Adquirencia Bancaria: ")

    add_callout(
        doc,
        "POLÍTICA DE BLOQUEO POR CIERRE DE CAJA: Una vez que el Dueño o Administrador ejecuta el Cierre Diario de Caja, el Punto de Venta se bloquea automáticamente para esa jornada. El cajero no podrá ingresar ventas extemporáneas con fecha del día cerrado. Esto garantiza la trazabilidad e impide fraudes contables.",
        title="REGLA OPERATIVA IMPORTANTE",
        kind="danger"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 5: MANUAL DEL DUEÑO (GESTIÓN DE CAJA Y DASHBOARD)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 5: Manual del Dueño (Gestión de Flujo y Dashboard)", level=1)
    
    add_heading_styled(doc, "5.1 Cierre y Arqueo Diario de Caja", level=2)
    add_paragraph_styled(
        doc,
        "Al finalizar la jornada laboral, el Dueño de la empresa debe proceder al Arqueo Físico de Caja. Este proceso audita el dinero en efectivo que realmente existe en la gaveta contra el total de ventas en efectivo registradas por los trabajadores menos los retiros autorizados."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/08_cierre_caja.png",
        "5.1",
        "Formulario de Cierre y Arqueo Diario de Caja, con conteo físico de gaveta y justificación de descuadres."
    )

    add_paragraph_styled(
        doc,
        "El procedimiento de arqueo exige:",
        bold_prefix="Pasos del Arqueo: "
    )
    add_bullet_styled(doc, "El Dueño cuenta físicamente el dinero en la gaveta y digita el monto en la casilla 'Efectivo Real en Caja'.", "1. Conteo Físico: ")
    add_bullet_styled(doc, "El sistema compara dicho monto con el 'Efectivo Esperado' (Ventas Efectivo - Retiros de Caja).", "2. Cálculo de la Diferencia: ")
    add_bullet_styled(doc, "Si existe una diferencia (sobrante o faltante), el sistema despliega el campo obligatorio 'Justificación del Descuadre', donde el responsable debe documentar la causa del desfase antes de cerrar.", "3. Justificación de Descuadres: ")
    add_bullet_styled(doc, "Al presionar 'Confirmar Cierre Diario', la caja queda sellada y se genera un folio oficial inmutable.", "4. Cierre Definitivo: ")

    add_heading_styled(doc, "5.2 Historial y Auditoría de Cierres", level=2)
    add_paragraph_styled(
        doc,
        "El Dueño puede consultar en todo momento la bitácora histórica de cierres diarios para verificar la consistencia del flujo de caja, las justificaciones ingresadas y los patrones de descuadre repetitivos."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/09_historial_cierres.png",
        "5.2",
        "Historial consolidado de Cierres Diarios de Caja con estado de cuadratura y trazabilidad de folios."
    )

    add_heading_styled(doc, "5.3 Panel de Control Gerencial (Dashboard)", level=2)
    add_paragraph_styled(
        doc,
        "El Dashboard Gerencial es el centro neurálgico para la toma de decisiones. Presenta de manera ejecutiva el estado de salud de la empresa, su Score Crediticio global y el Semáforo de Riesgo a 90 días."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/03_dashboard_general.png",
        "5.3",
        "Dashboard Gerencial de SmartFinanzas: Tacómetro del Semáforo de Riesgo, Score Crediticio y Tarjetas de KPIs."
    )

    add_paragraph_styled(
        doc,
        "El Semáforo de Riesgo se calcula mediante un modelo de Gradient Boosting y clasifica la empresa en tres rangos:",
        bold_prefix="Rangos del Semáforo de Riesgo Financiero: "
    )
    add_bullet_styled(doc, "La empresa presenta sólida solvencia operativa, holgura de liquidez corriente y bajo apalancamiento. Probabilidad mínima de insolvencia.", "Zona Verde (Score <= 35 puntos): ")
    add_bullet_styled(doc, "Nivel de alerta preventiva. Se observa deterioro en márgenes operativos, acumulación de inventarios lentos o endeudamiento de corto plazo. Se sugiere aplicar las recomendaciones del sistema.", "Zona Amarilla (Score entre 36 y 70 puntos): ")
    add_bullet_styled(doc, "Alerta máxima de estrés financiero. Alta probabilidad de incapacidad de pago en los próximos 90 días si no se inyecta liquidez o se renegocian pasivos de forma inmediata.", "Zona Roja (Score > 70 puntos): ")

    add_heading_styled(doc, "5.4 Módulo de Explicabilidad con SHAP (XAI)", level=2)
    add_paragraph_styled(
        doc,
        "A diferencia de los modelos tradicionales de inteligencia artificial que operan como 'cajas negras', SmartFinanzas utiliza la teoría de juegos cooperativos mediante valores SHAP (SHapley Additive exPlanations) para descomponer con exactitud matemática el origen del score."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/04_dashboard_shap.png",
        "5.4",
        "Módulo de Explicabilidad SHAP: Identificación gráfica y cuantitativa del Top 3 de factores determinantes del riesgo."
    )

    add_paragraph_styled(
        doc,
        "El panel destaca las 3 variables de mayor peso relativo (por ejemplo, Rotación de Inventarios, Razón Corriente o Margen Operacional), indicando si cada una empuja el semáforo hacia la zona segura (valor positivo/verde) o hacia la zona de peligro (valor negativo/rojo). Esto permite que el Dueño sepa exactamente en qué palanca operativa intervenir."
    )

    add_heading_styled(doc, "5.5 Curva de Tendencia Temporal e Históricos", level=2)
    add_paragraph_styled(
        doc,
        "El gráfico de evolución temporal permite visualizar el comportamiento del Score de Riesgo a lo largo de los trimestres, identificando si la empresa se está recuperando o si el deterioro financiero se está agravando progresivamente."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/05_dashboard_tendencia.png",
        "5.5",
        "Curva de Tendencia Temporal del Score de Riesgo con selectores de período histórico."
    )

    add_heading_styled(doc, "5.6 Plan de Acción y Sugerencias Financieras Automatizadas", level=2)
    add_paragraph_styled(
        doc,
        "El motor de SmartFinanzas no se limita a diagnosticar el problema: genera prescripciones estratégicas personalizadas para la empresa, priorizando las medidas correctivas según el impacto detectado por SHAP."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/06_recomendaciones.png",
        "5.6",
        "Panel de Sugerencias Financieras Inteligentes y Plan de Acción Estratégico."
    )

    add_heading_styled(doc, "5.7 Proyección Predictiva a 90 Días (Qt+1) y Exportación a PDF", level=2)
    add_paragraph_styled(
        doc,
        "El módulo predictivo anticipa la situación de la empresa en el próximo trimestre, permitiendo anticipar quiebras técnicas antes de que sean visibles en las cartolas bancarias."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/07_dashboard_predictivo.png",
        "5.7",
        "Módulo Predictivo a 90 Días con simulaciones de escenarios y proyecciones de ratios futuros."
    )

    add_paragraph_styled(
        doc,
        "Desde la parte superior del Dashboard, el Dueño puede presionar el botón 'Exportar Informe PDF' para generar un informe gerencial formal timbrado, ideal para presentar ante comités bancarios, entidades crediticias o directorios."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 6: MANUAL DEL CONTADOR (MÓDULO ETL Y VALIDACIÓN)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 6: Manual del Contador (Módulo ETL y Validación Contable)", level=1)
    
    add_heading_styled(doc, "6.1 Ingesta de Balances y Carga de Archivos IFRS", level=2)
    add_paragraph_styled(
        doc,
        "El Contador de la empresa es el responsable técnico de alimentar el sistema con los Estados Financieros de cada cierre de período. Para garantizar la consistencia analítica, SmartFinanzas provee una plantilla estandarizada bajo normativa IFRS."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/11_etl_carga.png",
        "6.1",
        "Módulo ETL: Carga masiva de balances financieros, descarga de plantilla IFRS y validación sintáctica."
    )

    add_paragraph_styled(
        doc,
        "El proceso de ingesta se desarrolla en tres etapas:",
        bold_prefix="Etapas de Carga: "
    )
    add_bullet_styled(doc, "El Contador descarga el archivo base en formato Excel (.xlsx) o CSV con las cuentas requeridas.", "1. Descarga de Plantilla Oficial: ")
    add_bullet_styled(doc, "Completa los montos de Activo Corriente, Activo Total, Pasivo Corriente, Pasivo Total, Patrimonio, Ventas, Costos, EBITDA y Gastos Financieros.", "2. Llenado de Cuentas: ")
    add_bullet_styled(doc, "Arrastra el archivo a la zona de carga o presiona 'Examinar'. El sistema analiza las columnas y valida que se cumpla la ecuación contable básica (Activo = Pasivo + Patrimonio).", "3. Carga y Validación Automática: ")

    add_heading_styled(doc, "6.2 Matriz de los 7 Ratios Financieros Base (V1 a V7)", level=2)
    add_paragraph_styled(
        doc,
        "Una vez procesado el archivo, el motor ETL calcula instantáneamente los 7 ratios financieros fundamentales (variables predictivas V1 a V7) y genera una matriz comparativa."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/12_etl_ratios.png",
        "6.2",
        "Matriz de los 7 Ratios Financieros (V1 a V7) con semaforización de valores y análisis evolutivo."
    )

    add_heading_styled(doc, "6.3 Detección de Anomalías y Tratamiento de Outliers", level=2)
    add_paragraph_styled(
        doc,
        "Para prevenir errores humanos de digitación (como ceros adicionales o valores negativos imposibles), el Módulo ETL incorpora un algoritmo de detección de valores anómalos (Outliers) basado en rangos intercuartílicos e históricos de la empresa."
    )
    add_paragraph_styled(
        doc,
        "Si un ratio supera los umbrales razonables de la industria, el sistema marca el registro con una advertencia visual. El Contador puede corregir el archivo fuente y volver a subirlo, o confirmar profesionalmente que el valor corresponde a un evento extraordinario real de la empresa."
    )

    add_heading_styled(doc, "6.4 Ejecución de la Predicción y Trazabilidad Histórica", level=2)
    add_paragraph_styled(
        doc,
        "Con los ratios validados, el Contador hace clic en 'Ejecutar Análisis y Predicción'. Esta acción dispara el modelo de Machine Learning, recalcula el Score Crediticio y actualiza inmediatamente los semáforos del Dashboard del Dueño."
    )

    add_screenshot_figure(
        doc,
        "docs/capturas/13_etl_historial.png",
        "6.3",
        "Historial y Bitácora de Auditoría del Módulo ETL, registrando autor, fecha y estado de cada balance procesado."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 7: GLOSARIO DE INDICADORES FINANCIEROS Y FÓRMULAS
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 7: Glosario de Indicadores Financieros y Fórmulas", level=1)
    
    add_paragraph_styled(
        doc,
        "A continuación se presenta la definición matemática, conceptual y los rangos de interpretación de los 7 ratios primarios (V1 a V7) utilizados por el motor de inteligencia predictiva de SmartFinanzas."
    )

    tbl_ratios = doc.add_table(rows=1, cols=4)
    tbl_ratios.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_r = [Inches(1.0), Inches(1.8), Inches(2.2), Inches(1.5)]
    style_table_header(tbl_ratios, col_w_r, ["Código", "Nombre del Ratio", "Fórmula Matemática", "Rango Saludable"])

    ratios_data = [
        ("V1", "Razón Corriente (Liquidez)", "Activo Circulante / Pasivo Circulante", "1.2 a 2.0 veces"),
        ("V2", "Prueba Ácida", "(Activo Circulante - Inventarios) / Pasivo Circulante", ">= 1.0 veces"),
        ("V3", "Nivel de Endeudamiento", "Pasivo Total / Activo Total", "0.4 a 0.6 (40% - 60%)"),
        ("V4", "Cobertura de Gastos Financieros", "EBITDA / Gastos Financieros", ">= 3.0 veces"),
        ("V5", "Margen Operacional", "EBITDA / Ingresos Operacionales (Ventas)", ">= 15%"),
        ("V6", "Margen Neto", "Resultado del Ejercicio / Ventas Netas", ">= 8%"),
        ("V7", "Rotación de Capital de Trabajo", "Ventas Netas / Capital de Trabajo Neto", "4.0 a 8.0 veces/año"),
        ("ROA", "Retorno sobre Activos", "Utilidad Neta / Activo Total", ">= 5%"),
        ("ROE", "Retorno sobre Patrimonio", "Utilidad Neta / Patrimonio Neto", ">= 12%"),
        ("COV", "Cobertura de Intereses Corto Plazo", "Flujo Operativo / Intereses Devengados", ">= 2.5 veces")
    ]
    for i, r in enumerate(ratios_data):
        add_table_row(tbl_ratios, col_w_r, r, is_even=(i%2==0))
    set_table_borders(tbl_ratios)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO 8: SOLUCIÓN DE PROBLEMAS Y PREGUNTAS FRECUENTES (FAQ)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Capítulo 8: Solución de Problemas y Preguntas Frecuentes (FAQ)", level=1)
    
    faqs = [
        (
            "1. El trabajador intenta registrar una venta pero el sistema muestra el error 'Caja del día cerrada'. ¿Qué debe hacer?",
            "Este mensaje indica que el Dueño o Administrador ya ejecutó el Cierre Diario de Caja para esa jornada. Por seguridad y consistencia contable, no se permiten nuevas transacciones con la fecha cerrada. Si la venta pertenece al turno del día siguiente, verifique que la fecha del sistema corresponda a la nueva jornada hábil."
        ),
        (
            "2. Se detectó una diferencia física de dinero al realizar el arqueo de caja. ¿Cómo se procede?",
            "El Dueño debe ingresar el monto exacto recontado en la casilla 'Efectivo Real en Caja'. Si el valor no coincide con el efectivo esperado, el sistema exigirá obligatoriamente completar el campo 'Justificación del Descuadre'. Describa el motivo (por ejemplo, propina no registrada, error en entrega de vuelto o retiro de emergencia no anotado) y guarde el cierre. La justificación quedará registrada en la auditoría inmutable."
        ),
        (
            "3. El semáforo de riesgo cambió abruptamente de Verde a Amarillo. ¿Cuál es el primer paso?",
            "Diríjase a la sección 'Módulo de Explicabilidad SHAP' del Dashboard Gerencial. Observe la barra con mayor impacto negativo: allí se indicará si el cambio se debió a una caída en el Margen Operacional (V5), un aumento excesivo del pasivo corriente (V3) o una baja de liquidez (V1). Luego, consulte las 'Sugerencias Financieras' para aplicar las recomendaciones prescriptivas."
        ),
        (
            "4. La carga del balance en el módulo ETL fue rechazada con error de estructura. ¿Cómo se soluciona?",
            "Asegúrese de descargar la plantilla oficial desde el botón 'Descargar Plantilla Ejemplo' del módulo ETL. No altere los nombres de las cabeceras ni elimine columnas. Verifique que los valores numéricos no contengan símbolos de moneda (como $) ni letras, y que la suma de Activos coincida con la suma de Pasivos y Patrimonio."
        ),
        (
            "5. ¿Cómo se crea un nuevo usuario Trabajador o Contador en la empresa?",
            "El usuario con rol 'Administrador' debe ingresar a la sección de Configuración de Usuarios, hacer clic en 'Nuevo Usuario', ingresar el nombre, correo electrónico institucional, asignar el rol correspondiente (Trabajador o Contador) y definir la contraseña provisional de acceso."
        )
    ]

    for q, a in faqs:
        add_paragraph_styled(doc, q, bold_prefix="", space_after=2)
        add_paragraph_styled(doc, a, bold_prefix="Respuesta: ", space_after=10)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_callout(
        doc,
        "MESA DE AYUDA Y SOPORTE TÉCNICO: Si experimenta inconvenientes técnicos no resueltos en esta guía, contacte a soporte corporativo al correo soporte@smartfinanzas.cl o a través de la mesa de soporte en línea de su consola institucional.",
        title="CANALES DE ASISTENCIA TÉCNICA",
        kind="info"
    )

    # Guardar documento
    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Manual_de_Usuario_SmartFinanzas.docx")
    doc.save(output_path)
    print(f"Manual generado con éxito en: {output_path}")
    print(f"Tamaño final del archivo: {os.path.getsize(output_path):,} bytes")

if __name__ == "__main__":
    build_manual()
