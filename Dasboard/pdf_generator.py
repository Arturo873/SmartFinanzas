"""
Generador de Informes Ejecutivos en PDF con ReportLab.
SmartFinanzas - Capa de Presentación Gerencial.
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
from reportlab.lib.units import inch


def construir_informe_ejecutivo_pdf(
    empresa,
    ultima_prediccion,
    top_3_variables,
    ingreso_real_hoy,
    usuario=None,
    total_ventas_hoy=0,
):
    """
    Construye y devuelve un archivo PDF en memoria (BytesIO) con el diagnóstico
    ejecutivo de riesgo de insolvencia y resumen operativo de SmartFinanzas.
    """
    buffer = io.BytesIO()

    # Documento con márgenes de media pulgada (36 pt)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Paleta de colores corporativa
    COLOR_PRIMARIO = colors.HexColor('#0f172a')
    COLOR_SECUNDARIO = colors.HexColor('#1e293b')
    COLOR_MUTED = colors.HexColor('#64748b')
    COLOR_BORDE = colors.HexColor('#e2e8f0')
    COLOR_FONDO_CLARO = colors.HexColor('#f8fafc')

    # Estilos de tipografía personalizados
    estilo_titulo = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=COLOR_PRIMARIO,
    )
    estilo_subtitulo = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_MUTED,
    )
    estilo_seccion = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARIO,
        spaceAfter=6,
    )
    estilo_texto = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_SECUNDARIO,
    )
    estilo_tabla_head = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
    )
    estilo_tabla_celda = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=COLOR_SECUNDARIO,
    )
    estilo_tabla_celda_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=COLOR_PRIMARIO,
    )

    elementos = []

    # 1. ENCABEZADO CORPORATIVO
    fecha_emision = timezone.localtime().strftime('%d/%m/%Y %H:%M')
    nombre_empresa = empresa.razon_social if empresa else "Empresa Demo"
    rut_empresa = empresa.rut if empresa else "N/A"
    usuario_nombre = usuario.username if usuario else "Gerencia General"

    tabla_header_data = [
        [
            Paragraph("<b>SMARTFINANZAS</b> &middot; Sistema de Gestión de Liquidez", estilo_subtitulo),
            Paragraph(f"<b>Fecha de Emisión:</b> {fecha_emision}", estilo_subtitulo),
        ],
        [
            Paragraph(f"<b>INFORME EJECUTIVO DE RIESGO DE INSOLVENCIA</b>", estilo_titulo),
            Paragraph(f"<b>Generado por:</b> {usuario_nombre}", estilo_subtitulo),
        ],
        [
            Paragraph(f"<b>Empresa:</b> {nombre_empresa} &nbsp;|&nbsp; <b>RUT:</b> {rut_empresa}", estilo_subtitulo),
            Paragraph(f"<b>Modelo:</b> Random Forest v1.1 + SHAP", estilo_subtitulo),
        ]
    ]

    tabla_header = Table(tabla_header_data, colWidths=[360, 180])
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tabla_header)
    elementos.append(Spacer(1, 10))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARIO, spaceAfter=12))

    # 2. SECCIÓN: SEMÁFORO DE RIESGO Y SCORE
    score_val = float(ultima_prediccion.score_riesgo) if (ultima_prediccion and ultima_prediccion.score_riesgo is not None) else 0.0
    nivel_val = ultima_prediccion.nivel_semaforo if ultima_prediccion else "Sin Datos"

    if nivel_val == 'Rojo':
        color_semaforo = colors.HexColor('#dc2626')
        texto_nivel = "CRÍTICO - ALTO RIESGO DE INSOLVENCIA"
        desc_nivel = (
            "La empresa se ubica en el cuadrante de alerta máxima. La probabilidad estadística de insolvencia "
            "supera el umbral del 70%. Se recomienda la activación inmediata de protocolos de preservación de caja."
        )
    elif nivel_val == 'Amarillo':
        color_semaforo = colors.HexColor('#d97706')
        texto_nivel = "MODERADO - ALERTA PREVENTIVA"
        desc_nivel = (
            "La empresa presenta tensiones de liquidez y márgenes ajustados (score entre 35% y 70%). "
            "Requiere supervisión continua en la rotación de cuentas y disciplina en gastos operativos."
        )
    else:
        color_semaforo = colors.HexColor('#16a34a')
        texto_nivel = "BAJO - CONDICIÓN FINANCIERA SOLVENTE"
        desc_nivel = (
            "La empresa exhibe una estructura equilibrada con riesgo controlado (score inferior o igual a 35%). "
            "La capacidad de pago y absorción de compromisos financieros a corto plazo se mantiene sólida."
        )

    elementos.append(Paragraph("1. Diagnóstico del Semáforo de Riesgo", estilo_seccion))

    estilo_score_num = ParagraphStyle(
        'ScoreNum',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=32,
        textColor=color_semaforo,
        alignment=1,
    )
    estilo_score_badge = ParagraphStyle(
        'ScoreBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=color_semaforo,
        alignment=1,
    )

    fecha_pred_str = ultima_prediccion.fecha_prediccion.strftime('%d/%m/%Y %H:%M') if (ultima_prediccion and ultima_prediccion.fecha_prediccion) else "N/A"

    data_semaforo = [
        [
            Paragraph(f"SCORE DE RIESGO<br/><b>{score_val:.1f}</b> / 100", estilo_score_num),
            Paragraph(
                f"<b>ESTADO: {texto_nivel}</b><br/><br/>"
                f"{desc_nivel}<br/><br/>"
                f"<font color='#64748b' size='7.5'>Última inferencia ejecutada el: {fecha_pred_str}</font>",
                estilo_texto,
            )
        ]
    ]

    tabla_semaforo = Table(data_semaforo, colWidths=[150, 390])
    tabla_semaforo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO_CLARO),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDE),
        ('LINEAFTER', (0, 0), (0, 0), 1, COLOR_BORDE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elementos.append(tabla_semaforo)
    elementos.append(Spacer(1, 14))

    # 3. SECCIÓN: EXPLICABILIDAD SHAP (TOP-3 VARIABLES)
    elementos.append(Paragraph("2. Factores Clave de la Predicción (Explicabilidad Local SHAP)", estilo_seccion))
    elementos.append(Paragraph(
        "A continuación se detallan las 3 variables financieras con mayor impacto cuantitativo en la predicción "
        "generada por el modelo Random Forest:",
        estilo_texto
    ))
    elementos.append(Spacer(1, 6))

    filas_shap = [
        [
            Paragraph("Variable Financiera", estilo_tabla_head),
            Paragraph("Valor Actual", estilo_tabla_head),
            Paragraph("Impacto SHAP", estilo_tabla_head),
            Paragraph("Diagnóstico Interpretativo", estilo_tabla_head),
        ]
    ]

    if top_3_variables:
        for item in top_3_variables:
            nombre_var = item.get('nombre', item.get('variable', 'Variable'))
            val = item.get('valor', 0.0)
            unidad = item.get('unidad', '')
            impacto = item.get('impacto_pct', item.get('impacto', 0.0))
            texto = item.get('texto', item.get('texto_resumen', ''))
            aumenta = item.get('aumenta_riesgo', impacto >= 0)

            signo = "+" if impacto >= 0 else ""
            color_impacto = "#dc2626" if aumenta else "#16a34a"

            filas_shap.append([
                Paragraph(f"<b>{nombre_var}</b>", estilo_tabla_celda_bold),
                Paragraph(f"{val:.2f}{unidad}", estilo_tabla_celda),
                Paragraph(f"<font color='{color_impacto}'><b>{signo}{impacto:.1f}%</b></font>", estilo_tabla_celda),
                Paragraph(texto, estilo_tabla_celda),
            ])
    else:
        filas_shap.append([
            Paragraph("No hay variables SHAP registradas", estilo_tabla_celda),
            Paragraph("-", estilo_tabla_celda),
            Paragraph("-", estilo_tabla_celda),
            Paragraph("Ejecute una predicción desde el módulo para calcular el impacto.", estilo_tabla_celda),
        ])

    tabla_shap = Table(filas_shap, colWidths=[120, 70, 75, 275])
    tabla_shap.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_shap)
    elementos.append(Spacer(1, 14))

    # 4. SECCIÓN: RESUMEN OPERATIVO DE CAJA Y VENTAS
    elementos.append(Paragraph("3. Resumen Operativo del Día Actual (Flujo de Ventas)", estilo_seccion))

    ingreso_fmt = f"${Decimal(ingreso_real_hoy):,.0f}".replace(',', '.')

    data_operativa = [
        [
            Paragraph("<b>Ingreso Real Ventas (Hoy):</b>", estilo_tabla_celda_bold),
            Paragraph(f"<font size='11' color='#0f172a'><b>{ingreso_fmt}</b></font>", estilo_tabla_celda),
            Paragraph("<b>Transacciones Registradas:</b>", estilo_tabla_celda_bold),
            Paragraph(f"{total_ventas_hoy} operación(es)", estilo_tabla_celda),
        ],
        [
            Paragraph("<b>Fecha Contable:</b>", estilo_tabla_celda_bold),
            Paragraph(timezone.localdate().strftime('%d/%m/%Y'), estilo_tabla_celda),
            Paragraph("<b>Estado de Caja:</b>", estilo_tabla_celda_bold),
            Paragraph("Operaciones procesadas", estilo_tabla_celda),
        ]
    ]

    tabla_operativa = Table(data_operativa, colWidths=[140, 130, 140, 130])
    tabla_operativa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO_CLARO),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_operativa)
    elementos.append(Spacer(1, 14))

    # 5. RECOMENDACIONES ESTRATÉGICAS
    elementos.append(Paragraph("4. Recomendaciones Estratégicas para la Gerencia", estilo_seccion))

    if nivel_val == 'Rojo':
        rec_texto = (
            "&bull; <b>Plan de Contingencia de Caja:</b> Congelar compras de activos fijos no esenciales.<br/>"
            "&bull; <b>Gestión de Pasivos:</b> Renegociar plazos con proveedores estratégicos para extender el ciclo de caja.<br/>"
            "&bull; <b>Cobranza Activa:</b> Implementar incentivos de pronto pago a clientes para acelerar ingresos inmediatos."
        )
    elif nivel_val == 'Amarillo':
        rec_texto = (
            "&bull; <b>Monitoreo de Eficiencia:</b> Controlar márgenes por línea de producto y reducir costos ocultos.<br/>"
            "&bull; <b>Fondo de Reserva:</b> Destinar un porcentaje fijo de la utilidad diaria a provisiones de liquidez.<br/>"
            "&bull; <b>Revisión de Créditos:</b> Ajustar políticas de crédito comercial para evitar atrasos superiores a 30 días."
        )
    else:
        rec_texto = (
            "&bull; <b>Mantenimiento de Solvencia:</b> Continuar con la disciplina de rotación de inventarios y capital de trabajo.<br/>"
            "&bull; <b>Inversión Productiva:</b> Evaluar alternativas de expansión con bajo apalancamiento financiero.<br/>"
            "&bull; <b>Gestión de Excedentes:</b> Rentabilizar excesos de liquidez temporal en instrumentos de bajo riesgo."
        )

    elementos.append(Paragraph(rec_texto, estilo_texto))
    elementos.append(Spacer(1, 20))

    # 6. PIE DE PÁGINA Y NOTA LEGAL
    elementos.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_BORDE, spaceAfter=8))
    elementos.append(Paragraph(
        "<font size='7.5' color='#94a3b8'>"
        "SmartFinanzas v2.0 &middot; Documento de uso interno y confidencial emitido exclusivamente para toma de decisiones gerenciales. "
        "Las predicciones probabilísticas y métricas SHAP son estimaciones estadísticas de soporte y no constituyen asesoría tributaria vinculante."
        "</font>",
        estilo_texto
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer

