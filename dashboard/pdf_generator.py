"""
Generador de Informes Ejecutivos en PDF con ReportLab.
SmartFinanzas - Capa de Presentación Gerencial y Diagnóstico Formal de Riesgo.
"""

import io
from decimal import Decimal
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Lienzo de ReportLab que efectúa dos pasadas para calcular dinámicamente
    el número total de páginas e imprimir encabezados y pies de página formales.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.empresa_nombre = "SmartFinanzas"
        self.titulo_header = "SMARTFINANZAS · Informe Ejecutivo de Riesgo y Diagnóstico Financiero"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#64748b'))

        # Encabezado formal visible a partir de la página 2
        if self._pageNumber > 1:
            tit_header = getattr(self, 'titulo_header', "SMARTFINANZAS · Informe Ejecutivo")
            self.drawString(36, 756, tit_header)
            self.drawRightString(576, 756, str(self.empresa_nombre))
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)

        # Pie de página formal en todas las páginas
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(36, 42, 576, 42)
        self.drawString(36, 30, "Documento Confidencial · Uso Interno Gerencial · Capa Analítica ML SmartFinanzas")
        self.drawRightString(576, 30, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def construir_informe_ejecutivo_pdf(
    empresa,
    ultima_prediccion,
    top_3_variables=None,
    ingreso_real_hoy=0,
    usuario=None,
    total_ventas_hoy=0,
    todos_los_ratios=None,
    ratio_asociado=None,
    info_periodo=None,
    historico_puntos=None,
    **kwargs,
):
    """
    Construye y devuelve un archivo PDF en memoria (BytesIO) con el diagnóstico
    ejecutivo estructurado y formal de SmartFinanzas, incluyendo:
    - Diagnóstico de Semáforo de Riesgo y Probabilidad
    - Explicabilidad Algorítmica SHAP Completa
    - Trazabilidad Integral de Ratios Financieros
    - Información Contable del Período (Balance y Estado de Resultados)
    - Evolución Histórica / Tendencia de Solvencia
    - Resumen Operativo de Flujo de Caja
    - Plan de Acción y Recomendaciones Estratégicas
    """
    buffer = io.BytesIO()

    # Documento tamaño Carta (612 x 792 pt), márgenes de 36 pt (ancho útil = 540 pt)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Paleta de Colores Corporativos Formales
    C_PRIMARIO = colors.HexColor('#0f172a')     # Slate 900
    C_SECUNDARIO = colors.HexColor('#334155')   # Slate 700
    C_MUTED = colors.HexColor('#64748b')        # Slate 500
    C_BORDE = colors.HexColor('#cbd5e1')        # Slate 300
    C_BORDE_LIGHT = colors.HexColor('#e2e8f0')  # Slate 200
    C_FONDO_CLARO = colors.HexColor('#f8fafc')  # Slate 50
    C_FONDO_ALT = colors.HexColor('#f1f5f9')    # Slate 100
    C_AZUL = colors.HexColor('#1d4ed8')         # Blue 700
    C_AZUL_FONDO = colors.HexColor('#eff6ff')   # Blue 50
    C_VERDE = colors.HexColor('#15803d')        # Green 700
    C_VERDE_FONDO = colors.HexColor('#f0fdf4')  # Green 50
    C_AMARILLO = colors.HexColor('#b45309')     # Amber 700
    C_AMARILLO_FONDO = colors.HexColor('#fefce8') # Amber 50
    C_ROJO = colors.HexColor('#b91c1c')         # Red 700
    C_ROJO_FONDO = colors.HexColor('#fef2f2')   # Red 50

    # Estilos Tipográficos
    estilo_banner_sup = ParagraphStyle(
        'BannerSup', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=C_AZUL,
        textTransform='uppercase', spaceAfter=3
    )
    estilo_titulo = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=C_PRIMARIO
    )
    estilo_subtitulo = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12, textColor=C_MUTED
    )
    estilo_meta_header = ParagraphStyle(
        'MetaHeader', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_SECUNDARIO, alignment=2
    )
    estilo_seccion = ParagraphStyle(
        'SectionHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=C_PRIMARIO,
        spaceBefore=10, spaceAfter=5
    )
    estilo_texto = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12, textColor=C_SECUNDARIO
    )
    estilo_texto_muted = ParagraphStyle(
        'BodyMuted', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_MUTED
    )
    estilo_tabla_head = ParagraphStyle(
        'TableHead', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=colors.white
    )
    estilo_tabla_celda = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_SECUNDARIO
    )
    estilo_tabla_celda_bold = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=C_PRIMARIO
    )
    estilo_tabla_celda_center = ParagraphStyle(
        'TableCellCenter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_SECUNDARIO, alignment=1
    )
    estilo_tabla_celda_right = ParagraphStyle(
        'TableCellRight', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_SECUNDARIO, alignment=2
    )

    elementos = []

    # =========================================================================
    # ENCABEZADO FORMAL Y PORTADA
    # =========================================================================
    fecha_emision = timezone.localtime().strftime('%d/%m/%Y %H:%M')
    nombre_empresa = empresa.business_name if empresa else "Empresa Sin Asignar"
    rut_empresa = empresa.tax_id if (empresa and empresa.tax_id) else "Sin RUT"
    usuario_nombre = usuario.username if usuario else "Auditoría Financiera"
    rol_nombre = (
        getattr(getattr(usuario, 'profile', None), 'role', None)
        or getattr(getattr(usuario, 'role', None), 'name', None)
        or "Usuario Operador"
    )

    periodo_texto = "Período Vigente"
    if ultima_prediccion and ultima_prediccion.ratio and ultima_prediccion.ratio.period:
        periodo_texto = ultima_prediccion.ratio.period
    elif info_periodo and info_periodo.get('periodo'):
        periodo_texto = info_periodo.get('periodo')

    data_header = [
        [
            Paragraph("SMARTFINANZAS &middot; PLATAFORMA DE INTELIGENCIA FINANCIERA", estilo_banner_sup),
            Paragraph(f"<b>Fecha de Emisión:</b> {fecha_emision}", estilo_meta_header),
        ],
        [
            Paragraph("<b>INFORME EJECUTIVO DE RIESGO DE INSOLVENCIA</b>", estilo_titulo),
            Paragraph(f"<b>Período Evaluado:</b> <font color='#1d4ed8'><b>{periodo_texto}</b></font>", estilo_meta_header),
        ],
        [
            Paragraph("Diagnóstico Predictivo de Solvencia, Explicabilidad Algorítmica SHAP y Auditoría Contable", estilo_subtitulo),
            Paragraph(f"<b>Emisor:</b> {usuario_nombre} ({rol_nombre})", estilo_meta_header),
        ]
    ]
    t_header = Table(data_header, colWidths=[360, 180])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(t_header)
    elementos.append(Spacer(1, 6))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=C_PRIMARIO, spaceAfter=8))

    # Cuadro de Metadatos de la Empresa y del Modelo
    fecha_pred_str = ultima_prediccion.prediction_date.strftime('%d/%m/%Y %H:%M') if (ultima_prediccion and ultima_prediccion.prediction_date) else "N/A"
    pred_id_str = f"#{ultima_prediccion.id}" if ultima_prediccion else "N/A"

    meta_table_data = [
        [
            Paragraph(f"<b>Razón Social:</b> {nombre_empresa}", estilo_tabla_celda),
            Paragraph(f"<b>RUT Empresa:</b> {rut_empresa}", estilo_tabla_celda),
            Paragraph(f"<b>Inferencia ID:</b> {pred_id_str}", estilo_tabla_celda),
            Paragraph(f"<b>Fecha Análisis:</b> {fecha_pred_str}", estilo_tabla_celda),
        ],
        [
            Paragraph("<b>Modelo ML:</b> Random Forest Classifier", estilo_tabla_celda),
            Paragraph("<b>Explicabilidad:</b> SHAP TreeExplainer", estilo_tabla_celda),
            Paragraph(f"<b>Período Contable:</b> {periodo_texto}", estilo_tabla_celda),
            Paragraph("<b>Normativa:</b> Estándar IFRS", estilo_tabla_celda),
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[160, 120, 110, 150])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(t_meta)
    elementos.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 1: DIAGNÓSTICO DEL SEMÁFORO DE RIESGO
    # =========================================================================
    score_val = float(ultima_prediccion.risk_score) if (ultima_prediccion and ultima_prediccion.risk_score is not None) else 0.0
    nivel_val = ultima_prediccion.traffic_light_level if ultima_prediccion else "Sin Datos"
    prob_insolvencia = score_val
    prob_solvencia = max(0.0, 100.0 - score_val)

    if nivel_val == 'Rojo' or score_val > 70.0:
        c_semaforo = C_ROJO
        c_fondo_sem = C_ROJO_FONDO
        titulo_semaforo = "CRÍTICO &middot; ALTO RIESGO DE INSOLVENCIA"
        diag_semaforo = (
            "La compañía se encuentra en el rango de alerta crítica. La probabilidad estimada de insolvencia "
            f"es del <b>{prob_insolvencia:.1f}%</b>, superando el umbral de seguridad técnica del 70%. Las obligaciones a corto "
            "plazo exceden la capacidad de generación operativa y liquidez disponible. Se aconseja activar "
            "de forma urgente el plan de contingencia de tesorería y reestructuración de pasivos."
        )
    elif nivel_val == 'Amarillo' or score_val > 35.0:
        c_semaforo = C_AMARILLO
        c_fondo_sem = C_AMARILLO_FONDO
        titulo_semaforo = "MODERADO &middot; ALERTA PREVENTIVA DE LIQUIDEZ"
        diag_semaforo = (
            f"La compañía presenta un nivel de riesgo moderado (Score: <b>{score_val:.1f}/100</b>, probabilidad de insolvencia del <b>{prob_insolvencia:.1f}%</b>). "
            "Se detectan tensiones puntuales en los índices de liquidez o apalancamiento que requieren seguimiento riguroso. "
            "Se recomienda reforzar la cobranza de cuentas por cobrar y controlar el crecimiento de pasivos circulantes."
        )
    else:
        c_semaforo = C_VERDE
        c_fondo_sem = C_VERDE_FONDO
        titulo_semaforo = "BAJO &middot; CONDICIÓN FINANCIERA SOLVENTE"
        diag_semaforo = (
            f"La compañía exhibe una condición patrimonial sólida (Score: <b>{score_val:.1f}/100</b>, probabilidad de solvencia estimada del <b>{prob_solvencia:.1f}%</b>). "
            "La cobertura de pasivos corrientes mediante activos líquidos y la generación operativa respaldan adecuadamente "
            "el cumplimiento de compromisos financieros inmediatos."
        )

    elementos.append(Paragraph("1. Diagnóstico Ejecutivo del Nivel de Riesgo (Semáforo)", estilo_seccion))

    estilo_score_grande = ParagraphStyle(
        'ScoreBig', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=28, leading=30, textColor=c_semaforo, alignment=1
    )
    estilo_semaforo_badge = ParagraphStyle(
        'SemBadge', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=c_semaforo, alignment=1
    )

    data_semaforo = [
        [
            Paragraph(f"SCORE DE RIESGO<br/><b>{score_val:.1f}</b><font size='14'> / 100</font>", estilo_score_grande),
            Paragraph(
                f"<font size='9.5' color='{c_semaforo.hexval()}'><b>{titulo_semaforo}</b></font><br/><br/>"
                f"{diag_semaforo}<br/><br/>"
                f"<b>Probabilidad Insolvencia:</b> {prob_insolvencia:.1f}% &nbsp;|&nbsp; "
                f"<b>Probabilidad Solvencia:</b> {prob_solvencia:.1f}% &nbsp;|&nbsp; "
                f"<b>Fecha de Cálculo:</b> {fecha_pred_str}",
                estilo_texto
            )
        ]
    ]
    t_sem = Table(data_semaforo, colWidths=[150, 390])
    t_sem.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_fondo_sem),
        ('BOX', (0, 0), (-1, -1), 1, c_semaforo),
        ('LINEAFTER', (0, 0), (0, 0), 1, C_BORDE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(t_sem)
    elementos.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 2: EXPLICABILIDAD SHAP DE LA PREDICCIÓN (MATRIZ COMPLETA)
    # =========================================================================
    elementos.append(Paragraph("2. Explicabilidad SHAP del Diagnóstico (Factores Clave de Decisión)", estilo_seccion))
    elementos.append(Paragraph(
        "A continuación se presenta el desglose matemático cuantitativo generado por el explicador SHAP (TreeExplainer). "
        "Cada indicador refleja el grado en que empujó la probabilidad final hacia un mayor riesgo (+) o hacia una mayor solvencia (-):",
        estilo_texto_muted
    ))
    elementos.append(Spacer(1, 5))

    filas_shap = [
        [
            Paragraph("Factor / Indicador", estilo_tabla_head),
            Paragraph("Grupo", estilo_tabla_head),
            Paragraph("Valor", estilo_tabla_head),
            Paragraph("Impacto SHAP", estilo_tabla_head),
            Paragraph("Efecto en Riesgo", estilo_tabla_head),
            Paragraph("Diagnóstico Interpretativo del Factor", estilo_tabla_head),
        ]
    ]

    ratios_list = todos_los_ratios or top_3_variables or []
    if ratios_list:
        # Ordenar por impacto absoluto descendente
        try:
            ratios_ordenados = sorted(
                ratios_list,
                key=lambda x: abs(float(x.get('impacto_pct', x.get('impacto', x.get('impacto_shap', 0.0))) or 0.0)),
                reverse=True
            )
        except Exception:
            ratios_ordenados = ratios_list

        for r in ratios_ordenados:
            cod = r.get('codigo', '')
            nom = r.get('nombre', r.get('variable', 'Variable'))
            grp = r.get('grupo', 'Financiero')
            val = float(r.get('valor', 0.0) or 0.0)
            unidad = r.get('unidad', '')
            impacto = float(r.get('impacto_pct', r.get('impacto', 0.0)) or 0.0)
            aumenta = r.get('aumenta_riesgo', impacto >= 0)
            diag_txt = r.get('texto', r.get('texto_resumen', 'Sin diagnóstico específico'))

            signo = "+" if impacto >= 0 else ""
            color_imp = "#b91c1c" if aumenta else "#15803d"
            texto_efecto = "Aumenta Riesgo" if aumenta else "Reduce Riesgo"

            filas_shap.append([
                Paragraph(f"<b>{cod}: {nom}</b>", estilo_tabla_celda_bold),
                Paragraph(grp, estilo_tabla_celda),
                Paragraph(f"{val:.2f}{unidad}", estilo_tabla_celda_center),
                Paragraph(f"<font color='{color_imp}'><b>{signo}{impacto:.1f}%</b></font>", estilo_tabla_celda_center),
                Paragraph(f"<font color='{color_imp}'><b>{texto_efecto}</b></font>", estilo_tabla_celda_center),
                Paragraph(diag_txt, estilo_tabla_celda),
            ])
    else:
        filas_shap.append([
            Paragraph("No se registraron variables SHAP calculadas", estilo_tabla_celda),
            Paragraph("-", estilo_tabla_celda_center),
            Paragraph("-", estilo_tabla_celda_center),
            Paragraph("-", estilo_tabla_celda_center),
            Paragraph("-", estilo_tabla_celda_center),
            Paragraph("Ejecute un análisis desde el módulo predictivo para procesar la explicabilidad.", estilo_tabla_celda),
        ])

    t_shap = Table(filas_shap, colWidths=[120, 65, 55, 65, 80, 155])
    t_shap.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARIO),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_FONDO_CLARO]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elementos.append(t_shap)
    elementos.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 3: TRAZABILIDAD INTEGRAL - RATIOS FINANCIEROS DE LA PREDICCIÓN
    # =========================================================================
    elementos.append(Paragraph("3. Trazabilidad Integral: Matriz de Ratios Financieros de la Inferencia", estilo_seccion))
    elementos.append(Paragraph(
        "Indicadores cuantitativos calculados sobre los estados financieros oficiales para el período evaluado:",
        estilo_texto_muted
    ))
    elementos.append(Spacer(1, 5))

    # Ratios de referencia Z-Altman y Prueba Ácida
    val_z = getattr(ratio_asociado, 'ref_altman_z_score', None)
    val_z_float = float(val_z) if val_z is not None else None

    val_pa = getattr(ratio_asociado, 'ref_quick_ratio', None)
    val_pa_float = float(val_pa) if val_pa is not None else None

    # Mapeo de reglas para evaluar el estado cualitativo de cada ratio
    def evaluar_ratio(cod, val):
        if val is None:
            return ("Sin Datos", C_MUTED)
        if cod == 'X1':
            return ("Óptimo", C_VERDE) if val >= 1.5 else (("Aceptable", C_AMARILLO) if val >= 1.0 else ("Baja Liquidez", C_ROJO))
        elif cod == 'X2':
            return ("Sólido", C_VERDE) if val >= 0.15 else (("Equilibrado", C_AMARILLO) if val >= 0.0 else ("Capital Negativo", C_ROJO))
        elif cod == 'X3':
            return ("Controlado", C_VERDE) if val <= 1.0 else (("Moderado", C_AMARILLO) if val <= 2.5 else ("Alto Apalancamiento", C_ROJO))
        elif cod == 'X4':
            return ("Rentable", C_VERDE) if val >= 0.08 else (("Aceptable", C_AMARILLO) if val >= 0.02 else ("Bajo Retorno", C_ROJO))
        elif cod == 'X5':
            return ("Margen Fuerte", C_VERDE) if val >= 0.12 else (("Margen Medio", C_AMARILLO) if val >= 0.04 else ("Margen Débil", C_ROJO))
        elif cod == 'X6':
            return ("Alta Eficiencia", C_VERDE) if val >= 1.2 else (("Media", C_AMARILLO) if val >= 0.7 else ("Baja Rotación", C_ROJO))
        elif cod == 'X7':
            return ("Estable", C_VERDE) if val <= 0.3 else (("Moderado", C_AMARILLO) if val <= 0.6 else ("Alta Volatilidad", C_ROJO))
        return ("Calculado", C_AZUL)

    filas_ratios = [
        [
            Paragraph("Ratio / Indicador", estilo_tabla_head),
            Paragraph("Fórmula Contable Aplicada", estilo_tabla_head),
            Paragraph("Valor Calculado", estilo_tabla_head),
            Paragraph("Meta / Referencia", estilo_tabla_head),
            Paragraph("Evaluación", estilo_tabla_head),
        ]
    ]

    # Diccionario de fórmulas y metas estándar
    METAS_FORMULAS = {
        'X1': ('Activo Corriente / Pasivo Corriente', '&ge; 1.50x'),
        'X2': ('Capital de Trabajo / Activo Total', '&gt; 0.00%'),
        'X3': ('Pasivo Total / Patrimonio Neto', '&lt; 1.00x'),
        'X4': ('EBIT / Activo Total (ROA Operacional)', '&gt; 5.00%'),
        'X5': ('EBIT / Ventas Netas (Margen Operativo)', '&gt; 10.00%'),
        'X6': ('Ventas Netas / Activo Total (Rotación)', '&gt; 1.00x'),
        'X7': ('Desviación Flujo Diario / Flujo Medio', 'Baja Dispersión'),
    }

    if todos_los_ratios:
        for r in todos_los_ratios:
            cod = r.get('codigo', '')
            nom = r.get('nombre', 'Ratio')
            val = float(r.get('valor', 0.0) or 0.0)
            unidad = r.get('unidad', '')
            formula_txt, meta_txt = METAS_FORMULAS.get(cod, (r.get('formula', '-'), r.get('meta', '-')))
            estado_lbl, color_est = evaluar_ratio(cod, val)

            filas_ratios.append([
                Paragraph(f"<b>{cod}: {nom}</b>", estilo_tabla_celda_bold),
                Paragraph(formula_txt, estilo_tabla_celda),
                Paragraph(f"<b>{val:.2f}{unidad}</b>", estilo_tabla_celda_center),
                Paragraph(meta_txt, estilo_tabla_celda_center),
                Paragraph(f"<font color='{color_est.hexval()}'><b>{estado_lbl}</b></font>", estilo_tabla_celda_center),
            ])

    # Fila Altman Z''-Score si está disponible
    if val_z_float is not None:
        if val_z_float >= 2.60:
            lbl_z, col_z = ("Zona Segura", C_VERDE)
        elif val_z_float >= 1.10:
            lbl_z, col_z = ("Zona Gris", C_AMARILLO)
        else:
            lbl_z, col_z = ("Zona de Quiebra", C_ROJO)

        filas_ratios.append([
            Paragraph("<b>Z''EM: Altman Mercados Emergentes</b>", estilo_tabla_celda_bold),
            Paragraph("6.56*X2 + 3.26*X4 + 6.72*X5 + 1.05*X3_inv", estilo_tabla_celda),
            Paragraph(f"<b>{val_z_float:.2f}</b>", estilo_tabla_celda_center),
            Paragraph("&gt; 2.60 (Segura)", estilo_tabla_celda_center),
            Paragraph(f"<font color='{col_z.hexval()}'><b>{lbl_z}</b></font>", estilo_tabla_celda_center),
        ])

    # Fila Prueba Ácida si está disponible
    if val_pa_float is not None:
        if val_pa_float >= 1.0:
            lbl_pa, col_pa = ("Óptima", C_VERDE)
        elif val_pa_float >= 0.7:
            lbl_pa, col_pa = ("Aceptable", C_AMARILLO)
        else:
            lbl_pa, col_pa = ("Baja Cobertura", C_ROJO)

        filas_ratios.append([
            Paragraph("<b>Prueba Ácida (Quick Ratio)</b>", estilo_tabla_celda_bold),
            Paragraph("(Activo Corriente - Inventarios) / Pasivo Corriente", estilo_tabla_celda),
            Paragraph(f"<b>{val_pa_float:.2f}x</b>", estilo_tabla_celda_center),
            Paragraph("&ge; 1.00x", estilo_tabla_celda_center),
            Paragraph(f"<font color='{col_pa.hexval()}'><b>{lbl_pa}</b></font>", estilo_tabla_celda_center),
        ])

    t_ratios = Table(filas_ratios, colWidths=[130, 160, 80, 85, 85])
    t_ratios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARIO),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_FONDO_CLARO]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_ratios)
    elementos.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 4: INFORMACIÓN CONTABLE AUDITABLE DEL PERÍODO (BALANCE & RESULTADOS)
    # =========================================================================
    if info_periodo:
        elementos.append(Paragraph("4. Información Contable Oficial del Período (Balance & Resultados)", estilo_seccion))
        elementos.append(Paragraph(
            "Cifras contables consolidadas ingresadas y validadas mediante el pipeline de extracción ETL:",
            estilo_texto_muted
        ))
        elementos.append(Spacer(1, 5))

        act_tot = info_periodo.get('activo_total', 0)
        pas_tot = info_periodo.get('pasivo_total', 0)
        patrim = info_periodo.get('patrimonio', 0)
        act_cte = info_periodo.get('activo_corriente', 0)
        pas_cte = info_periodo.get('pasivo_corriente', 0)
        cap_trab = info_periodo.get('capital_trabajo', 0)
        ingresos = info_periodo.get('ingresos_netos', 0)
        ebit = info_periodo.get('ebit', 0)
        util_neta = info_periodo.get('utilidad_neta', 0)
        inventarios = info_periodo.get('inventarios', 0)
        efectivo = info_periodo.get('efectivo_equivalentes', 0)
        archivo_orig = info_periodo.get('archivo_origen', 'Carga Contable')
        fecha_carga_orig = info_periodo.get('fecha_carga')
        fecha_carga_str = fecha_carga_orig.strftime('%d/%m/%Y %H:%M') if fecha_carga_orig else 'N/A'

        cuadre_ok = info_periodo.get('cuadrado', True)
        texto_cuadre = "<font color='#15803d'><b>Ecuación Cuadrada (Activo = Pasivo + Patrimonio)</b></font>" if cuadre_ok else "<font color='#b91c1c'><b>Diferencia detectada en balance</b></font>"

        data_balance = [
            [
                Paragraph("<b>Activo Total:</b>", estilo_tabla_celda_bold),
                Paragraph(f"${act_tot:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>Ingresos por Ventas:</b>", estilo_tabla_celda_bold),
                Paragraph(f"${ingresos:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Pasivo Total:</b>", estilo_tabla_celda_bold),
                Paragraph(f"${pas_tot:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>EBIT (Resultado Operacional):</b>", estilo_tabla_celda_bold),
                Paragraph(f"${ebit:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Patrimonio Neto:</b>", estilo_tabla_celda_bold),
                Paragraph(f"${patrim:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>Utilidad Neta del Ejercicio:</b>", estilo_tabla_celda_bold),
                Paragraph(f"${util_neta:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Activo Corriente (Circulante):</b>", estilo_tabla_celda),
                Paragraph(f"${act_cte:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>Margen EBIT (%):</b>", estilo_tabla_celda),
                Paragraph(f"{info_periodo.get('margen_ebit_pct', 0):.1f}%", estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Pasivo Corriente (Circulante):</b>", estilo_tabla_celda),
                Paragraph(f"${pas_cte:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>Margen Neto (%):</b>", estilo_tabla_celda),
                Paragraph(f"{info_periodo.get('margen_neto_pct', 0):.1f}%", estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Capital de Trabajo Neto:</b>", estilo_tabla_celda),
                Paragraph(f"${cap_trab:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>Inventarios Registrados:</b>", estilo_tabla_celda),
                Paragraph(f"${inventarios:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Efectivo y Equivalentes:</b>", estilo_tabla_celda),
                Paragraph(f"${efectivo:,.0f}".replace(',', '.'), estilo_tabla_celda_right),
                Paragraph("<b>Endeudamiento sobre Activos:</b>", estilo_tabla_celda),
                Paragraph(f"{info_periodo.get('ratio_endeudamiento', 0):.1f}%", estilo_tabla_celda_right),
            ],
            [
                Paragraph(f"<b>Validación Contable:</b> {texto_cuadre}", estilo_tabla_celda),
                Paragraph("", estilo_tabla_celda),
                Paragraph(f"<b>Archivo Origen:</b> {archivo_orig} ({fecha_carga_str})", estilo_tabla_celda),
                Paragraph("", estilo_tabla_celda),
            ]
        ]
        t_bal = Table(data_balance, colWidths=[150, 120, 150, 120])
        t_bal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
            ('GRID', (0, 0), (-1, -2), 0.5, C_BORDE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
            ('SPAN', (0, -1), (1, -1)),
            ('SPAN', (2, -1), (3, -1)),
            ('BACKGROUND', (0, -1), (-1, -1), C_FONDO_ALT),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elementos.append(t_bal)
        elementos.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 5: EVOLUCIÓN HISTÓRICA / CURVA DE SOLVENCIA
    # =========================================================================
    if historico_puntos and len(historico_puntos) > 1:
        elementos.append(Paragraph("5. Evolución Histórica de Solvencia & Tendencia de Riesgo", estilo_seccion))
        elementos.append(Paragraph(
            "Trayectoria cronológica de los últimos períodos evaluados por el motor predictivo de la empresa:",
            estilo_texto_muted
        ))
        elementos.append(Spacer(1, 5))

        filas_hist = [
            [
                Paragraph("Período Contable", estilo_tabla_head),
                Paragraph("Fecha Inferencia", estilo_tabla_head),
                Paragraph("Score de Riesgo", estilo_tabla_head),
                Paragraph("Clasificación", estilo_tabla_head),
                Paragraph("Estado en Informe", estilo_tabla_head),
            ]
        ]

        for p in historico_puntos:
            score_p = float(p.get('score', 0))
            nivel_p = p.get('nivel', 'Verde')
            color_p = C_ROJO if nivel_p == 'Rojo' else (C_AMARILLO if nivel_p == 'Amarillo' else C_VERDE)
            es_act = p.get('es_actual', False)
            marcador_txt = "<font color='#1d4ed8'><b>&bull; PERÍODO ACTUAL</b></font>" if es_act else "Histórico"

            filas_hist.append([
                Paragraph(f"<b>{p.get('periodo', '-')}</b>", estilo_tabla_celda_bold),
                Paragraph(str(p.get('fecha', '-')), estilo_tabla_celda),
                Paragraph(f"<b>{score_p:.1f}</b> / 100", estilo_tabla_celda_center),
                Paragraph(f"<font color='{color_p.hexval()}'><b>{nivel_p.upper()}</b></font>", estilo_tabla_celda_center),
                Paragraph(marcador_txt, estilo_tabla_celda_center),
            ])

        t_hist = Table(filas_hist, colWidths=[120, 130, 95, 95, 100])
        t_hist.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARIO),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_FONDO_CLARO]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(t_hist)
        elementos.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 6: RESUMEN OPERATIVO TRANSACCIONAL DEL DÍA (FLUJO DE VENTAS)
    # =========================================================================
    elementos.append(Paragraph("6. Resumen Operativo de Transacciones y Caja Diaria", estilo_seccion))
    ingreso_fmt = f"${Decimal(ingreso_real_hoy):,.0f}".replace(',', '.')
    fecha_hoy_str = timezone.localdate().strftime('%d/%m/%Y')

    data_operativa = [
        [
            Paragraph("<b>Ingreso Real Ventas (Hoy):</b>", estilo_tabla_celda_bold),
            Paragraph(f"<font size='9' color='#0f172a'><b>{ingreso_fmt}</b></font>", estilo_tabla_celda),
            Paragraph("<b>Operaciones Registradas:</b>", estilo_tabla_celda_bold),
            Paragraph(f"{total_ventas_hoy} transacción(es)", estilo_tabla_celda),
        ],
        [
            Paragraph("<b>Fecha Contable:</b>", estilo_tabla_celda_bold),
            Paragraph(fecha_hoy_str, estilo_tabla_celda),
            Paragraph("<b>Monitoreo de Flujo:</b>", estilo_tabla_celda_bold),
            Paragraph("Cuadratura operativa activa", estilo_tabla_celda),
        ]
    ]
    t_operativa = Table(data_operativa, colWidths=[140, 130, 140, 130])
    t_operativa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(t_operativa)
    elementos.append(Spacer(1, 12))

    # =========================================================================
    # SECCIÓN 7: PLAN ESTRATÉGICO Y RECOMENDACIONES GERENCIALES
    # =========================================================================
    elementos.append(Paragraph("7. Plan de Acción y Recomendaciones Estratégicas Priorizadas", estilo_seccion))

    if nivel_val == 'Rojo' or score_val > 70.0:
        recomendaciones_bloque = [
            ("1. Preservación Inmediata de Liquidez:", "Suspender de manera inmediata inversiones en activos fijos no productivos y gastos de capital (CAPEX) discrecionales. Priorizar el cumplimiento de obligaciones laborales y fiscales."),
            ("2. Reestructuración de Pasivos de Corto Plazo:", "Iniciar negociación inmediata con acreedores y proveedores críticos para reprogramar vencimientos de corto a mediano plazo, reduciendo la presión sobre la caja operativa."),
            ("3. Aceleración de Cobranzas y Rotación:", "Ofrecer planes de pronto pago con descuentos financieros a clientes vigentes para monetizar rápidamente la cartera de cuentas por cobrar."),
            ("4. Auditoría y Control Diario:", "Exigir conciliación y cierre de caja diario estricto para monitorear desviaciones de flujo de efectivo en tiempo real.")
        ]
    elif nivel_val == 'Amarillo' or score_val > 35.0:
        recomendaciones_bloque = [
            ("1. Monitoreo de Eficiencia Operativa:", "Revisar los márgenes de contribución por línea de negocio para identificar productos o servicios con rentabilidad comprimida y recortar sobrecostos."),
            ("2. Fortalecimiento del Fondo de Reserva:", "Destinar un porcentaje mensual obligatorio del flujo operativo a reservas de contingencia de liquidez equivalente a al menos 30 días de operación."),
            ("3. Política de Crédito Comercial:", "Ajustar los plazos máximos de crédito otorgados a clientes a un máximo de 30 días, evitando concentración crediticia en clientes con historial moroso."),
            ("4. Optimización de Inventarios:", "Liquidar inventario de baja rotación para liberar capital de trabajo inmovilizado.")
        ]
    else:
        recomendaciones_bloque = [
            ("1. Consolidación de Estructura de Capital:", "Aprovechar la sólida solvencia patrimonial para negociar mejores condiciones de financiamiento con tasas preferenciales para proyectos de expansión."),
            ("2. Inversión en Productividad:", "Evaluar reinversión de excedentes en modernización operativa y tecnología que mejore la rotación de activos y la eficiencia comercial."),
            ("3. Rentabilización de Excedentes de Caja:", "Gestionar los saldos ociosos de tesorería en instrumentos de renta fija de alta liquidez y bajo riesgo para generar retornos financieros adicionales."),
            ("4. Mantenimiento Preventivo de Ratios:", "Preservar la razón corriente por encima de 1.50x y un apalancamiento inferior a 1.00x para resguardar la resiliencia ante contingencias del mercado.")
        ]

    filas_rec = []
    for titulo_rec, desc_rec in recomendaciones_bloque:
        filas_rec.append([
            Paragraph(f"<b>{titulo_rec}</b>", estilo_tabla_celda_bold),
            Paragraph(desc_rec, estilo_tabla_celda),
        ])

    t_rec = Table(filas_rec, colWidths=[160, 380])
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elementos.append(t_rec)
    elementos.append(Spacer(1, 16))

    # =========================================================================
    # SECCIÓN 8: CERTIFICACIÓN, FIRMAS Y AVISO LEGAL
    # =========================================================================
    data_firmas = [
        [
            Paragraph("________________________________________<br/><b>Responsable de Auditoría / Analista</b><br/>" + usuario_nombre, estilo_tabla_celda_center),
            Paragraph("", estilo_tabla_celda),
            Paragraph("________________________________________<br/><b>Gerencia General / Representante Legal</b><br/>" + nombre_empresa, estilo_tabla_celda_center),
        ]
    ]
    t_firmas = Table(data_firmas, colWidths=[240, 60, 240])
    t_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(KeepTogether([
        t_firmas,
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=0.8, color=C_BORDE, spaceAfter=6),
        Paragraph(
            "<font size='7' color='#94a3b8'>"
            "<b>NOTA LEGAL Y TÉCNICA:</b> Este informe ejecutivo ha sido emitido de manera automatizada por el motor analítico de SmartFinanzas v2.0. "
            "Las estimaciones probabilísticas de insolvencia y las métricas de explicabilidad SHAP corresponden a modelos predictivos supervisados de soporte para la toma de decisiones gerenciales "
            "y se sustentan en los saldos contables ingresados bajo responsabilidad de la empresa declarante. "
            "El presente informe no constituye dictamen pericial ni asesoría tributaria vinculante ante entes fiscalizadores."
            "</font>",
            estilo_texto
        )
    ]))

    # Función creadora de canvas personalizada con el nombre de la empresa para el encabezado dinámico
    def make_canvas(*args, **kwargs_c):
        c = NumberedCanvas(*args, **kwargs_c)
        c.empresa_nombre = nombre_empresa
        return c

    doc.build(elementos, canvasmaker=make_canvas)
    buffer.seek(0)
    return buffer


def construir_informe_predictivo_pdf(
    empresa=None,
    usuario=None,
    ultima_prediccion=None,
    periodo_balance='2024-Q4',
    periodo_proyectado='2025-Q1',
    ventana_preventiva_dias=90,
    score_proyectado=0.0,
    score_base=0.0,
    nivel_proyectado='Verde',
    delta_info=None,
    plan_recomendaciones=None,
    matriz_backtesting=None,
    todos_los_ratios=None,
    ratio_asociado=None,
    info_periodo=None,
    timeline_puntos=None,
    **kwargs,
):
    """
    Genera el Informe Ejecutivo Especializado de Proyección y Plan de Acción a 90 Días
    para el Dashboard Predictivo (Q_t -> Q_{t+1}).

    Incorpora:
    1. Portada formal ejecutiva y cuadro de metadatos de gobernanza concursal (Ley 20.720 / 21.563).
    2. Diagnóstico de Transición de Solvencia: Score Base (Q_t) vs Score Proyectado (Q_{t+1}),
       Aceleración Delta (\u0394) de Riesgo y Test de Quiebra Altman Z'' (1983).
    3. Plan Estratégico y Preventivo a 90 Días:
       - Directriz Macro de Transición (Objetivo Trimestral y Procedimiento).
       - Medidas Micro-Estratégicas por Factor Determinante SHAP (Situación, Acción, Impacto y Plazo).
    4. Matriz de Validación Histórica (Backtesting Retrospectivo a 90 Días).
    5. Explicabilidad Algorítmica SHAP Completa sobre Ratios Financieros (X1 a X7).
    6. Auditoría y Balances Contables del Período Analizado (IFRS).
    7. Certificación de Auditoría, Firmas y Nota Legal de Exención de Responsabilidad Fiduciaria.
    """
    buffer = io.BytesIO()

    # Documento tamaño Carta (612 x 792 pt), márgenes de 36 pt (ancho útil = 540 pt)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Paleta de Colores Corporativos Formales
    C_PRIMARIO = colors.HexColor('#0f172a')     # Slate 900
    C_SECUNDARIO = colors.HexColor('#334155')   # Slate 700
    C_MUTED = colors.HexColor('#64748b')        # Slate 500
    C_BORDE = colors.HexColor('#cbd5e1')        # Slate 300
    C_BORDE_LIGHT = colors.HexColor('#e2e8f0')  # Slate 200
    C_FONDO_CLARO = colors.HexColor('#f8fafc')  # Slate 50
    C_FONDO_ALT = colors.HexColor('#f1f5f9')    # Slate 100
    C_AZUL = colors.HexColor('#1d4ed8')         # Blue 700
    C_AZUL_FONDO = colors.HexColor('#eff6ff')   # Blue 50
    C_VERDE = colors.HexColor('#15803d')        # Green 700
    C_VERDE_FONDO = colors.HexColor('#f0fdf4')  # Green 50
    C_AMARILLO = colors.HexColor('#b45309')     # Amber 700
    C_AMARILLO_FONDO = colors.HexColor('#fefce8') # Amber 50
    C_ROJO = colors.HexColor('#b91c1c')         # Red 700
    C_ROJO_FONDO = colors.HexColor('#fef2f2')   # Red 50

    # Estilos Tipográficos
    estilo_banner_sup = ParagraphStyle(
        'PredBannerSup', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=C_AZUL,
        textTransform='uppercase', spaceAfter=2
    )
    estilo_titulo = ParagraphStyle(
        'PredDocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=C_PRIMARIO
    )
    estilo_subtitulo = ParagraphStyle(
        'PredDocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_MUTED
    )
    estilo_meta_header = ParagraphStyle(
        'PredMetaHeader', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=C_SECUNDARIO, alignment=2
    )
    estilo_seccion = ParagraphStyle(
        'PredSectionHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=C_PRIMARIO,
        spaceBefore=10, spaceAfter=4
    )
    estilo_texto = ParagraphStyle(
        'PredBodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11.5, textColor=C_SECUNDARIO
    )
    estilo_texto_muted = ParagraphStyle(
        'PredBodyMuted', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=C_MUTED
    )
    estilo_tabla_head = ParagraphStyle(
        'PredTableHead', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.white
    )
    estilo_tabla_celda = ParagraphStyle(
        'PredTableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=C_SECUNDARIO
    )
    estilo_tabla_celda_bold = ParagraphStyle(
        'PredTableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10.5, textColor=C_PRIMARIO
    )
    estilo_tabla_celda_center = ParagraphStyle(
        'PredTableCellCenter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=C_SECUNDARIO, alignment=1
    )
    estilo_tabla_celda_right = ParagraphStyle(
        'PredTableCellRight', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=C_SECUNDARIO, alignment=2
    )
    estilo_card_title = ParagraphStyle(
        'PredCardTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=C_MUTED, textTransform='uppercase'
    )
    estilo_card_val = ParagraphStyle(
        'PredCardVal', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=C_PRIMARIO, alignment=1
    )
    estilo_card_sub = ParagraphStyle(
        'PredCardSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7, leading=9, textColor=C_SECUNDARIO, alignment=1
    )

    elementos = []

    # =========================================================================
    # ENCABEZADO FORMAL Y PORTADA EJECUTIVA
    # =========================================================================
    fecha_emision = timezone.localtime().strftime('%d/%m/%Y %H:%M')
    nombre_empresa = empresa.business_name if empresa else "Empresa Sin Asignar"
    rut_empresa = empresa.tax_id if (empresa and empresa.tax_id) else "Sin RUT"
    usuario_nombre = usuario.username if usuario else "Auditoría Financiera"
    rol_nombre = (
        getattr(getattr(usuario, 'profile', None), 'role', None)
        or getattr(getattr(usuario, 'role', None), 'name', None)
        or "Usuario Operador"
    )

    periodo_base_txt = str(periodo_balance or '2024-Q4')
    periodo_proy_txt = str(periodo_proyectado or '2025-Q1')

    data_header = [
        [
            Paragraph("SMARTFINANZAS &middot; PLATAFORMA DE INTELIGENCIA FINANCIERA & ALERTA TEMPRANA", estilo_banner_sup),
            Paragraph(f"<b>Fecha de Emisión:</b> {fecha_emision}", estilo_meta_header),
        ],
        [
            Paragraph("<b>INFORME EJECUTIVO DE PROYECCIÓN Y PLAN A 90 DÍAS</b>", estilo_titulo),
            Paragraph(f"<b>Horizonte:</b> <font color='#1d4ed8'><b>{periodo_base_txt} &rarr; {periodo_proy_txt}</b></font>", estilo_meta_header),
        ],
        [
            Paragraph("Diagnóstico de Transición Financiera (Q<sub>t</sub> &rarr; Q<sub>t+1</sub>), Recomendaciones Estratégicas y Validación Histórica", estilo_subtitulo),
            Paragraph(f"<b>Emisor:</b> {usuario_nombre} ({rol_nombre})", estilo_meta_header),
        ]
    ]
    t_header = Table(data_header, colWidths=[360, 180])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(t_header)
    elementos.append(Spacer(1, 4))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=C_PRIMARIO, spaceAfter=6))

    # Cuadro de Metadatos de Gobernanza y Modelo Predictivo
    pred_id_str = f"#{ultima_prediccion.id}" if ultima_prediccion else "Automática"
    fecha_pred_str = ultima_prediccion.prediction_date.strftime('%d/%m/%Y %H:%M') if (ultima_prediccion and ultima_prediccion.prediction_date) else fecha_emision

    meta_table_data = [
        [
            Paragraph(f"<b>Razón Social:</b> {nombre_empresa}", estilo_tabla_celda),
            Paragraph(f"<b>RUT:</b> {rut_empresa}", estilo_tabla_celda),
            Paragraph(f"<b>Trimestre Base (Q<sub>t</sub>):</b> {periodo_base_txt}", estilo_tabla_celda),
            Paragraph(f"<b>Trimestre Proyectado:</b> {periodo_proy_txt}", estilo_tabla_celda),
        ],
        [
            Paragraph("<b>Modelo ML:</b> Random Forest v1.1", estilo_tabla_celda),
            Paragraph(f"<b>Inferencia ID:</b> {pred_id_str}", estilo_tabla_celda),
            Paragraph(f"<b>Ventana Preventiva:</b> {ventana_preventiva_dias} Días", estilo_tabla_celda),
            Paragraph("<b>Marco:</b> Ley 20.720 / 21.563 / IFRS", estilo_tabla_celda),
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[150, 110, 140, 140])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(t_meta)
    elementos.append(Spacer(1, 8))

    # =========================================================================
    # SECCIÓN 1: ALERTA TEMPRANA Y DIAGNÓSTICO DE TRANSICIÓN DE SOLVENCIA
    # =========================================================================
    elementos.append(Paragraph("1. Alerta Temprana y Diagnóstico de Transición de Solvencia (Q<sub>t</sub> &rarr; Q<sub>t+1</sub>)", estilo_seccion))

    score_base_val = float(score_base or 0.0)
    score_proy_val = float(score_proyectado or 0.0)
    nivel_proy_val = str(nivel_proyectado or ('Rojo' if score_proy_val > 70 else ('Amarillo' if score_proy_val > 35 else 'Verde')))

    if nivel_proy_val.lower() == 'rojo':
        color_proy_box = C_ROJO
        bg_proy_box = C_ROJO_FONDO
        estado_proy_txt = "RIESGO CRÍTICO"
        desc_proy_txt = "Alta probabilidad de insolvencia (>70%)"
    elif nivel_proy_val.lower() == 'amarillo':
        color_proy_box = C_AMARILLO
        bg_proy_box = C_AMARILLO_FONDO
        estado_proy_txt = "ALERTA PREVENTIVA"
        desc_proy_txt = "Tensión financiera moderada (35-70%)"
    else:
        color_proy_box = C_VERDE
        bg_proy_box = C_VERDE_FONDO
        estado_proy_txt = "ZONA SOLVENTE"
        desc_proy_txt = "Solvencia patrimonial sólida (\u226435%)"

    nivel_base_txt = "Solvente" if score_base_val <= 35 else ("Alerta" if score_base_val <= 70 else "Crítico")

    # Cálculo Altman Z'' (1983)
    altman_z_str = "--"
    altman_zona_txt = "Sin evaluación"
    if ratio_asociado:
        try:
            from dashboard.views import calcular_z_score_altman_1983
            z_val = calcular_z_score_altman_1983(ratio_asociado)
            altman_z_str = f"{z_val:.2f}"
            if z_val >= 2.60:
                altman_zona_txt = "Zona Segura (\u2265 2.60)"
            elif z_val < 1.10:
                altman_zona_txt = "Zona de Quiebra (< 1.10)"
            else:
                altman_zona_txt = "Zona Gris (1.10 - 2.60)"
        except Exception:
            altman_z_str = "--"

    # Delta info
    delta_val_str = "0.0 pts"
    delta_dir_txt = "Estable"
    if delta_info and isinstance(delta_info, dict):
        diff = delta_info.get('diferencia', 0.0)
        diff_f = float(diff or 0.0)
        if diff_f > 0:
            delta_val_str = f"+{diff_f:.1f} pts"
            delta_dir_txt = "Acelerando Riesgo \u2191"
        elif diff_f < 0:
            delta_val_str = f"{diff_f:.1f} pts"
            delta_dir_txt = "Reduciendo Riesgo \u2193"
        else:
            delta_val_str = "0.0 pts"
            delta_dir_txt = "Riesgo Constante \u2192"
    else:
        diff_calc = score_proy_val - score_base_val
        if diff_calc > 0:
            delta_val_str = f"+{diff_calc:.1f} pts"
            delta_dir_txt = "Acelerando Riesgo \u2191"
        elif diff_calc < 0:
            delta_val_str = f"{diff_calc:.1f} pts"
            delta_dir_txt = "Reduciendo Riesgo \u2193"
        else:
            delta_val_str = "0.0 pts"
            delta_dir_txt = "Riesgo Constante \u2192"

    # Tarjetas de Resumen Ejecutivo (4 columnas: 135 pt cada una = 540 pt)
    card_data = [
        [
            Paragraph("BALANCE ANALIZADO (Q<sub>t</sub>)", estilo_card_title),
            Paragraph("PROYECCIÓN (Q<sub>t+1</sub>)", estilo_card_title),
            Paragraph("ACELERACIÓN DINÁMICA", estilo_card_title),
            Paragraph("ALTMAN Z'' (1983)", estilo_card_title),
        ],
        [
            Paragraph(f"<b>{score_base_val:.1f}%</b>", estilo_card_val),
            Paragraph(f"<font color='{color_proy_box.hexval()}'><b>{score_proy_val:.1f}%</b></font>", estilo_card_val),
            Paragraph(f"<b>{delta_val_str}</b>", estilo_card_val),
            Paragraph(f"<b>{altman_z_str}</b>", estilo_card_val),
        ],
        [
            Paragraph(f"{periodo_base_txt} &middot; {nivel_base_txt}", estilo_card_sub),
            Paragraph(f"<font color='{color_proy_box.hexval()}'><b>{estado_proy_txt}</b></font>", estilo_card_sub),
            Paragraph(delta_dir_txt, estilo_card_sub),
            Paragraph(altman_zona_txt, estilo_card_sub),
        ]
    ]
    t_cards = Table(card_data, colWidths=[135, 135, 135, 135])
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), C_FONDO_CLARO),
        ('BACKGROUND', (1, 0), (1, -1), bg_proy_box),
        ('BACKGROUND', (2, 0), (2, -1), C_FONDO_CLARO),
        ('BACKGROUND', (3, 0), (3, -1), C_FONDO_CLARO),
        ('BOX', (0, 0), (0, -1), 0.5, C_BORDE),
        ('BOX', (1, 0), (1, -1), 1.0, color_proy_box),
        ('BOX', (2, 0), (2, -1), 0.5, C_BORDE),
        ('BOX', (3, 0), (3, -1), 0.5, C_BORDE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos.append(t_cards)
    elementos.append(Spacer(1, 5))

    # Párrafo interpretativo del horizonte predictivo
    if score_proy_val > 70.0:
        desc_alerta_p = (
            f"<b>DIAGNÓSTICO CRÍTICO:</b> La evaluación predictiva anticipa que en el horizonte de 90 días ({periodo_proy_txt}) "
            f"la compañía alcanzará un índice de vulnerabilidad de <b>{score_proy_val:.1f}%</b>, situándose en <b>Zona Crítica de Insolvencia</b>. "
            f"Se activa la ventana de salvaguarda concursal conforme a la Ley N° 20.720 (modernizada por Ley 21.563), requiriéndose la ejecución "
            f"inmediata del plan de reestructuración operativa y congelamiento de pasivos de corto plazo para evitar un procedimiento de liquidación judicial."
        )
    elif score_proy_val > 35.0:
        desc_alerta_p = (
            f"<b>ALERTA PREVENTIVA TEMPRANA:</b> El modelo proyecta para el próximo trimestre ({periodo_proy_txt}) un score de <b>{score_proy_val:.1f}%</b>, "
            f"reflejando tensiones emergentes en la liquidez operativa y apalancamiento. La empresa dispone de una ventana de 90 días para ejecutar ajustes "
            f"en políticas de cobro, contención de gastos fijos y reprogramación de vencimientos comerciales antes de que la presión sobre la caja escale a niveles críticos."
        )
    else:
        desc_alerta_p = (
            f"<b>ESTABILIDAD Y SOLVENCIA CONFIRMADA:</b> La proyección a 90 días ({periodo_proy_txt}) sitúa el score en <b>{score_proy_val:.1f}%</b> "
            f"(<b>Zona Solvente</b>), demostrando una sólida cobertura de obligaciones a corto plazo y equilibrio patrimonial. "
            f"Se recomienda mantener las directrices de eficiencia de capital de trabajo y constituir reservas de liquidez ante eventuales fluctuaciones de mercado."
        )
    elementos.append(Paragraph(desc_alerta_p, estilo_texto))
    elementos.append(Spacer(1, 8))

    # =========================================================================
    # SECCIÓN 2: PLAN ESTRATÉGICO Y RECOMENDACIONES PREVENTIVAS A 90 DÍAS
    # =========================================================================
    elementos.append(Paragraph("2. Plan Estratégico y Recomendaciones Preventivas a 90 Días", estilo_seccion))

    macro_rec = (plan_recomendaciones.get('macro') if (plan_recomendaciones and isinstance(plan_recomendaciones, dict)) else None) or {}
    tacticas_rec = (plan_recomendaciones.get('tacticas') if (plan_recomendaciones and isinstance(plan_recomendaciones, dict)) else None) or []

    macro_titulo = macro_rec.get('titulo') or "Directriz Macro de Transición Financiera"
    macro_prioridad = macro_rec.get('prioridad') or ("Alta" if score_proy_val > 70 else ("Media" if score_proy_val > 35 else "Estratégica"))
    macro_resumen = macro_rec.get('resumen_transicion') or "Plan preventivo diseñado para amortiguar presiones de caja en los próximos 90 días."
    macro_accion = macro_rec.get('accion_principal') or "Implementar control estricto de egresos operativos y preservar liquidez."
    macro_pasos = macro_rec.get('procedimiento_pasos') or []
    macro_fuente = macro_rec.get('cita_fuente') or "Ley 20.720 / 21.563 de Reorganización y Liquidación de Empresas; Zurita (2008)."

    pasos_html = ""
    if macro_pasos and isinstance(macro_pasos, list):
        pasos_html = "<br/>".join([f"&bull; {p}" for p in macro_pasos[:3]])

    macro_content = [
        [
            Paragraph(f"<b>DIRECTRIZ MACRO: {macro_titulo.upper()}</b>", estilo_tabla_celda_bold),
            Paragraph(f"<b>Prioridad:</b> <font color='{color_proy_box.hexval()}'><b>{macro_prioridad.upper()}</b></font>", estilo_tabla_celda_right),
        ],
        [
            Paragraph(f"<b>Diagnóstico de Transición:</b> {macro_resumen}", estilo_tabla_celda),
            Paragraph("", estilo_tabla_celda),
        ],
        [
            Paragraph(f"<b>Acción Estratégica Principal:</b> {macro_accion}", estilo_tabla_celda),
            Paragraph("", estilo_tabla_celda),
        ],
    ]
    if pasos_html:
        macro_content.append([
            Paragraph(f"<b>Procedimiento Paso a Paso:</b><br/>{pasos_html}", estilo_tabla_celda),
            Paragraph("", estilo_tabla_celda),
        ])
    macro_content.append([
        Paragraph(f"<b>Fundamento Doctrinal y Normativo:</b> <font color='#64748b'>{macro_fuente}</font>", estilo_texto_muted),
        Paragraph("", estilo_tabla_celda),
    ])

    t_macro = Table(macro_content, colWidths=[430, 110])
    t_macro.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)) if pasos_html else ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, -1), (1, -1)),
        ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
        ('BOX', (0, 0), (-1, -1), 1.0, color_proy_box),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elementos.append(t_macro)
    elementos.append(Spacer(1, 6))

    # Medidas Micro-Estratégicas por Factor Determinante (SHAP)
    if tacticas_rec:
        elementos.append(Paragraph("<b>Medidas Micro-Estratégicas por Factor Determinante (SHAP):</b>", estilo_texto))
        elementos.append(Spacer(1, 3))

        filas_tacticas = [
            [
                Paragraph("Factor / Ratio Crítico", estilo_tabla_head),
                Paragraph("Situación Actual / Diagnóstico", estilo_tabla_head),
                Paragraph("Acción Táctica Recomendada", estilo_tabla_head),
                Paragraph("Plazo / Responsable", estilo_tabla_head),
            ]
        ]

        # Mapeo de plazos y responsables según grupo de riesgo
        RESPONSABLES_POR_GRUPO = {
            'Liquidez': ('Tesorería / Cobranzas', 'Inmediato (0-15 días)'),
            'Endeudamiento': ('Gerencia / Finanzas', 'Corto Plazo (15-45 días)'),
            'Rentabilidad': ('Comercial / Operaciones', 'Mediano Plazo (30-60 días)'),
            'Eficiencia': ('Operaciones / Ventas', 'Mediano Plazo (30-90 días)'),
            'Flujo de Caja': ('Tesorería / Contabilidad', 'Inmediato (0-15 días)'),
        }

        for tac in tacticas_rec[:4]:
            tac_grupo = tac.get('grupo_riesgo') or 'Financiero'
            tac_prio = tac.get('prioridad') or 'Alta'
            tac_titulo = tac.get('titulo') or 'Medida Preventiva'
            tac_diag = tac.get('diagnostico_operativo') or ''
            tac_que = tac.get('que_hacer') or ''
            tac_proc = tac.get('procedimiento') or ''

            resp_sug, plazo_sug = RESPONSABLES_POR_GRUPO.get(tac_grupo, ('Administración', '30-60 días'))
            col_prio = C_ROJO if tac_prio == 'Alta' else (C_AMARILLO if tac_prio == 'Media' else C_VERDE)

            cuerpo_accion = f"<b>{tac_titulo}</b><br/>{tac_que}"
            if tac_proc:
                cuerpo_accion += f"<br/><font color='#64748b'><b>Paso sugerido:</b> {tac_proc}</font>"

            filas_tacticas.append([
                Paragraph(f"<b>{tac_grupo}</b><br/><font color='{col_prio.hexval()}'><b>Prioridad {tac_prio}</b></font>", estilo_tabla_celda),
                Paragraph(tac_diag if tac_diag else "Desviación observada respecto al rango óptimo.", estilo_tabla_celda),
                Paragraph(cuerpo_accion, estilo_tabla_celda),
                Paragraph(f"<b>{resp_sug}</b><br/>{plazo_sug}", estilo_tabla_celda_center),
            ])

        t_tacticas = Table(filas_tacticas, colWidths=[110, 140, 200, 90])
        t_tacticas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARIO),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_FONDO_CLARO]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(t_tacticas)
    elementos.append(Spacer(1, 8))

    # =========================================================================
    # SECCIÓN 3: MATRIZ DE VALIDACIÓN HISTÓRICA (BACKTESTING A 90 DÍAS)
    # =========================================================================
    if matriz_backtesting and isinstance(matriz_backtesting, list) and len(matriz_backtesting) > 0:
        elementos.append(Paragraph("3. Matriz de Validación Histórica (Backtesting Retrospectivo a 90 Días)", estilo_seccion))
        elementos.append(Paragraph(
            "Verificación empírica de la precisión predictiva del modelo contrastando pronósticos pasados frente a los balances reales posteriores (Altman Z''):",
            estilo_texto_muted
        ))
        elementos.append(Spacer(1, 4))

        filas_bt = [
            [
                Paragraph("Trimestre Base (Q<sub>t</sub>)", estilo_tabla_head),
                Paragraph("Proyectado (Q<sub>t+1</sub>)", estilo_tabla_head),
                Paragraph("Score Pred.", estilo_tabla_head),
                Paragraph("Nivel", estilo_tabla_head),
                Paragraph("Realidad Contable Observada", estilo_tabla_head),
                Paragraph("Dictamen de Validación", estilo_tabla_head),
            ]
        ]

        for item_bt in matriz_backtesting[-6:]:  # Últimos 6 trimestres para ajuste de página
            p_base_i = str(item_bt.get('periodo_base', '-'))
            p_fut_i = str(item_bt.get('periodo_proyectado', '-'))
            sc_bt_i = float(item_bt.get('score_proyectado', 0.0))
            niv_bt_i = str(item_bt.get('nivel_proyectado', 'Verde'))
            col_bt_i = C_ROJO if niv_bt_i == 'Rojo' else (C_AMARILLO if niv_bt_i == 'Amarillo' else C_VERDE)
            real_txt = str(item_bt.get('estado_real', '-'))
            res_txt = str(item_bt.get('resultado', '-'))
            es_act = bool(item_bt.get('es_activo', False))

            base_label = f"<b>{p_base_i}</b>"
            if es_act:
                base_label += " <font color='#1d4ed8'><b>[ACTUAL]</b></font>"

            filas_bt.append([
                Paragraph(base_label, estilo_tabla_celda),
                Paragraph(p_fut_i, estilo_tabla_celda_center),
                Paragraph(f"<b>{sc_bt_i:.1f}%</b>", estilo_tabla_celda_center),
                Paragraph(f"<font color='{col_bt_i.hexval()}'><b>{niv_bt_i.upper()}</b></font>", estilo_tabla_celda_center),
                Paragraph(real_txt, estilo_tabla_celda),
                Paragraph(f"<b>{res_txt}</b>", estilo_tabla_celda_center),
            ])

        t_bt = Table(filas_bt, colWidths=[100, 75, 60, 60, 145, 100])
        t_bt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARIO),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_FONDO_CLARO]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(t_bt)
        elementos.append(Spacer(1, 8))

    # =========================================================================
    # SECCIÓN 4: EXPLICABILIDAD ALGORÍTMICA SHAP Y RATIOS FINANCIEROS (X1 a X7)
    # =========================================================================
    if todos_los_ratios:
        elementos.append(Paragraph("4. Explicabilidad Algorítmica SHAP y Factores Financieros Determinantes (X1 a X7)", estilo_seccion))
        elementos.append(Paragraph(
            "Cumplimiento de transparencia algorítmica (OECD AI Principles & IEEE 7001): Descomposición cuantitativa del score en los 7 ratios financieros oficiales:",
            estilo_texto_muted
        ))
        elementos.append(Spacer(1, 4))

        filas_ratios = [
            [
                Paragraph("Cód.", estilo_tabla_head),
                Paragraph("Variable Financiera", estilo_tabla_head),
                Paragraph("Grupo", estilo_tabla_head),
                Paragraph("Valor Balance", estilo_tabla_head),
                Paragraph("Meta Óptima", estilo_tabla_head),
                Paragraph("Impacto SHAP en Riesgo", estilo_tabla_head),
            ]
        ]

        for r_item in todos_los_ratios:
            cod = r_item.get('codigo', '-')
            nom = r_item.get('nombre', '-')
            grp = r_item.get('grupo', '-')
            val = r_item.get('valor', 0.0)
            uni = r_item.get('unidad', '')
            meta = r_item.get('meta', '-')
            desc = r_item.get('texto_explicativo') or ''
            es_top = r_item.get('es_top_3', False)
            imp_shap = r_item.get('impacto_shap', 0.0)

            val_str = f"{val:.2f}{uni}" if isinstance(val, (int, float)) else str(val)
            shap_signo = "+" if imp_shap > 0 else ""
            shap_txt = f"{shap_signo}{imp_shap:.3f}" if imp_shap else "--"

            cod_txt = f"<b>{cod}</b>"
            if es_top:
                cod_txt += " <font color='#1d4ed8'><b>*</b></font>"

            filas_ratios.append([
                Paragraph(cod_txt, estilo_tabla_celda_center),
                Paragraph(f"<b>{nom}</b>", estilo_tabla_celda),
                Paragraph(grp, estilo_tabla_celda),
                Paragraph(f"<b>{val_str}</b>", estilo_tabla_celda_right),
                Paragraph(meta, estilo_tabla_celda_center),
                Paragraph(f"{desc} ({shap_txt})", estilo_tabla_celda),
            ])

        t_ratios = Table(filas_ratios, colWidths=[35, 125, 75, 75, 75, 155])
        t_ratios.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARIO),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_FONDO_CLARO]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(t_ratios)
        elementos.append(Spacer(1, 8))

    # =========================================================================
    # SECCIÓN 5: INFORMACIÓN CONTABLE DEL BALANCE DEL PERÍODO
    # =========================================================================
    if info_periodo:
        elementos.append(Paragraph("5. Resumen de Estados Financieros del Período Evaluado (IFRS)", estilo_seccion))

        def fmt_m(num):
            try:
                return f"${Decimal(num):,.0f}".replace(',', '.')
            except Exception:
                return "$0"

        act_tot = fmt_m(info_periodo.get('activo_total', 0))
        pas_tot = fmt_m(info_periodo.get('pasivo_total', 0))
        patrim = fmt_m(info_periodo.get('patrimonio', 0))
        act_cte = fmt_m(info_periodo.get('activo_corriente', 0))
        pas_cte = fmt_m(info_periodo.get('pasivo_corriente', 0))
        cap_trab = fmt_m(info_periodo.get('capital_trabajo', 0))
        ing_netos = fmt_m(info_periodo.get('ingresos_netos', 0))
        ebit_val = fmt_m(info_periodo.get('ebit', 0))
        util_neta = fmt_m(info_periodo.get('utilidad_neta', 0))
        cuad_txt = "Cuadrado (Activo = Pasivo + Patrimonio)" if info_periodo.get('cuadrado') else "Descuadre Contable Detectado"

        data_bal = [
            [
                Paragraph("<b>Activo Total:</b>", estilo_tabla_celda_bold),
                Paragraph(act_tot, estilo_tabla_celda_right),
                Paragraph("<b>Pasivo Total:</b>", estilo_tabla_celda_bold),
                Paragraph(pas_tot, estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Activo Corriente:</b>", estilo_tabla_celda_bold),
                Paragraph(act_cte, estilo_tabla_celda_right),
                Paragraph("<b>Pasivo Corriente:</b>", estilo_tabla_celda_bold),
                Paragraph(pas_cte, estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Capital de Trabajo:</b>", estilo_tabla_celda_bold),
                Paragraph(cap_trab, estilo_tabla_celda_right),
                Paragraph("<b>Patrimonio Neto:</b>", estilo_tabla_celda_bold),
                Paragraph(patrim, estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Ingresos Operacionales:</b>", estilo_tabla_celda_bold),
                Paragraph(ing_netos, estilo_tabla_celda_right),
                Paragraph("<b>Resultado Operacional (EBIT):</b>", estilo_tabla_celda_bold),
                Paragraph(ebit_val, estilo_tabla_celda_right),
            ],
            [
                Paragraph("<b>Utilidad Neta:</b>", estilo_tabla_celda_bold),
                Paragraph(util_neta, estilo_tabla_celda_right),
                Paragraph("<b>Cuadratura IFRS:</b>", estilo_tabla_celda_bold),
                Paragraph(f"<b>{cuad_txt}</b>", estilo_tabla_celda_right),
            ],
        ]
        t_bal = Table(data_bal, colWidths=[140, 130, 140, 130])
        t_bal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_FONDO_CLARO),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDE),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elementos.append(t_bal)
        elementos.append(Spacer(1, 10))

    # =========================================================================
    # SECCIÓN 6: CERTIFICACIÓN, FIRMAS Y AVISO LEGAL DE SALVAGUARDA
    # =========================================================================
    data_firmas = [
        [
            Paragraph("________________________________________<br/><b>Responsable de Auditoría / Analista</b><br/>" + usuario_nombre, estilo_tabla_celda_center),
            Paragraph("", estilo_tabla_celda),
            Paragraph("________________________________________<br/><b>Gerencia General / Representante Legal</b><br/>" + nombre_empresa, estilo_tabla_celda_center),
        ]
    ]
    t_firmas = Table(data_firmas, colWidths=[240, 60, 240])
    t_firmas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(KeepTogether([
        t_firmas,
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=0.8, color=C_BORDE, spaceAfter=4),
        Paragraph(
            "<font size='6.5' color='#64748b'>"
            "<b>NOTA LEGAL, TÉCNICA Y DE DEBER FIDUCIARIO:</b> Este informe ejecutivo ha sido emitido de manera automatizada por el motor predictivo de SmartFinanzas v2.0 "
            "bajo el marco analítico de la Ley N° 20.720 (modernizada por Ley N° 21.563 de Reorganización y Liquidación de Empresas) y la Ley FinTech N° 21.521. "
            "Las proyecciones probabilísticas y las recomendaciones tácticas a 90 días constituyen instrumentos de soporte preventivo para la administración y no sustituyen el juicio soberano "
            "del Directorio ni el deber fiduciario de cuidado establecido en el Artículo 41 de la Ley N° 18.046 sobre Sociedades Anónimas. "
            "El presente informe no constituye asesoría tributaria vinculante ante el Servicio de Impuestos Internos (SII), certificación formal ante la CMF ni dictamen pericial judicial."
            "</font>",
            estilo_texto
        )
    ]))

    # Función creadora de canvas personalizada con el nombre de la empresa y título predictivo
    def make_canvas_pred(*args, **kwargs_c):
        c = NumberedCanvas(*args, **kwargs_c)
        c.empresa_nombre = nombre_empresa
        c.titulo_header = "SMARTFINANZAS · Informe Ejecutivo de Proyección y Plan a 90 Días"
        return c

    doc.build(elementos, canvasmaker=make_canvas_pred)
    buffer.seek(0)
    return buffer
