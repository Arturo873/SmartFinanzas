from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from io import StringIO, BytesIO
from xhtml2pdf import pisa
import pandas as pd
import uuid
import os

from .viewsML import (
    obtener_metricas_modelo_oficial,
    predecir_probabilidades,
    predecir_riesgo,
    analizar_contribucion_riesgo,
    obtener_recomendacion_general,
    ruta_cache_modelo,
)
from .datos_macro import obtener_contexto_macro
from .variables_modelo import VARIABLES_MODELO, calcular_variables_modelo
from .models import Empresa, HistorialPrediccion, PerfilUsuario, EstadoCarga
from .decorators import rol_requerido

COLUMNAS_PLANTILLA = [
    'Id_Empresa', 'Periodo', 'Activo_Circulante', 'Pasivo_Circulante',
    'Efectivo_Equivalentes', 'Inventarios', 'Activo_Total',
    'Pasivo_Total', 'Patrimonio_Neto', 'Utilidad_Neta',
    # Requerimientos v8 (RF-08): V4, V5, V6 y el Z-score de Altman.
    'Ingresos_Netos', 'EBIT', 'Utilidades_Retenidas',
]

COLUMNAS_NUMERICAS = COLUMNAS_PLANTILLA[2:]

TOLERANCIA_DESCUADRE_PORCENTAJE = 0.01  # 1% del Activo Total
TOLERANCIA_DESCUADRE_MINIMA = 1.0  # monto mínimo absoluto, evita falsos positivos con Activo_Total = 0

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Bienvenido, {request.user.username}.')
        return redirect('home')

    return render(request, 'AppWeb/login.html', {'form': form})


def logout_view(request: HttpRequest):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


def registro_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        rol = request.POST.get('rol')

        if not username or not password or rol not in dict(PerfilUsuario.ROLES):
            messages.error(request, 'Completa usuario, contraseña y selecciona un rol válido.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya existe.')
        else:
            user = User.objects.create_user(username=username, password=password)
            PerfilUsuario.objects.create(user=user, rol=rol)
            login(request, user)
            messages.success(request, f'Cuenta creada como {rol}. ¡Bienvenido!')
            return redirect('home')

    return render(request, 'AppWeb/registro.html', {'roles': PerfilUsuario.ROLES})


@login_required(login_url='login')
def home(request: HttpRequest):
    perfil = getattr(request.user, 'perfil', None)
    estado = EstadoCarga.actual()
    contexto = {
        'paso_1': bool(estado.ruta_csv and os.path.exists(estado.ruta_csv)),
        'rol': perfil.rol if perfil else None,
    }
    return render(request, 'AppWeb/index.html', contexto)

def _contexto_carga():
    return {
        'datos_cargados': bool(EstadoCarga.actual().ruta_csv),
        'columnas_plantilla': COLUMNAS_PLANTILLA,
    }


@rol_requerido(PerfilUsuario.ROL_CONTADOR)
def carga_datos(request: HttpRequest):
    if request.method == 'POST':
        if 'archivo_datos' not in request.FILES:
            messages.error(request, 'No se seleccionó ningún archivo.')
            return render(request, 'AppWeb/cargaDatos.html', _contexto_carga())

        archivo = request.FILES['archivo_datos']
        tipo_documento = request.POST.get('tipo_documento')

        if not (archivo.name.endswith('.csv') or archivo.name.endswith('.xlsx')):
            messages.error(request, 'Formato no soportado. Por favor suba un archivo .csv o .xlsx')
            return render(request, 'AppWeb/cargaDatos.html', _contexto_carga())

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

                    if not errores:
                        tolerancia = (df['Activo_Total'].abs() * TOLERANCIA_DESCUADRE_PORCENTAJE).clip(lower=TOLERANCIA_DESCUADRE_MINIMA)
                        diferencia = (df['Activo_Total'] - (df['Pasivo_Total'] + df['Patrimonio_Neto'])).abs()
                        descuadradas = df[diferencia > tolerancia]
                        if not descuadradas.empty:
                            empresas = descuadradas['Id_Empresa'].unique()
                            errores.append(
                                f"Descuadre contable: {len(descuadradas)} fila(s) no cumplen la ecuación "
                                f"Activo = Pasivo + Patrimonio (tolerancia {TOLERANCIA_DESCUADRE_PORCENTAJE:.0%} del Activo Total). "
                                f"Empresas: {', '.join(map(str, empresas[:5]))}" + ('...' if len(empresas) > 5 else '')
                            )

                        # RF-09 v8: una parte no puede superar al total.
                        for parte, total in (('Activo_Circulante', 'Activo_Total'), ('Pasivo_Circulante', 'Pasivo_Total')):
                            invalidas = df[df[parte] > df[total] + TOLERANCIA_DESCUADRE_MINIMA]
                            if not invalidas.empty:
                                filas = ', '.join(str(i + 2) for i in invalidas.index[:5])
                                errores.append(
                                    f"Descuadre contable: {parte} es mayor que {total} en {len(invalidas)} fila(s). "
                                    f"Filas del archivo: {filas}" + ('...' if len(invalidas) > 5 else '')
                                )

            if errores:
                for e in errores:
                    messages.error(request, e)
                messages.warning(request, 'El archivo no fue guardado. Corrija los errores y vuelva a intentar.')
            else:
                archivo_id = str(uuid.uuid4())
                ruta_csv = os.path.join(DATA_DIR, f'{archivo_id}.csv')
                df.to_csv(ruta_csv, index=False)
                estado = EstadoCarga.actual()
                estado.ruta_csv = ruta_csv
                estado.save()
                messages.success(request, f'¡Archivo "{archivo.name}" validado correctamente! {len(df)} registros cargados.')

        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {e}')

        return render(request, 'AppWeb/cargaDatos.html', _contexto_carga())

    return render(request, 'AppWeb/cargaDatos.html', _contexto_carga())

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
    denom_activo = activo_total if activo_total > 0 else eps

    ratios = {
        'razon_corriente': activo_circulante / denom,
        'prueba_acida': (activo_circulante - inventario) / denom,
        'ratio_caja': caja_y_bancos / denom,
        'cobertura_operacional': flujo_caja_operativo / denom,
        'capital_trabajo': activo_circulante - pasivo_circulante,
        'endeudamiento_corto_plazo': pasivo_circulante / (pasivo_total if pasivo_total > 0 else eps),
        'solvencia_general': activo_total / (pasivo_total if pasivo_total > 0 else eps),
        # Alimentan al modelo real (modelo_oficial); ver
        # DatasetEntrenamientoML/entrenar_modelo_oficial.py -> RATIOS_MODELO.
        'rentabilidad_activos': flujo_caja_operativo / denom_activo,
        'capital_trabajo_sobre_activos': (activo_circulante - pasivo_circulante) / denom_activo,
    }

    return {k: round(v, 4) for k, v in ratios.items()}


def calcular_tendencia_periodos(df: pd.DataFrame) -> list:
    contextos_macro = {periodo: obtener_contexto_macro(periodo) for periodo in df['Periodo'].unique()}
    variables_por_fila = [
        calcular_variables_modelo(fila, contextos_macro[fila['Periodo']])
        for fila in df.to_dict('records')
    ]
    scores_por_fila = predecir_probabilidades(variables_por_fila) * 100

    df_scores = df.assign(_score=scores_por_fila)
    promedio = df_scores.groupby('Periodo')['_score'].mean().round(1)
    return [
        {'periodo': periodo, 'score_promedio': valor}
        for periodo, valor in sorted(promedio.items())
    ]


@rol_requerido(PerfilUsuario.ROL_DUENO)
def ejecutar_prediccion(request: HttpRequest):
    if request.method == 'POST':
        try:
            estado = EstadoCarga.actual()
            ruta_csv = estado.ruta_csv
            if not ruta_csv:
                messages.error(request, 'No hay datos cargados. Pide al Contador que cargue un archivo primero.')
                return redirect('home')

            if not os.path.exists(ruta_csv):
                messages.error(request, 'Los datos han expirado. Pide al Contador que cargue el archivo nuevamente.')
                return redirect('home')

            df = pd.read_csv(ruta_csv)

            empresa_id = request.POST.get('empresa_id', df['Id_Empresa'].iloc[0])
            df_empresa = df[df['Id_Empresa'] == empresa_id]
            if df_empresa.empty:
                df_empresa = df.iloc[[0]]
                empresa_id = df['Id_Empresa'].iloc[0]

            row = df_empresa.iloc[0]
            ratios_empresa = calcular_ratios_liquidez(row)

            # Las 8 variables del modelo v8 (RF-10). V7 queda en el valor
            # neutro porque el módulo de caja (RF-19 a RF-22) aún no está
            # implementado.
            contexto_macro = obtener_contexto_macro(row['Periodo'])
            variables_modelo = calcular_variables_modelo(row.to_dict(), contexto_macro)
            tabla_variables_modelo = [
                {'clave': clave, 'nombre': nombre, 'grupo': grupo, 'valor': variables_modelo[clave]}
                for clave, nombre, grupo in VARIABLES_MODELO
            ]

            puntaje_riesgo, riesgo, color = predecir_riesgo(variables_modelo)

            metricas_modelo = obtener_metricas_modelo_oficial()

            top_3_riesgo = analizar_contribucion_riesgo(variables_modelo)
            recomendacion_general = obtener_recomendacion_general(color)

            empresa, _ = Empresa.objects.get_or_create(
                rut=str(empresa_id), defaults={'nombre': str(empresa_id)}
            )
            HistorialPrediccion.objects.create(
                empresa=empresa,
                score=puntaje_riesgo,
                riesgo=color,
                razon_corriente=ratios_empresa.get('razon_corriente'),
                prueba_acuda=ratios_empresa.get('prueba_acida'),
            )
            historial_empresa = [
                {'fecha': h.fecha_prediccion.strftime('%d-%m-%Y %H:%M'), 'score': h.score}
                for h in HistorialPrediccion.objects.filter(empresa=empresa).order_by('fecha_prediccion')
            ]

            tendencia_periodos = calcular_tendencia_periodos(df)

            messages.success(request, f'Análisis predictivo completado para {empresa_id}.')

            contexto = {
                'ratios': ratios_empresa,
                'variables_modelo': tabla_variables_modelo,
                'contexto_macro': contexto_macro,
                'periodo': row['Periodo'],
                'score': puntaje_riesgo,
                'riesgo': riesgo,
                'color': color,
                'empresa_id': empresa_id,
                'top_3_riesgo': top_3_riesgo,
                'recomendacion_general': recomendacion_general,
                'historial_empresa': historial_empresa,
                'tendencia_periodos': tendencia_periodos,
                'modelo_info': {
                    'dataset': 'Datos sintéticos generados desde empresas chilenas reales (CMF)',
                    'split': 'Prueba: 20% del dataset sintético y empresas CMF no usadas al entrenar',
                    'version': 'v8',
                },
            }
            contexto.update(metricas_modelo)
            request.session['ultimo_resultado'] = contexto
            return render(request, 'AppWeb/resultado_prediccion.html', contexto)

        except Exception as e:
            messages.error(request, f"Error en la predicción: {str(e)}")
            return redirect('home')

    return redirect('home')


@rol_requerido(PerfilUsuario.ROL_DUENO)
def exportar_pdf(request: HttpRequest):
    contexto = request.session.get('ultimo_resultado')
    if not contexto:
        messages.error(request, 'No hay una predicción reciente para exportar. Ejecuta una predicción primero.')
        return redirect('home')

    html = render_to_string('AppWeb/resultado_prediccion_pdf.html', contexto)

    buffer = BytesIO()
    pisa.CreatePDF(src=html, dest=buffer)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    nombre_archivo = f"informe_riesgo_{contexto.get('empresa_id', 'empresa')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


@rol_requerido(PerfilUsuario.ROL_CONTADOR)
def limpiar_datos(request: HttpRequest):
    if request.method == 'POST':
        estado = EstadoCarga.actual()
        if estado.ruta_csv and os.path.exists(estado.ruta_csv):
            ruta_cache = ruta_cache_modelo(estado.ruta_csv)
            if os.path.exists(ruta_cache):
                os.remove(ruta_cache)
            os.remove(estado.ruta_csv)
        estado.ruta_csv = None
        estado.save()
        request.session.pop('ultimo_resultado', None)
        messages.success(request, 'Datos eliminados correctamente.')
    return redirect('home')


