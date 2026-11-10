"""
Módulo de Servicios ETL (Extract, Transform, Load) para SmartFinanzas.

Este servicio implementa el pipeline integral de ingesta, saneamiento,
validación contable y persistencia de estados financieros a partir de archivos
(.csv, .xlsx). Además, calcula de forma desacoplada los ratios de liquidez,
las 7 variables del modelo de Machine Learning (V1 a V7) y los ratios
de referencia contable (Z''EM de Altman, Prueba Ácida, etc.).
"""

import os
import uuid
import logging
from decimal import Decimal
from io import StringIO, BytesIO
from typing import Tuple, List, Dict, Any, Optional

import numpy as np
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import FinancialUpload, FinancialRatio
from usuarios.models import User, Company
from AppWeb.models import UploadState

logger = logging.getLogger(__name__)


# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES DEL PIPELINE ETL
# ==============================================================================

COLUMNAS_PLANTILLA: List[str] = [
    'Id_Empresa',
    'Periodo',
    'Activo_Circulante',
    'Pasivo_Circulante',
    'Efectivo_Equivalentes',
    'Inventarios',
    'Activo_Total',
    'Pasivo_Total',
    'Patrimonio_Neto',
    'Utilidad_Neta',
    'Ingresos_Netos',
    'EBIT',
    'Utilidades_Retenidas',
]

COLUMNAS_NUMERICAS: List[str] = COLUMNAS_PLANTILLA[2:]

TOLERANCIA_DESCUADRE_PORCENTAJE: float = 0.01  # 1% del Activo Total
TOLERANCIA_DESCUADRE_MINIMA: float = 1.0      # Mínimo absoluto para evitar falsos positivos

RAZON_CORRIENTE_MAXIMA: float = 10.0
LEVERAGE_MAXIMO: float = 10.0
MARGEN_OPERACIONAL_LIMITE: float = 1.0
ROTACION_ACTIVOS_MAXIMA: float = 10.0
MINIMO_CIERRES_VOLATILIDAD: int = 20

# Directorio de almacenamiento temporal de archivos procesados
DATA_DIR: str = os.path.join(settings.BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# ==============================================================================
# FUNCIONES MATEMÁTICAS Y DE INGENIERÍA FINANCIERA (DESACOPLADAS)
# ==============================================================================

def _dividir_seguro(numerador: float, denominador: float, eps: float = 1e-6) -> Optional[float]:
    """División segura que evita ZeroDivisionError devolviendo None si denominador <= 0."""
    if denominador is None or abs(denominador) <= eps:
        return None
    return numerador / denominador


def calcular_zem_altman(fila: Dict[str, Any]) -> float:
    """
    Z-score de Altman para mercados emergentes (Z''EM):
    Altman (2000) modificó la fórmula para mercados emergentes y empresas
    no manufactureras:
    Z''EM = 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    donde:
      X1 = (Activo_Circulante - Pasivo_Circulante) / Activo_Total
      X2 = Utilidades_Retenidas / Activo_Total
      X3 = EBIT / Activo_Total
      X4 = Patrimonio_Neto / Pasivo_Total
    """
    activo_total = float(fila['Activo_Total'])
    pasivo_total = float(fila['Pasivo_Total'])
    activo_total_seguro = activo_total if activo_total > 0 else 1.0

    x1 = (float(fila['Activo_Circulante']) - float(fila['Pasivo_Circulante'])) / activo_total_seguro
    x2 = float(fila['Utilidades_Retenidas']) / activo_total_seguro
    x3 = float(fila['EBIT']) / activo_total_seguro
    x4 = float(fila['Patrimonio_Neto']) / pasivo_total if pasivo_total > 0 else LEVERAGE_MAXIMO

    return round(3.25 + 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4, 4)


def calcular_volatilidad_desde_cierres(empresa: Optional[Company]) -> Tuple[Optional[float], int, bool]:
    """
    Calcula V7 (Volatilidad del Flujo de Caja) a partir de los cierres confirmados
    registrados en el módulo transaccional (CashRegisterClosure).

    Devuelve: (volatilidad_valor, cantidad_cierres, usa_volatilidad_neutra)
    """
    if not empresa:
        return None, 0, True

    try:
        from moduloTransaccional.models import CashRegisterClosure
        cierres = CashRegisterClosure.objects.filter(
            company=empresa
        ).exclude(status__in=['ANULADO', 'Anulado', 'CANCELADO']).order_by('date')

        count = cierres.count()
        if count < MINIMO_CIERRES_VOLATILIDAD:
            return None, count, True

        flujos = []
        ingresos = []
        for c in cierres:
            flujo_diario = float(c.counted_total or c.system_total or 0)
            ventas_brutas = float(c.system_total or 0)
            flujos.append(flujo_diario)
            if ventas_brutas > 0:
                ingresos.append(ventas_brutas)

        if len(flujos) < MINIMO_CIERRES_VOLATILIDAD or not ingresos or np.mean(ingresos) <= 0:
            return None, count, True

        flujos_arr = np.asarray(flujos, dtype=float)
        ingresos_mean = float(np.mean(ingresos))
        volatilidad = float(flujos_arr.std(ddof=1) / ingresos_mean)
        return round(volatilidad, 4), count, False
    except Exception:
        return None, 0, True


def calcular_indicadores_completos(fila: Dict[str, Any], empresa: Optional[Company] = None) -> Dict[str, Any]:
    """
    Calcula los 7 ratios del modelo ML y todos los ratios de referencia contable
    para una fila de balance financiero.
    """
    activo_circulante = float(fila['Activo_Circulante'])
    pasivo_circulante = float(fila['Pasivo_Circulante'])
    activo_total = float(fila['Activo_Total'])
    pasivo_total = float(fila['Pasivo_Total'])
    patrimonio = float(fila['Patrimonio_Neto'])
    ingresos = float(fila['Ingresos_Netos'])
    ebit = float(fila['EBIT'])
    utilidad_neta = float(fila['Utilidad_Neta'])
    inventarios = float(fila['Inventarios'])
    efectivo = float(fila['Efectivo_Equivalentes'])

    activo_total_seguro = activo_total if activo_total > 0 else 1.0
    denom_corto_plazo = pasivo_circulante if pasivo_circulante > 0 else 1e-6

    # V1: Razón Corriente
    razon_corriente = _dividir_seguro(activo_circulante, pasivo_circulante)
    if razon_corriente is None or razon_corriente > RAZON_CORRIENTE_MAXIMA:
        v1 = RAZON_CORRIENTE_MAXIMA
    else:
        v1 = max(0.0, razon_corriente)

    # V2: Capital de Trabajo / Activos Totales
    v2 = (activo_circulante - pasivo_circulante) / activo_total_seguro

    # V3: Leverage Total (Pasivo Total / Patrimonio)
    leverage = _dividir_seguro(pasivo_total, patrimonio)
    if leverage is None or patrimonio <= 0 or leverage > LEVERAGE_MAXIMO:
        v3 = LEVERAGE_MAXIMO
    else:
        v3 = max(0.0, leverage)

    # V4: ROA Operacional (EBIT / Activo Total)
    v4 = ebit / activo_total_seguro

    # V5: Margen Operacional (EBIT / Ingresos)
    margen = _dividir_seguro(ebit, ingresos)
    if margen is None:
        v5 = -MARGEN_OPERACIONAL_LIMITE if ebit < 0 else 0.0
    else:
        v5 = float(np.clip(margen, -MARGEN_OPERACIONAL_LIMITE, MARGEN_OPERACIONAL_LIMITE))

    # V6: Rotación de Activos (Ingresos / Activo Total)
    rotacion = _dividir_seguro(ingresos, activo_total_seguro)
    v6 = min(rotacion if rotacion is not None else 0.0, ROTACION_ACTIVOS_MAXIMA)

    # V7: Volatilidad de Flujo
    v7, cierres_count, usa_neutra = calcular_volatilidad_desde_cierres(empresa)

    # Ratios de Referencia Contable
    ref_prueba_acida = (activo_circulante - inventarios) / denom_corto_plazo
    ref_razon_caja = efectivo / denom_corto_plazo
    ref_cobertura_operacional = utilidad_neta / denom_corto_plazo
    ref_z_altman = calcular_zem_altman(fila)

    return {
        # Variables predictivas ML (V1-V7)
        'v1_razon_corriente': round(v1, 4),
        'v2_capital_trabajo_activos': round(v2, 4),
        'v3_leverage_total': round(v3, 4),
        'v4_roa_operacional': round(v4, 4),
        'v5_margen_operacional': round(v5, 4),
        'v6_rotacion_activos': round(v6, 4),
        'v7_volatilidad_flujo': v7,
        'cierres_confirmados_count': cierres_count,
        'usa_volatilidad_neutra': usa_neutra,
        # Ratios contables de referencia
        'ref_prueba_acida': round(ref_prueba_acida, 4),
        'ref_razon_caja': round(ref_razon_caja, 4),
        'ref_cobertura_operacional': round(ref_cobertura_operacional, 4),
        'ref_z_altman': round(ref_z_altman, 4),
    }


def detectar_anomalias_financieras(objeto_financiero) -> List[Dict[str, Any]]:
    """
    [RF-10] Detecta valores fuera del rango predefinido de normalidad (outliers)
    o inconsistencias de signo en cuentas contables antes de ejecutar el modelo.

    Parámetros:
        objeto_financiero: Instancia de RatioFinanciero, CargaFinanciera o dict con cuentas y ratios.

    Retorna:
        Lista de diccionarios con las anomalías detectadas:
        - campo: Nombre entendible de la cuenta o ratio
        - valor: Valor numérico formateado
        - rango_esperado: Rango normal aceptable
        - motivo: Explicación de la anomalía o riesgo de distorsión
        - tipo: 'Outlier' o 'Signo Inválido'
        - severidad: 'warning' o 'danger'
    """
    anomalias = []
    if not objeto_financiero:
        return anomalias

    carga = getattr(objeto_financiero, 'upload', None) or (objeto_financiero if hasattr(objeto_financiero, 'total_assets') else None)
    ratio = objeto_financiero if hasattr(objeto_financiero, 'v1_current_ratio') else getattr(objeto_financiero, 'ratios', None)

    # 1. Validación de cuentas contables primarias (FinancialUpload)
    if carga:
        cuentas_no_negativas = [
            ('Efectivo y Equivalentes', getattr(carga, 'cash_and_equivalents', None), 'Caja y bancos no admiten saldo negativo; los descubiertos deben clasificarse en el pasivo corriente.'),
            ('Inventarios', getattr(carga, 'inventories', None), 'El saldo de existencias no puede ser negativo.'),
            ('Activo Circulante', getattr(carga, 'current_assets', None), 'El activo circulante no puede ser negativo.'),
            ('Pasivo Circulante', getattr(carga, 'current_liabilities', None), 'El pasivo circulante no puede ser negativo.'),
            ('Pasivo Total', getattr(carga, 'total_liabilities', None), 'El pasivo total exigible no puede ser negativo.'),
            ('Ingresos Netos (Ventas)', getattr(carga, 'net_revenue', None), 'Las ventas o ingresos de la operación no pueden ser negativos.'),
        ]

        for nombre_cuenta, val, motivo_neg in cuentas_no_negativas:
            if val is not None:
                val_float = float(val)
                if val_float < 0:
                    anomalias.append({
                        'campo': nombre_cuenta,
                        'valor': f"${val_float:,.2f}",
                        'rango_esperado': 'Mayor o igual a $0.00',
                        'motivo': motivo_neg,
                        'tipo': 'Signo Inválido',
                        'severidad': 'danger',
                    })

        # Activo total no puede ser cero ni negativo
        act_total = getattr(carga, 'total_assets', None)
        if act_total is not None and float(act_total) <= 0:
            anomalias.append({
                'campo': 'Activo Total',
                'valor': f"${float(act_total):,.2f}",
                'rango_esperado': 'Mayor a $0.00',
                'motivo': 'El activo total de la empresa debe ser estrictamente positivo.',
                'tipo': 'Signo Inválido',
                'severidad': 'danger',
            })

        # Margen EBITDA / Operacional desde cuentas brutas (EBIT vs Ingresos)
        ebit = getattr(carga, 'ebit', None)
        ingresos = getattr(carga, 'net_revenue', None)
        if ebit is not None and ingresos is not None:
            ebit_f = float(ebit)
            ing_f = float(ingresos)
            if ing_f > 0:
                margen_calc = ebit_f / ing_f
                if margen_calc > 1.0:
                    anomalias.append({
                        'campo': 'Margen Operacional / EBITDA',
                        'valor': f"{margen_calc * 100:.1f}%",
                        'rango_esperado': '-100% a 100%',
                        'motivo': f'Margen superior al 100%: el EBIT (${ebit_f:,.0f}) excede los ingresos totales (${ing_f:,.0f}), lo que indica un posible error de digitación o reclasificación contable.',
                        'tipo': 'Outlier Extremo',
                        'severidad': 'warning',
                    })
                elif margen_calc < -1.0:
                    anomalias.append({
                        'campo': 'Margen Operacional / EBITDA',
                        'valor': f"{margen_calc * 100:.1f}%",
                        'rango_esperado': '-100% a 100%',
                        'motivo': f'Pérdida operacional severa: el déficit operacional excede el 100% de la facturación.',
                        'tipo': 'Outlier Extremo',
                        'severidad': 'warning',
                    })

    # 2. Validación de Ratios Financieros calculados (FinancialRatio)
    if ratio and hasattr(ratio, 'v1_current_ratio'):
        # V1: Razón Corriente (rango normal típico: 0.20x a 8.00x)
        v1 = getattr(ratio, 'v1_current_ratio', None)
        if v1 is not None:
            v1_f = float(v1)
            if v1_f >= 8.0:
                anomalias.append({
                    'campo': 'Razón Corriente (V1)',
                    'valor': f"{v1_f:.2f}x",
                    'rango_esperado': '0.20x a 8.00x',
                    'motivo': 'Liquidez extremadamente alta: pasivo corriente subdeclarado o acumulación inusual de inventarios/caja.',
                    'tipo': 'Outlier',
                    'severidad': 'warning',
                })
            elif v1_f < 0.20:
                anomalias.append({
                    'campo': 'Razón Corriente (V1)',
                    'valor': f"{v1_f:.2f}x",
                    'rango_esperado': '0.20x a 8.00x',
                    'motivo': 'Liquidez crítica: activos de corto plazo cubren menos del 20% de las deudas inmediatas.',
                    'tipo': 'Outlier',
                    'severidad': 'warning',
                })

        # V3: Leverage Total (Pasivo Total / Patrimonio) (normal 0.0x a 7.0x)
        v3 = getattr(ratio, 'v3_total_leverage', None)
        if v3 is not None:
            v3_f = float(v3)
            if v3_f >= 7.0:
                anomalias.append({
                    'campo': 'Leverage Total (V3)',
                    'valor': f"{v3_f:.2f}x",
                    'rango_esperado': '0.00x a 7.00x',
                    'motivo': 'Endeudamiento desproporcionado: las deudas superan más de 7 veces el patrimonio contable.',
                    'tipo': 'Outlier',
                    'severidad': 'warning',
                })

        # V4: ROA Operacional (EBIT / Activo Total) (normal -50% a 50%)
        v4 = getattr(ratio, 'v4_operating_roa', None)
        if v4 is not None:
            v4_f = float(v4)
            if v4_f > 0.60 or v4_f < -0.60:
                anomalias.append({
                    'campo': 'ROA Operacional (V4)',
                    'valor': f"{v4_f * 100:.1f}%",
                    'rango_esperado': '-50% a 50%',
                    'motivo': 'Rentabilidad de activos atípica con respecto a la escala operacional del negocio.',
                    'tipo': 'Outlier',
                    'severidad': 'warning',
                })

        # V5: Margen Operacional si no se detectó en carga
        v5 = getattr(ratio, 'v5_operating_margin', None)
        if v5 is not None and not any(a['campo'].startswith('Margen Operacional') for a in anomalias):
            v5_f = float(v5)
            if v5_f >= 1.0 or v5_f <= -1.0:
                anomalias.append({
                    'campo': 'Margen Operacional (V5)',
                    'valor': f"{v5_f * 100:.1f}%",
                    'rango_esperado': '-100% a 100%',
                    'motivo': 'Margen operacional fuera de rango: excede el 100% de los ingresos ordinarios.',
                    'tipo': 'Outlier Extremo',
                    'severidad': 'warning',
                })

        # V6: Rotación de Activos (normal 0.05x a 6.00x)
        v6 = getattr(ratio, 'v6_asset_turnover', None)
        if v6 is not None:
            v6_f = float(v6)
            if v6_f > 6.0:
                anomalias.append({
                    'campo': 'Rotación de Activos (V6)',
                    'valor': f"{v6_f:.2f}x",
                    'rango_esperado': '0.05x a 6.00x',
                    'motivo': 'Rotación de activos inusualmente alta: ventas desproporcionadas respecto a la inversión en activos.',
                    'tipo': 'Outlier',
                    'severidad': 'warning',
                })

    return anomalias


# ==============================================================================
# PIPELINE DE EXTRACCIÓN Y VALIDACIÓN DE ARCHIVOS
# ==============================================================================

def extraer_dataframe_desde_archivo(archivo) -> Tuple[Optional[pd.DataFrame], List[str]]:
    """
    Extrae un DataFrame desde un archivo subido (.csv o .xlsx).
    Detecta automáticamente separadores (; o ,) y codificaciones (utf-8, latin-1).
    Aplica validación de tamaño máximo de 25 MB (RNF-10).
    """
    errores: List[str] = []
    nombre = getattr(archivo, 'name', '').lower()

    # Validación de tamaño máximo de 25 MB (RNF-10)
    MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024
    tamano = getattr(archivo, 'size', None)
    if tamano and tamano > MAX_FILE_SIZE_BYTES:
        tamano_mb = tamano / (1024 * 1024)
        errores.append(
            f"El archivo seleccionado pesa {tamano_mb:.2f} MB, superando el límite máximo permitido de 25 MB (RNF-10)."
        )
        return None, errores

    if not (nombre.endswith('.csv') or nombre.endswith('.xlsx')):
        errores.append("Formato no soportado. Por favor suba un archivo en formato .csv o .xlsx.")
        return None, errores

    try:
        if nombre.endswith('.csv'):
            contenido_bytes = archivo.read()
            archivo.seek(0)
            
            # Intento de decodificación utf-8, fallback a latin-1
            try:
                contenido_str = contenido_bytes.decode('utf-8')
            except UnicodeDecodeError:
                contenido_str = contenido_bytes.decode('latin-1')

            primera_linea = contenido_str.split('\n')[0] if contenido_str else ''
            separador = ';' if ';' in primera_linea else ','
            df = pd.read_csv(StringIO(contenido_str), sep=separador)
        else:
            df = pd.read_excel(archivo)

        return df, []
    except Exception as e:
        errores.append(f"Error al leer el archivo estructurado: {str(e)}")
        return None, errores


def validar_estructura_y_consistencia(df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame]:
    """
    Aplica las reglas de negocio y consistencia contable sobre el DataFrame:
    1. Existencia de las 13 columnas estandarizadas de la plantilla.
    2. Detección de celdas nulas o faltantes.
    3. Conversión numérica limpia (removiendo comas y espacios).
    4. Ecuación fundamental: Activo Total == Pasivo Total + Patrimonio Neto (+-1%).
    5. Subcomponentes: Activo Circulante <= Activo Total, Pasivo Circulante <= Pasivo Total.
    """
    errores: List[str] = []
    df_procesado = df.copy()

    # 1. Verificar columnas requeridas
    columnas_faltantes = [col for col in COLUMNAS_PLANTILLA if col not in df_procesado.columns]
    if columnas_faltantes:
        errores.append(f"El archivo no posee la estructura requerida. Columnas faltantes: {columnas_faltantes}")
        return False, errores, df_procesado

    # 2. Verificar celdas nulas en las columnas requeridas
    nulos = df_procesado[COLUMNAS_PLANTILLA].isnull().sum().sum()
    if nulos > 0:
        errores.append(
            f"Se detectaron {nulos} celda(s) vacía(s) o nulas. Por favor complete toda la información requerida."
        )
        return False, errores, df_procesado

    # 3. Conversión numérica y limpieza de formato
    for col in COLUMNAS_NUMERICAS:
        if not pd.api.types.is_numeric_dtype(df_procesado[col]):
            try:
                # Quitar comas de miles y espacios
                df_procesado[col] = (
                    df_procesado[col]
                    .astype(str)
                    .str.strip()
                    .str.replace(',', '', regex=False)
                    .astype(float)
                )
            except Exception:
                errores.append(f"La columna '{col}' contiene valores no numéricos o inválidos.")
                return False, errores, df_procesado

    # 4. Validación de la Ecuación Fundamental del Balance General
    # Activo = Pasivo + Patrimonio (con tolerancia de 1% del Activo Total, mín 1.0)
    tolerancia = (df_procesado['Activo_Total'].abs() * TOLERANCIA_DESCUADRE_PORCENTAJE).clip(
        lower=TOLERANCIA_DESCUADRE_MINIMA
    )
    diferencia = (df_procesado['Activo_Total'] - (df_procesado['Pasivo_Total'] + df_procesado['Patrimonio_Neto'])).abs()
    descuadradas = df_procesado[diferencia > tolerancia]

    if not descuadradas.empty:
        empresas_afectadas = descuadradas['Id_Empresa'].unique()
        filas = ', '.join(str(i + 2) for i in descuadradas.index[:5])
        errores.append(
            f"Descuadre contable detectado en {len(descuadradas)} fila(s) (filas: {filas}): "
            f"No cumplen la ecuación Activo = Pasivo + Patrimonio (tolerancia {TOLERANCIA_DESCUADRE_PORCENTAJE:.0%}). "
            f"Empresas: {', '.join(map(str, empresas_afectadas[:5]))}" + ('...' if len(empresas_afectadas) > 5 else '')
        )

    # 5. Validación de subcomponentes contables (RF-09: una parte no puede superar el total)
    for parte, total in (('Activo_Circulante', 'Activo_Total'), ('Pasivo_Circulante', 'Pasivo_Total')):
        invalidas = df_procesado[df_procesado[parte] > df_procesado[total] + TOLERANCIA_DESCUADRE_MINIMA]
        if not invalidas.empty:
            filas = ', '.join(str(i + 2) for i in invalidas.index[:5])
            errores.append(
                f"Inconsistencia contable: {parte} es mayor que {total} en {len(invalidas)} fila(s) (filas: {filas})."
            )

    if errores:
        return False, errores, df_procesado

    return True, [], df_procesado


# ==============================================================================
# PIPELINE DE CARGA (LOAD) Y PERSISTENCIA INTEGRAL
# ==============================================================================

def procesar_e_ingestar_balance(
    archivo,
    tipo_documento: str = 'Balance General',
    usuario_db: Optional[User] = None,
    empresa_default: Optional[Company] = None
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Ejecuta el pipeline completo de ETL:
    1. Extrae el archivo subido.
    2. Aplica validaciones contables y sintácticas.
    3. Persiste en FinancialUpload y FinancialRatio en una transacción atómica.
    4. Sincroniza el archivo CSV con UploadState para retrocompatibilidad con AppWeb.
    """
    # 1. Extracción
    df_raw, errores_lectura = extraer_dataframe_desde_archivo(archivo)
    if errores_lectura:
        return False, errores_lectura, {}

    # 2. Validación y Transformación
    es_valido, errores_validacion, df = validar_estructura_y_consistencia(df_raw)
    if not es_valido:
        return False, errores_validacion, {}

    cargas_creadas = []
    ratios_creados = []
    fecha_ahora = timezone.now()
    nombre_archivo = getattr(archivo, 'name', 'archivo_subido')

    try:
        with transaction.atomic():
            for _, fila in df.iterrows():
                fila_dict = fila.to_dict()
                id_empresa_raw = str(fila_dict.get('Id_Empresa', '')).strip()

                # Resolver la Empresa asignada (prioridad absoluta a la empresa del usuario)
                empresa_obj = empresa_default or (usuario_db.company if usuario_db else None)
                if not empresa_obj and id_empresa_raw:
                    empresa_obj, _ = Company.objects.get_or_create(
                        tax_id=id_empresa_raw,
                        defaults={'business_name': f"Empresa {id_empresa_raw}"}
                    )

                # 3. Crear registro en FinancialUpload
                carga = FinancialUpload.objects.create(
                    upload_date=fecha_ahora,
                    period=str(fila_dict.get('Periodo', 'N/A')).strip(),
                    source_file=nombre_archivo,
                    upload_type=tipo_documento,
                    current_assets=Decimal(str(round(float(fila_dict['Activo_Circulante']), 2))),
                    current_liabilities=Decimal(str(round(float(fila_dict['Pasivo_Circulante']), 2))),
                    total_assets=Decimal(str(round(float(fila_dict['Activo_Total']), 2))),
                    total_liabilities=Decimal(str(round(float(fila_dict['Pasivo_Total']), 2))),
                    equity=Decimal(str(round(float(fila_dict['Patrimonio_Neto']), 2))),
                    net_revenue=Decimal(str(round(float(fila_dict['Ingresos_Netos']), 2))),
                    ebit=Decimal(str(round(float(fila_dict['EBIT']), 2))),
                    retained_earnings=Decimal(str(round(float(fila_dict['Utilidades_Retenidas']), 2))),
                    net_income=Decimal(str(round(float(fila_dict['Utilidad_Neta']), 2))),
                    inventories=Decimal(str(round(float(fila_dict['Inventarios']), 2))),
                    cash_and_equivalents=Decimal(str(round(float(fila_dict['Efectivo_Equivalentes']), 2))),
                    status='PROCESADO',
                    detected_errors=None,
                    user=usuario_db,
                    company=empresa_obj,
                )
                cargas_creadas.append(carga)

                # 4. Calcular ratios completos y crear registro en FinancialRatio
                ratios_data = calcular_indicadores_completos(fila_dict, empresa=empresa_obj)

                ratio = FinancialRatio.objects.create(
                    upload=carga,
                    period=carga.period,
                    calculation_date=fecha_ahora,
                    v1_current_ratio=Decimal(str(ratios_data['v1_razon_corriente'])),
                    v2_working_capital_to_assets=Decimal(str(ratios_data['v2_capital_trabajo_activos'])),
                    v3_total_leverage=Decimal(str(ratios_data['v3_leverage_total'])),
                    v4_operating_roa=Decimal(str(ratios_data['v4_roa_operacional'])),
                    v5_operating_margin=Decimal(str(ratios_data['v5_margen_operacional'])),
                    v6_asset_turnover=Decimal(str(ratios_data['v6_rotacion_activos'])),
                    v7_cash_flow_volatility=Decimal(str(ratios_data['v7_volatilidad_flujo'])) if ratios_data['v7_volatilidad_flujo'] is not None else None,
                    confirmed_closures_count=ratios_data['cierres_confirmados_count'],
                    uses_neutral_volatility=ratios_data['usa_volatilidad_neutra'],
                    ref_quick_ratio=Decimal(str(ratios_data['ref_prueba_acida'])),
                    ref_cash_ratio=Decimal(str(ratios_data['ref_razon_caja'])),
                    ref_operating_coverage=Decimal(str(ratios_data['ref_cobertura_operacional'])),
                    ref_altman_z_score=Decimal(str(ratios_data['ref_z_altman'])),
                    is_validated=True,
                    validated_by_user=usuario_db,
                    validation_date=fecha_ahora,
                    company=empresa_obj,
                )
                ratios_creados.append(ratio)

            # 5. Guardar copia en CSV sincronizada con UploadState (Retrocompatibilidad AppWeb)
            archivo_id = str(uuid.uuid4())
            ruta_csv = os.path.join(DATA_DIR, f"{archivo_id}.csv")
            df.to_csv(ruta_csv, index=False)

            estado = UploadState.current()
            estado.csv_path = ruta_csv
            estado.save()

        # Conteo de anomalías u outliers detectados en los ratios procesados (RF-10)
        total_anomalias = 0
        for r in ratios_creados:
            total_anomalias += len(detectar_anomalias_financieras(r))

        resumen = {
            'total_registros': len(df),
            'cargas_creadas': len(cargas_creadas),
            'ratios_creados': len(ratios_creados),
            'anomalias_detectadas': total_anomalias,
            'ruta_csv': ruta_csv,
            'nombre_archivo': nombre_archivo,
        }
        return True, [], resumen

    except Exception as e:
        logger.exception("Fallo inesperado durante la persistencia contable en ETL: %s", e)
        return False, [
            "Ocurrió un problema temporal al procesar y almacenar la información del documento contable. "
            "Por favor, verifique el archivo e intente la carga nuevamente."
        ], {}


def limpiar_archivos_y_estado() -> bool:
    """
    Elimina los archivos CSV temporales de la carpeta data/ y reinicia el UploadState.
    """
    try:
        estado = UploadState.current()
        if estado.csv_path and os.path.exists(estado.csv_path):
            try:
                os.remove(estado.csv_path)
            except OSError:
                pass
        estado.csv_path = None
        estado.save()
        return True
    except Exception:
        return False


def generar_plantilla_ejemplo_csv() -> bytes:
    """
    Genera en memoria un archivo CSV de ejemplo con la estructura oficial
    y una fila con datos contables consistentes y balanceados.
    """
    datos_ejemplo = [
        {
            'Id_Empresa': '76.123.456-7',
            'Periodo': '2025-Q4',
            'Activo_Circulante': 50000000.0,
            'Pasivo_Circulante': 25000000.0,
            'Efectivo_Equivalentes': 15000000.0,
            'Inventarios': 18000000.0,
            'Activo_Total': 120000000.0,
            'Pasivo_Total': 45000000.0,
            'Patrimonio_Neto': 75000000.0,
            'Utilidad_Neta': 12500000.0,
            'Ingresos_Netos': 140000000.0,
            'EBIT': 18000000.0,
            'Utilidades_Retenidas': 22000000.0,
        },
        {
            'Id_Empresa': '76.123.456-7',
            'Periodo': '2026-Q1',
            'Activo_Circulante': 55000000.0,
            'Pasivo_Circulante': 27000000.0,
            'Efectivo_Equivalentes': 18000000.0,
            'Inventarios': 20000000.0,
            'Activo_Total': 130000000.0,
            'Pasivo_Total': 48000000.0,
            'Patrimonio_Neto': 82000000.0,
            'Utilidad_Neta': 14000000.0,
            'Ingresos_Netos': 155000000.0,
            'EBIT': 21000000.0,
            'Utilidades_Retenidas': 26000000.0,
        }
    ]
    df_ejemplo = pd.DataFrame(datos_ejemplo)
    return df_ejemplo.to_csv(index=False, sep=';').encode('utf-8')

