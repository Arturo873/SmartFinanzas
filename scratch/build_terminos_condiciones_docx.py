"""
Generador del Documento Oficial de Términos y Condiciones de SmartFinanzas (.docx).
Compila de forma exhaustiva los 4 marcos legales y normativos implementados en el proyecto:
1. Términos de Servicio, Confidencialidad y Descargo Financiero (Registro).
2. Términos Legales de Rendición de Fondos, Arqueo Físico y Cierre Contable (Transaccional).
3. Términos de Ingesta, Veracidad Contable y Validación IFRS / CMF (ETL).
4. Descargo de Responsabilidad y Términos de Inferencia Predictiva (Dashboard / ML / PDF).
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
        run.font.size = Pt(15)
        run.bold = True
        run.font.color.rgb = COLOR_NAVY
    elif level == 2:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(12.5)
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
        r_pre.font.size = Pt(10)
        r_pre.font.color.rgb = COLOR_SLATE
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10)
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
        r_pre.font.size = Pt(9.5)
        r_pre.font.color.rgb = COLOR_SLATE
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = COLOR_SLATE
    return p

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

def build_terms_document():
    print("Iniciando la construcción del Compendio Oficial de Términos y Condiciones...")
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("SmartFinanzas SaaS | Compendio Jurídico y Términos Contractuales | v1.0")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # PORTADA CORPORATIVA
    # -------------------------------------------------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)
    r_pre = p_pre.add_run("INSTRUMENTO LEGAL Y MARCO REGULATORIO CORPORATIVO")
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
    r_sub = p_sub.add_run("Compendio Oficial de Términos de Servicio, Tratamiento de Datos, Veracidad IFRS, Rendición de Fondos y Descargos de Responsabilidad de Inteligencia Artificial")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_SLATE

    tbl_meta = doc.add_table(rows=1, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    col_w = [Inches(2.4), Inches(4.1)]
    
    style_table_header(tbl_meta, col_w, ["Parámetro Contractual", "Especificación del Instrumento"])
    meta_rows = [
        ("Naturaleza del Acuerdo:", "Contrato de Adhesión SaaS y Marco de Certificación Operativa"),
        ("Módulos Regulados:", "Registro (Usuarios), POS (Arqueo/Caja), ETL (IFRS) y Dashboard (ML/PDF)"),
        ("Jurisdicción y Ley Aplicable:", "República de Chile (Legislación Comercial, Laboral, Tributaria y FinTech)"),
        ("Normativas Integradas:", "Cód. Comercio, Ley 19.628, Ley 21.459, NIC 1/CMF, Cód. Trabajo, Ley FinTech 21.521"),
        ("Mecanismo de Consentimiento:", "Consentimiento Expreso por Módulo (Clickwrap con Modal Bloqueante)"),
        ("Aislamiento de Información:", "Arquitectura Multi-tenant Hermética con Cifrado de Credenciales"),
        ("Fecha de Vigencia:", "Noviembre 2026"),
        ("Estado de Publicación:", "Vigente y Vinculante para todos los Usuarios de la Plataforma")
    ]
    for i, row in enumerate(meta_rows):
        add_table_row(tbl_meta, col_w, row, is_even=(i%2==0))
    set_table_borders(tbl_meta)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_after = Pt(30)

    add_callout(
        doc,
        "AVISO LEGAL VINCULANTE: El acceso, navegación, registro de transacciones, carga de balances y consulta de diagnósticos predictivos en la plataforma SmartFinanzas implican la aceptación pura, simple y expresa de los términos contenidos en este instrumento. Ninguna persona física o jurídica podrá operar el sistema sin haber manifestado previamente su consentimiento mediante las casillas de verificación y modales normativos habilitados.",
        title="CARÁCTER VINCULANTE Y OBLIGATORIO",
        kind="warn"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # ÍNDICE GENERAL DEL COMPENDIO
    # -------------------------------------------------------------
    add_heading_styled(doc, "Índice General del Compendio Jurídico", level=1)
    
    toc_items = [
        ("Título I: Disposiciones Generales y Principios Rectores", "Naturaleza del contrato SaaS, definiciones, consentimiento electrónico y soberanía de datos."),
        ("Título II: Términos de Servicio y Confidencialidad (Módulo de Registro)", "Marco normativo, aislamiento multi-tenant, secreto comercial y deber de custodia de claves."),
        ("Título III: Términos de Rendición de Fondos y Arqueo Físico (Módulo POS)", "Fe de arqueo (Cód. Comercio), responsabilidad laboral (Cód. Trabajo), NIA 240, COSO y sellado."),
        ("Título IV: Términos de Ingesta, Veracidad Contable y Validación IFRS (Módulo ETL)", "Norma NIC 1 / IAS 1, facultades CMF, Art. 17/97 Cód. Tributario y deslinde pericial."),
        ("Título V: Descargo de Responsabilidad y Gobernanza de IA (Dashboard ML)", "Principios OCDE, IEEE 7001, límites predictivos, Ley FinTech 21.521 y Art. 41 Ley 18.046."),
        ("Título VI: Propiedad Intelectual y Licenciamiento de Software", "Derechos de autor sobre código, algoritmos, modelos .joblib y prohibiciones de ingeniería inversa."),
        ("Título VII: Protocolo de Seguridad, Criptografía y Auditoría", "Hashing de contraseñas, aislamiento relacional y trazabilidad inmutable de folios."),
        ("Título VIII: Vigencia, Modificaciones y Jurisdicción Aplicable", "Procedimiento de actualización contractual, resolución de controversias y tribunales de Santiago.")
    ]
    
    tbl_toc = doc.add_table(rows=1, cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_toc = [Inches(2.6), Inches(3.9)]
    style_table_header(tbl_toc, col_w_toc, ["Título / Capítulo", "Materias y Artículos Regulados"])
    for i, item in enumerate(toc_items):
        add_table_row(tbl_toc, col_w_toc, item, is_even=(i%2==0))
    set_table_borders(tbl_toc)

    doc.add_page_break()

    # -------------------------------------------------------------
    # TÍTULO I: DISPOSICIONES GENERALES Y PRINCIPIOS RECTORES
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título I: Disposiciones Generales y Principios Rectores", level=1)
    
    add_heading_styled(doc, "Artículo 1: Naturaleza del Acuerdo", level=2)
    add_paragraph_styled(
        doc,
        "El presente documento constituye un contrato de adhesión de servicios tecnológicos en la nube (SaaS - Software as a Service) celebrado entre SmartFinanzas SpA (en adelante, 'La Plataforma') y la persona natural o jurídica que suscribe o hace uso de la solución (en adelante, 'La Empresa' o 'El Usuario'). La utilización de cualquier módulo del software presupone la lectura íntegra, entendimiento y consentimiento vinculante de todas las estipulaciones aquí detalladas."
    )

    add_heading_styled(doc, "Artículo 2: Definiciones Operativas y Técnicas", level=2)
    add_paragraph_styled(doc, "Para la debida interpretación del presente instrumento, se establecen las siguientes definiciones:")
    add_bullet_styled(doc, "Modelo arquitectónico de software donde múltiples clientes comparten la infraestructura lógica, pero sus datos se encuentran aislados criptográfica y lógicamente en particiones inaccesibles entre sí.", "Arquitectura Multi-Tenant: ")
    add_bullet_styled(doc, "Índice numérico adimensional en escala de 0 a 100 generado por modelos supervisados de Machine Learning que evalúa la probabilidad de insolvencia a 90 días.", "Score de Riesgo Financiero: ")
    add_bullet_styled(doc, "Categorización visual del riesgo basada en umbrales matemáticos: Verde (<= 35, Saludable), Amarillo (36-70, Alerta Preventiva) y Rojo (> 70, Alerta Crítica).", "Semáforo de Insolvencia: ")
    add_bullet_styled(doc, "SHapley Additive exPlanations. Metodología basada en la teoría de juegos cooperativos que cuantifica la contribución marginal de cada ratio financiero en la composición del Score.", "Explicabilidad SHAP (XAI): ")
    add_bullet_styled(doc, "Pipeline de Extracción, Transformación y Carga encargado de ingerir balances en formato Excel/CSV, auditar la ecuación contable y calcular la matriz de ratios V1 a V7.", "Módulo ETL: ")
    add_bullet_styled(doc, "Punto de Venta comercial optimizado para el registro de ventas, cálculo de IVA, deducción de comisiones por tarjetas y control de caja.", "Módulo Transaccional (POS): ")

    add_heading_styled(doc, "Artículo 3: Mecanismo de Consentimiento Electrónico (Clickwrap)", level=2)
    add_paragraph_styled(
        doc,
        "En conformidad con la Ley N° 19.799 sobre Documentos Electrónicos, Firma Electrónica y Servicios de Certificación de Chile, la aceptación de este contrato se formaliza mediante actos positivos inequívocos ('Clickwrap'). El sistema despliega modales de lectura obligatoria con casillas de verificación bloqueantes en cuatro etapas operativas críticas: Registro de Cuenta, Arqueo de Caja, Carga de Balances ETL y Descarga de Informes Predictivos en PDF. No es posible avanzar en ninguna de dichas operaciones sin certificar la aceptación previa."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TÍTULO II: TÉRMINOS DE SERVICIO Y CONFIDENCIALIDAD (REGISTRO)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título II: Términos de Servicio, Confidencialidad y Descargo Financiero (Módulo de Registro)", level=1)
    
    add_paragraph_styled(
        doc,
        "Los siguientes términos rigen la creación de cuentas de empresa y usuarios administradores en la plataforma SmartFinanzas:"
    )

    add_heading_styled(doc, "Sección 2.1: Marco Normativo y Fuentes de Aplicación", level=2)
    add_paragraph_styled(
        doc,
        "El presente acuerdo se rige supletoriamente por las normas del Código de Comercio de la República de Chile (Libro I, Título II: De las Obligaciones de los Comerciantes) en lo relativo a la reserva de libros contables; la Ley N° 19.628 sobre Protección de la Vida Privada y sus modificaciones posteriores respecto del tratamiento consentido de datos de identificación; y la Ley N° 21.459 que tipifica delitos informáticos, asegurando el acceso legítimo y custodia de credenciales."
    )

    add_heading_styled(doc, "Sección 2.2: Objeto y Alcance de la Plataforma", level=2)
    add_paragraph_styled(
        doc,
        "SmartFinanzas es un entorno de software bajo modalidad SaaS destinado a la consolidación transaccional de ventas, arqueos diarios de caja física, ingesta de estados financieros bajo estándar IFRS y cálculo automatizado de indicadores financieros predictivos. El usuario declara que la cuenta creada será utilizada exclusivamente para la administración financiera de la empresa a la cual se vincula."
    )

    add_heading_styled(doc, "Sección 2.3: Aislamiento Multi-Tenant y Deber de Confidencialidad", level=2)
    add_paragraph_styled(
        doc,
        "Cada organización registrada opera bajo una arquitectura de estricto aislamiento de datos (Multi-tenancy). Toda información contable, de ventas, clientes y transacciones pertenecerá con carácter privativo a la empresa titular. SmartFinanzas garantiza el deber de secreto comercial y reserva profesional, comprometiéndose a no transferir, ceder, vender ni comercializar bases de datos a terceros bajo ninguna circunstancia."
    )

    add_heading_styled(doc, "Sección 2.4: Custodia y Responsabilidad sobre las Credenciales", level=2)
    add_paragraph_styled(
        doc,
        "El usuario es el único y exclusivo responsable de la confidencialidad de su nombre de usuario y contraseña (hash seguro cifrado en base de datos mediante algoritmos PBKDF2 / Argon2). Toda acción realizada desde una sesión autenticada se presumirá legalmente ejecutada por el titular o por dependientes debidamente facultados bajo su supervisión."
    )

    add_heading_styled(doc, "Sección 2.5: Veracidad de la Información y Buena Fe Mercantil", level=2)
    add_paragraph_styled(
        doc,
        "El solicitante declara bajo juramento mercantil que los datos suministrados durante el proceso de registro y posterior operación son veraces, completos y actualizados, eximiendo a la plataforma de cualquier daño emergente originado por información fraudulenta, suplantación o balances adulterados."
    )

    add_heading_styled(doc, "Sección 2.6: Exención de Responsabilidad sobre Decisiones Financieras", level=2)
    add_paragraph_styled(
        doc,
        "SmartFinanzas y sus operadores no se hacen responsables de las decisiones financieras, de financiamiento, mercantiles, tributarias o de inversión que adopte la administración o cualquier persona de la empresa usuaria. Se deja constancia expresa de que las métricas de solvencia, semáforos de riesgo, explicabilidad y planes de acción emitidos por el sistema constituyen exclusivamente recomendaciones técnicas y analíticas de soporte orientativo basadas en modelos matemáticos. Conforme a la Ley N° 18.046 (Art. 41 sobre deber de cuidado) y las reglas generales de comercio en Chile, la responsabilidad final, legal y fiduciaria sobre cualquier decisión de negocios recae de manera exclusiva en el Directorio, Administradores y Representantes Legales de la empresa."
    )

    add_callout(
        doc,
        "DESCARGO FINANCIERO CRÍTICO: Los semáforos de riesgo y proyecciones a 90 días no son seguros contra quiebras ni sustituyen el juicio directivo ni las asesorías financieras matriculadas. Ningún resultado emitido por el software podrá fundamentar demandas indemnizatorias contra los desarrolladores de la plataforma.",
        title="CLÁUSULA DE INDEMNIDAD FINANCIERA",
        kind="danger"
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TÍTULO III: TÉRMINOS DE RENDICIÓN Y ARQUEO FÍSICO (POS)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título III: Términos Legales de Rendición de Fondos, Arqueo Físico y Cierre Contable (Módulo POS)", level=1)
    
    add_paragraph_styled(
        doc,
        "Los siguientes términos normativos se aplican a todo acto de cierre diario de caja y arqueo físico efectuado en el Módulo Transaccional:"
    )

    add_heading_styled(doc, "Sección 3.1: Fe de Arqueo y Exactitud Probatoria (Código de Comercio de Chile, Art. 25 al 44)", level=2)
    add_paragraph_styled(
        doc,
        "De acuerdo con el mandato de los artículos 25, 27, 33 y 41 del Código de Comercio chileno y las mejores prácticas contables, los libros y registros deben llevarse en orden cronológico, sin raspaduras, mutilaciones ni alteraciones, reflejando fidedignamente la realidad pecuniaria del negocio. El usuario declara bajo fe y juramento administrativo que el monto reportado en el campo 'Total Efectivo Físico Contado' representa el inventario físico estricto de dinero efectivo al momento exacto del corte de jornada."
    )

    add_heading_styled(doc, "Sección 3.2: Deber de Custodia y Responsabilidad Laboral (Código del Trabajo, Art. 10 N° 7 y Art. 58)", level=2)
    add_paragraph_styled(
        doc,
        "Con arreglo al contrato individual o colectivo de trabajo y a las disposiciones de los artículos 10 y 58 del Código del Trabajo de Chile, el cajero o custodio de fondos asume la obligación de resguardo y administración debida de los dineros confiados. Toda retención, reposición o deducción asociada a pérdidas o descuadres se regirá por los convenios de asignación de pérdida de caja pactados y los límites máximos estipulados por el ordenamiento laboral vigente."
    )

    add_heading_styled(doc, "Sección 3.3: Protocolo Mandatario ante Descuadres (NIA / ISA 240 y Marco COSO)", level=2)
    add_paragraph_styled(
        doc,
        "En aplicación de la Norma Internacional de Auditoría 240 (Responsabilidades del auditor en la auditoría de estados financieros con respecto al fraude) y los componentes de Control de Actividades del Marco COSO:"
    )
    add_bullet_styled(doc, "Ante cualquier diferencia (faltante o sobrante) respecto al saldo calculado por el sistema, es imperativo ingresar una justificación detallada y demostrable (boletas anuladas, vales de caja chica, errores de cambio o fallas en terminales POS bancarios).", "Justificación Obligatoria: ")
    add_bullet_styled(doc, "Los registros quedan sujetos a auditoría de conciliación cruzada con reportes diarios de pasarelas de pago adquirentes (Transbank, Redelcom u otras) y comprobantes de boleta electrónica emitidos ante el Servicio de Impuestos Internos (SII).", "Conciliación Cruzada: ")

    add_heading_styled(doc, "Sección 3.4: Sellado Transaccional e Inmutabilidad de Registros (Código Tributario, Art. 33)", level=2)
    add_paragraph_styled(
        doc,
        "Al presionar 'Confirmar y Cerrar Caja', el sistema ejecutará un sellado atómico e irreversible sobre todas las ventas y retiros de efectivo de la jornada, asignándoles un ID de cierre unívoco y estampilla de tiempo (timestamp). Queda terminantemente bloqueada la alteración retroactiva, eliminación o desvinculación de las operaciones selladas, resguardando la trazabilidad exigida por el Servicio de Impuestos Internos (SII)."
    )

    add_heading_styled(doc, "Sección 3.5: Prohibición de Ocultamiento y Sanciones Disciplinarias", level=2)
    add_paragraph_styled(
        doc,
        "Cualquier simulación, registro malicioso de montos o sustracción de evidencias durante el proceso de arqueo será considerada una infracción grave a las obligaciones laborales y deberes de confianza empresarial, habilitando la apertura de sumarios internos, término de contrato por causales del artículo 160 del Código del Trabajo y las denuncias penales que pudieran proceder por los delitos de apropiación indebida o estafa previstos en el Código Penal chileno."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TÍTULO IV: TÉRMINOS DE INGESTA IFRS Y VALIDACIÓN (ETL)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título IV: Términos de Ingesta, Veracidad Contable y Validación IFRS / CMF (Módulo ETL)", level=1)
    
    add_paragraph_styled(
        doc,
        "Los siguientes términos rigen la subida, procesamiento y almacenamiento de balances financieros dentro del Módulo ETL:"
    )

    add_heading_styled(doc, "Sección 4.1: Marco Normativo IFRS y Criterios Contables", level=2)
    add_paragraph_styled(
        doc,
        "El procesamiento automatizado de estados financieros se fundamenta en los criterios de la Norma Internacional de Contabilidad N° 1 (NIC 1 / IAS 1: Presentación de Estados Financieros), adoptada en Chile por la Comisión para el Mercado Financiero (CMF), requiriendo representación fiel de las transacciones, base contable de acumulación (devengo) y clasificación nítida entre partidas corrientes y no corrientes."
    )

    add_heading_styled(doc, "Sección 4.2: Responsabilidad por la Veracidad del Archivo Origen", level=2)
    add_paragraph_styled(
        doc,
        "Conforme al Artículo 17 y Artículo 97 N° 4 del Código Tributario de Chile y los principios generales de contabilidad mercantil, el usuario y la empresa garantizan que el balance general (.xlsx / .csv) incorporado proviene de los libros oficiales timbrados y respaldos documentales fidedignos. La presentación maliciosa de balances falsos o incompletos acarrea responsabilidad civil y penal exclusiva del emisor."
    )

    add_heading_styled(doc, "Sección 4.3: Ecuación Patrimonial y Consistencia Aritmética", level=2)
    add_paragraph_styled(
        doc,
        "El pipeline ETL efectúa validaciones de integridad estricta (Activo Total = Pasivo Total + Patrimonio Neto con una tolerancia máxima de cuadratura de 5% para diferencias de redondeo), verificación de existencia de partidas esenciales y contención de divisiones por cero. El sistema rechazará balances estructuralmente inválidos."
    )

    add_heading_styled(doc, "Sección 4.4: Deslinde de Responsabilidad del Motor ETL", level=2)
    add_paragraph_styled(
        doc,
        "La validación algorítmica de la plataforma comprueba consistencia matemática de tipos, formatos y fórmulas adimensionales (V1 a V7), pero no reemplaza una auditoría física de inventarios, arqueo pericial de cuentas ni verificación sustantiva de cartera por parte de auditores externos independientes colegiados."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TÍTULO V: DESCARGO Y GOBERNANZA DE IA (DASHBOARD / ML)
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título V: Descargo de Responsabilidad y Términos de Inferencia Predictiva (Dashboard ML / PDF)", level=1)
    
    add_paragraph_styled(
        doc,
        "Los siguientes términos rigen la visualización de métricas en el Dashboard Gerencial, el Módulo de Explicabilidad SHAP y la emisión de reportes ejecutivos descargables en PDF:"
    )

    add_heading_styled(doc, "Sección 5.1: Principios de IA Explicable y Fuentes Normativas", level=2)
    add_paragraph_styled(
        doc,
        "La generación del diagnóstico y las atribuciones de importancia factorial se rigen bajo los Principios de Inteligencia Artificial de la OCDE (OECD Principles on AI, 2019) y las directrices del IEEE Standard 7001 para Transparencia en Sistemas Algorítmicos, garantizando que ninguna decisión se apoye en una 'caja negra' inescrutable, sino en variables cuantitativas auditables (ratios financieros normalizados)."
    )

    add_heading_styled(doc, "Sección 5.2: Naturaleza Probabilística y Límite Predictivo", level=2)
    add_paragraph_styled(
        doc,
        "El Score de Riesgo (0 a 100) y el Semáforo de Insolvencia representan probabilidades estadísticas relativas calibradas sobre muestras históricas de empresas chilenas. En virtud de la Ley N° 21.521 (Ley FinTech de Chile), se deja constancia expresa de que las estimaciones matemáticas no constituyen certeza matemática absoluta sobre el futuro económico de la compañía ni sustituyen contingencias macroeconómicas sobrevinientes (tales como variaciones cambiarias abruptas, crisis de suministro o desastres naturales)."
    )

    add_heading_styled(doc, "Sección 5.3: Exención de Asesoría Financiera y Dictamen Pericial", level=2)
    add_paragraph_styled(
        doc,
        "El informe ejecutivo descargado tiene fines exclusivamente informativos y de gobernanza interna. No constituye asesoría tributaria vinculante, recomendación de inversión en valores ni dictamen pericial judicial ante el Servicio de Impuestos Internos (SII), la Comisión para el Mercado Financiero (CMF) o los tribunales ordinarios de justicia."
    )

    add_heading_styled(doc, "Sección 5.4: Deber de Cuidado y Decisión Fiduciaria de la Administración", level=2)
    add_paragraph_styled(
        doc,
        "Conforme al Artículo 41 de la Ley N° 18.046 sobre Sociedades Anónimas (aplicable por analogía al estándar general de administración mercantil en Chile), la adopción de planes de endeudamiento, recorte de gastos o renegociaciones con acreedores es competencia exclusiva y soberana del Directorio o Representante Legal de la empresa."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TÍTULO VI: PROPIEDAD INTELECTUAL Y LICENCIA DE USO
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título VI: Propiedad Intelectual y Licenciamiento de Software", level=1)
    
    add_heading_styled(doc, "Artículo 4: Titularidad de los Derechos de Autor", level=2)
    add_paragraph_styled(
        doc,
        "Todos los derechos de propiedad intelectual, derechos de autor y derechos conexos sobre el código fuente, diseño gráfico, interfaces de usuario, arquitectura de base de datos, algoritmos de explicabilidad y modelos serializados de Machine Learning (.joblib) son de titularidad exclusiva de SmartFinanzas SpA, encontrándose protegidos por la Ley N° 17.336 sobre Propiedad Intelectual de Chile y los tratados internacionales suscritos por el Estado chileno."
    )

    add_heading_styled(doc, "Artículo 5: Concesión de Licencia Limitada y Prohibiciones", level=2)
    add_paragraph_styled(
        doc,
        "SmartFinanzas concede a La Empresa una licencia de uso no exclusiva, intransferible, revocable y limitada estrictamente a la gestión interna de sus operaciones comerciales. Queda terminantemente prohibido:"
    )
    add_bullet_styled(doc, "Descompilar, realizar ingeniería inversa o desensamblar cualquier componente del software o de los modelos de Machine Learning.", "Ingeniería Inversa: ")
    add_bullet_styled(doc, "Vender, sublicenciar, arrendar o transferir el acceso a terceros ajenos a la organización titular.", "Cesión no Autorizada: ")
    add_bullet_styled(doc, "Utilizar robots, scrapers o mecanismos automatizados para extraer masivamente datos o replicar la interfaz.", "Extracción Automatizada: ")

    # -------------------------------------------------------------
    # TÍTULO VII: PROTOCOLO DE SEGURIDAD Y AUDITORÍA
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título VII: Protocolo de Seguridad, Criptografía y Auditoría", level=1)
    
    add_paragraph_styled(
        doc,
        "En resguardo de la confidencialidad exigida por la Ley N° 19.628 y las directrices de seguridad de la Ley N° 21.459 sobre Delitos Informáticos, La Plataforma implementa las siguientes medidas de control técnico:"
    )
    add_bullet_styled(doc, "Las contraseñas de usuario nunca se almacenan en texto plano; son procesadas mediante funciones de derivación de claves criptográficamente seguras con sal (salt) aleatoria.", "Criptografía de Credenciales: ")
    add_bullet_styled(doc, "Cada consulta a la base de datos incorpora filtros obligatorios por el identificador de la empresa (company_id), haciendo imposible que un usuario consulte información perteneciente a otra organización.", "Aislamiento Relacional: ")
    add_bullet_styled(doc, "Cada cierre de caja, venta y carga de balance registra el identificador de usuario, dirección IP de origen y marca temporal precisa para auditorías forenses.", "Pistas de Auditoría Inmutables: ")

    # -------------------------------------------------------------
    # TÍTULO VIII: VIGENCIA, MODIFICACIONES Y JURISDICCIÓN
    # -------------------------------------------------------------
    add_heading_styled(doc, "Título VIII: Vigencia, Modificaciones y Jurisdicción Aplicable", level=1)
    
    add_heading_styled(doc, "Artículo 6: Modificación de los Términos", level=2)
    add_paragraph_styled(
        doc,
        "SmartFinanzas se reserva la facultad de actualizar o modificar los presentes términos y condiciones para adecuarlos a nuevas exigencias legislativas (modificaciones de la CMF, SII o normativa laboral) o mejoras funcionales del software. Toda modificación sustantiva será notificada en la plataforma, requiriendo una nueva confirmación al ingresar."
    )

    add_heading_styled(doc, "Artículo 7: Domicilio y Jurisdicción", level=2)
    add_paragraph_styled(
        doc,
        "Para todos los efectos legales derivados de este contrato, las partes fijan su domicilio en la ciudad de Santiago de Chile y se someten a la competencia y jurisdicción de sus Tribunales Ordinarios de Justicia, renunciando a cualquier otro fuero que pudiera corresponderles."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_callout(
        doc,
        "CONSTANCIA DE INTEGRIDAD: El presente compendio consolida y unifica formalmente los textos legales, modales de advertencia y compromisos contractuales vigentes en el código fuente de SmartFinanzas.",
        title="DOCUMENTO LEGAL CONSOLIDADO",
        kind="succ"
    )

    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Terminos_y_Condiciones_SmartFinanzas.docx")
    doc.save(output_path)
    print(f"Documento de Términos y Condiciones generado con éxito en: {output_path}")
    print(f"Tamaño final del archivo: {os.path.getsize(output_path):,} bytes")

if __name__ == "__main__":
    build_terms_document()
