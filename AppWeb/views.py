from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from io import StringIO
import pandas as pd
import uuid
import os

from .viewsML import calcular_score_compuesto, obtener_metricas, analizar_contribucion_riesgo
from .fetch_capm_data import (
    get_tasa_libre_riesgo,
    get_prima_riesgo_mercado,
    get_sectores_beta,
    DEFAULT_SECTORES_BETA,
)

COLUMNAS_PLANTILLA = [
    'Id_Empresa', 'Periodo', 'Activo_Circulante', 'Pasivo_Circulante',
    'Efectivo_Equivalentes', 'Inventarios', 'Activo_Total',
    'Pasivo_Total', 'Patrimonio_Neto', 'Utilidad_Neta'
]

COLUMNAS_NUMERICAS = COLUMNAS_PLANTILLA[2:]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def home(request: HttpRequest):
    contexto = {
        'paso_1': bool(request.session.get('datos_cargados')),
        'paso_2': bool(request.session.get('beta_capm')),
    }
    return render(request, 'AppWeb/index.html', contexto)

def carga_datos(request: HttpRequest):
    if request.method == 'POST':
        if 'archivo_datos' not in request.FILES:
            messages.error(request, 'No se seleccionó ningún archivo.')
            return render(request, 'AppWeb/cargaDatos.html')

        archivo = request.FILES['archivo_datos']
        tipo_documento = request.POST.get('tipo_documento')

        if not (archivo.name.endswith('.csv') or archivo.name.endswith('.xlsx')):
            messages.error(request, 'Formato no soportado. Por favor suba un archivo .csv o .xlsx')
            return render(request, 'AppWeb/cargaDatos.html')

        try:
            if archivo.name.endswith('.csv'):
                contenido = archivo.read().decode('utf-8')
                primera_linea = contenido.split('\n')[0]
                separador = ';' if ';' in primera_linea else ','
                df = pd.read_csv(StringIO(contenido), sep=separador)
            else:
                df = pd.read_excel(archivo)

            errores = []
            columnas_faltantes = [c for c in COLUMNAS_PLANTILLA if c not in df.columns]

            if columnas_faltantes:
                errores.append(f"El archivo no posee la estructura correcta. Faltan columnas: {columnas_faltantes}")
            else:
                nulos = df[COLUMNAS_PLANTILLA].isnull().sum().sum()
                if nulos > 0:
                    errores.append(f"Se detectaron {nulos} celda(s) vacía(s) o nulas. Complete toda la información requerida.")
                else:
                    for col in COLUMNAS_NUMERICAS:
                        if not pd.api.types.is_numeric_dtype(df[col]):
                            try:
                                df[col] = df[col].astype(str).str.replace(',', '', regex=False).astype(float)
                            except Exception:
                                errores.append(f"La columna '{col}' contiene valores no numéricos.")
                                break

            if errores:
                for e in errores:
                    messages.error(request, e)
                messages.warning(request, 'El archivo no fue guardado. Corrija los errores y vuelva a intentar.')
            else:
                if tipo_documento == 'balance':
                    df['_diferencia'] = abs(df['Activo_Total'] - (df['Pasivo_Total'] + df['Patrimonio_Neto']))
                    descuadradas = df[df['_diferencia'] > 0.01]
                    if not descuadradas.empty:
                        empresas = descuadradas['Id_Empresa'].unique()
                        msj = f"Advertencia: {len(descuadradas)} fila(s) no cumplen la ecuación Activo = Pasivo + Patrimonio. Empresas: {', '.join(map(str, empresas[:5]))}"
                        if len(empresas) > 5:
                            msj += '...'
                        messages.warning(request, msj)
                    df.drop(columns=['_diferencia'], inplace=True)

                archivo_id = str(uuid.uuid4())
                ruta_csv = os.path.join(DATA_DIR, f'{archivo_id}.csv')
                df.to_csv(ruta_csv, index=False)
                request.session['datos_cargados'] = ruta_csv
                request.session['empresas_disponibles'] = df['Id_Empresa'].unique().tolist()
                messages.success(request, f'¡Archivo "{archivo.name}" validado correctamente! {len(df)} registros cargados.')

        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {e}')

        return render(request, 'AppWeb/cargaDatos.html')

    return render(request, 'AppWeb/cargaDatos.html')

def calculo_capm(request: HttpRequest):
    try:
        tasa_libre_riesgo, fuente_rf = get_tasa_libre_riesgo()
        prima_riesgo_mercado, fuente_erp = get_prima_riesgo_mercado()
        sectores_beta, fuente_betas = get_sectores_beta()
    except Exception:
        tasa_libre_riesgo, fuente_rf = 4.5, 'Valor por defecto'
        prima_riesgo_mercado, fuente_erp = 6.0, 'Valor por defecto'
        sectores_beta, fuente_betas = DEFAULT_SECTORES_BETA, 'Valor por defecto'
        messages.warning(request, 'No se pudieron obtener datos actualizados desde internet. Se usaron los valores asignados por defecto.')

    contexto = {
        'sectores': sectores_beta.keys(),
        'fuente_rf': fuente_rf,
        'fuente_erp': fuente_erp,
        'fuente_betas': fuente_betas,
        'tasa_libre_riesgo': tasa_libre_riesgo,
        'prima_riesgo_mercado': prima_riesgo_mercado,
    }

    if request.method == 'POST':
        sector_seleccionado = request.POST.get('sector')

        if sector_seleccionado in sectores_beta:
            beta_mercado = sectores_beta[sector_seleccionado]

            costo_patrimonio = tasa_libre_riesgo + (beta_mercado * prima_riesgo_mercado)

            request.session['beta_capm'] = beta_mercado

            contexto['sector_seleccionado'] = sector_seleccionado
            contexto['beta'] = beta_mercado
            contexto['costo_patrimonio'] = round(costo_patrimonio, 2)

            messages.success(request, f'Se ha asignado el coeficiente Beta de {beta_mercado} para el sector {sector_seleccionado}.')
        else:
            messages.error(request, 'Por favor, seleccione un sector industrial válido.')

    return render(request, 'AppWeb/capm.html', contexto)

def calcular_ratios_liquidez(row: dict):
    activo_circulante = row.get('Activo_Circulante', 0)
    pasivo_circulante = row.get('Pasivo_Circulante',0)
    inventario = row.get('Inventarios',0)
    caja_y_bancos = row.get('Efectivo_Equivalentes',0)
    flujo_caja_operativo = row.get('Utilidad_Neta',0)
    pasivo_total = row.get('Pasivo_Total',0)
    activo_total = row.get('Activo_Total',0)

    eps = 1e-6
    denom = pasivo_circulante if pasivo_circulante > 0 else eps

    ratios = {
        'razon_corriente': activo_circulante / denom,
        'prueba_acida': (activo_circulante - inventario) / denom,
        'ratio_caja': caja_y_bancos / denom,
        'cobertura_operacional': flujo_caja_operativo / denom,
        'capital_trabajo': activo_circulante - pasivo_circulante,
        'endeudamiento_corto_plazo': pasivo_circulante / (pasivo_total if pasivo_total > 0 else eps),
        'liquidez_inmediata': caja_y_bancos / denom,
        'solvencia_general': activo_total / (pasivo_total if pasivo_total > 0 else eps)
    }

    return {k: round(v, 4) for k, v in ratios.items()}


def ejecutar_prediccion(request: HttpRequest):
    if request.method == 'POST':
        try:
            ruta_csv = request.session.get('datos_cargados')
            if not ruta_csv:
                messages.error(request, 'No hay datos cargados. Cargue un archivo primero.')
                return redirect('carga_datos')

            if not os.path.exists(ruta_csv):
                messages.error(request, 'Los datos han expirado. Cargue un archivo nuevamente.')
                return redirect('carga_datos')

            df = pd.read_csv(ruta_csv)

            empresa_id = request.POST.get('empresa_id', df['Id_Empresa'].iloc[0])
            df_empresa = df[df['Id_Empresa'] == empresa_id]
            if df_empresa.empty:
                df_empresa = df.iloc[[0]]
                empresa_id = df['Id_Empresa'].iloc[0]

            row = df_empresa.iloc[0]
            ratios_empresa = calcular_ratios_liquidez(row)

            beta_sector = request.session.get('beta_capm', 0.85)

            puntaje_riesgo = calcular_score_compuesto(ratios_empresa)
            if puntaje_riesgo <= 35:
                riesgo, color = 'Bajo', 'Verde'
            elif puntaje_riesgo <= 70:
                riesgo, color = 'Moderado', 'Amarillo'
            else:
                riesgo, color = 'Crítico', 'Rojo'

            metricas_modelo = obtener_metricas(ruta_csv)

            top_3_riesgo = analizar_contribucion_riesgo(ratios_empresa)

            messages.success(request, f'Análisis predictivo completado para {empresa_id}.')

            contexto = {
                'ratios': ratios_empresa,
                'beta': beta_sector,
                'score': puntaje_riesgo,
                'riesgo': riesgo,
                'color': color,
                'empresa_id': empresa_id,
                'top_3_riesgo': top_3_riesgo,
            }
            contexto.update(metricas_modelo)
            return render(request, 'AppWeb/resultado_prediccion.html', contexto)

        except Exception as e:
            messages.error(request, f"Error en la predicción: {str(e)}")
            return redirect('home')

    return redirect('home')


def limpiar_datos(request: HttpRequest):
    if request.method == 'POST':
        ruta_csv = request.session.pop('datos_cargados', None)
        if ruta_csv and os.path.exists(ruta_csv):
            os.remove(ruta_csv)
        request.session.pop('beta_capm', None)
        request.session.pop('empresas_disponibles', None)
        messages.success(request, 'Datos y configuración eliminados correctamente.')
    return redirect('home')


