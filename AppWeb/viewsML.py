import os
import numpy as np
import pandas as pd
import joblib

from .variables_modelo import VARIABLES_MODELO

# Random Forest entrenado desde cero solo con empresas chilenas reales de la
# CMF (RNF-08), por DatasetSinteticoEntrenamientoML/paso3_entrenar_evaluar.py.
# Recibe las 7 variables de AppWeb/variables_modelo.py.
MODELO_OFICIAL_DIR = os.path.join(os.path.dirname(__file__), 'modelo_oficial')
_modelo_oficial_cache = {}


def _cargar_modelo_oficial():
    if not _modelo_oficial_cache:
        from django.conf import settings
        nombre_config = (
            getattr(settings, 'MODELO_ML_NOMBRE', None)
            or getattr(settings, 'ML_MODEL_NAME', None)
            or 'ModeloSmartfinanzas.joblib'
        )
        nombres = [nombre_config]
        if not nombre_config.endswith(('.joblib', '.pkl')):
            nombres.extend([f"{nombre_config}.joblib", f"{nombre_config}.pkl"])
        else:
            nombres.append(os.path.splitext(nombre_config)[0])
        for extra in ['ModeloSmartfinanzas.joblib', 'ModeloSmartfinanzas']:
            if extra not in nombres:
                nombres.append(extra)

        ruta_modelo = None
        for n in nombres:
            candidatos = [
                os.path.join(MODELO_OFICIAL_DIR, n),
                os.path.join(str(settings.BASE_DIR), 'capaAnalitica', 'modelo', n),
                os.path.join(str(settings.BASE_DIR), 'capaAnalitica', n),
                os.path.join(str(settings.BASE_DIR), n),
            ]
            for cand in candidatos:
                if os.path.exists(cand):
                    ruta_modelo = cand
                    break
            if ruta_modelo:
                break

        if not ruta_modelo:
            # Respaldo histórico
            for resp in ['modelo_riesgo_v11.joblib', 'random_forest_model.joblib']:
                cand1 = os.path.join(MODELO_OFICIAL_DIR, resp)
                cand2 = os.path.join(str(settings.BASE_DIR), 'capaAnalitica', 'modelo', resp)
                if os.path.exists(cand1):
                    ruta_modelo = cand1
                    break
                elif os.path.exists(cand2):
                    ruta_modelo = cand2
                    break

        if not ruta_modelo:
            ruta_modelo = os.path.join(MODELO_OFICIAL_DIR, 'ModeloSmartfinanzas.joblib')

        _modelo_oficial_cache['clf'] = joblib.load(ruta_modelo)
        _modelo_oficial_cache['metricas'] = joblib.load(os.path.join(MODELO_OFICIAL_DIR, 'metricas_v11.joblib'))
    return _modelo_oficial_cache['clf'], _modelo_oficial_cache['metricas']


def obtener_metricas_modelo_oficial() -> dict:
    """Métricas fijas del modelo entrenado (RNF-08), medidas en empresas reales
    de la CMF que el modelo nunca vio y sin datos de caja (V7 neutra), que es
    la situación actual del sistema."""
    _, metricas = _cargar_modelo_oficial()
    real = metricas['metricas_prueba_real_sin_caja']
    return {
        'accuracy': round(real['accuracy'] * 100, 1),
        'recall': round(real['recall_insolvente'] * 100, 1),
        'f1_score': round(real['f1'] * 100, 1),
        'pr_auc': round(real['pr_auc'] * 100, 1),
        'total_empresas': metricas['total_empresas_entrenamiento'],
    }


def _vectores(lista_variables: list) -> pd.DataFrame:
    """Matriz de entrada del modelo. V7 sin datos de caja toma el valor neutro
    (mediana de las empresas solventes), para no empujar la predicción hacia
    ninguna clase (RNF-10)."""
    _, metricas = _cargar_modelo_oficial()
    neutros = {'volatilidad_flujo_caja': metricas['volatilidad_neutra']}
    orden = metricas['features_orden']
    return pd.DataFrame(
        [[v[clave] if v[clave] is not None else neutros[clave] for clave in orden] for v in lista_variables],
        columns=orden, dtype=float,
    )


def predecir_probabilidades(lista_variables: list) -> np.ndarray:
    """Probabilidad de insolvencia (0-1) para varias empresas a la vez."""
    clf, _ = _cargar_modelo_oficial()
    df = _vectores(lista_variables)
    X = df.values if getattr(clf, 'feature_names_in_', None) is None else df
    return clf.predict_proba(X)[:, 1]


def clasificar_puntaje(puntaje_riesgo: float):
    if puntaje_riesgo <= 35:
        return 'Bajo', 'Verde'
    elif puntaje_riesgo <= 70:
        return 'Moderado', 'Amarillo'
    return 'Crítico', 'Rojo'


def predecir_riesgo(variables: dict):
    """Devuelve (puntaje_riesgo 0-100, etiqueta 'Bajo'/'Moderado'/'Crítico', color)."""
    puntaje_riesgo = round(float(predecir_probabilidades([variables])[0]) * 100, 1)
    return (puntaje_riesgo, *clasificar_puntaje(puntaje_riesgo))


# Explicación y consejo por variable (RF-03) y por grupo (RF-05). Los umbrales
# citados están en documentacion/fuentes_modelo_ml.md.
EXPLICACIONES = {
    'razon_corriente': {
        'label': 'Razón Corriente',
        'formato': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Tu activo corriente cubre {v:.2f} veces tu pasivo corriente. Bajo 1,0 las deudas de corto plazo '
            'superan a los recursos de corto plazo, y bajo 0,5 la capacidad de pago es baja (Riquelme, 2018).'
        ),
    },
    'capital_trabajo_sobre_activos': {
        'label': 'Capital de Trabajo sobre Activos',
        'formato': lambda v: f'{v:.1%}',
        'explicacion': lambda v: (
            f'Tu capital de trabajo equivale al {v:.1%} de tus activos totales. Un valor negativo indica que '
            'las deudas de corto plazo superan a los activos corrientes (Altman, 1968).'
        ),
    },
    'leverage_total': {
        'label': 'Leverage Total',
        'formato': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Tus deudas equivalen a {v:.2f} veces tu patrimonio. Bajo 1,0 indica buena capacidad de pago y '
            'sobre 5,0 es un endeudamiento alto (Riquelme, 2018). El valor máximo se asigna con patrimonio negativo.'
        ),
    },
    'roa_operacional': {
        'label': 'ROA Operacional',
        'formato': lambda v: f'{v:.1%}',
        'explicacion': lambda v: (
            f'Tu resultado operacional (EBIT) equivale al {v:.1%} de tus activos. Un valor negativo indica que '
            'la operación no genera rentabilidad sobre lo invertido (Altman, 1968).'
        ),
    },
    'margen_operacional': {
        'label': 'Margen Operacional',
        'formato': lambda v: f'{v:.1%}',
        'explicacion': lambda v: (
            f'Por cada $100 de ventas te quedan ${v * 100:.1f} de resultado operacional. Un margen bajo 8% refleja '
            'baja capacidad de generar resultados (Riquelme, 2018).'
        ),
    },
    'rotacion_activos': {
        'label': 'Rotación de Activos',
        'formato': lambda v: f'{v:.2f}x',
        'explicacion': lambda v: (
            f'Tus activos generan {v:.2f} veces su valor en ventas al año. Una rotación baja indica que los '
            'activos producen pocos ingresos (Altman, 1968).'
        ),
    },
    'volatilidad_flujo_caja': {
        'label': 'Volatilidad del Flujo de Caja',
        'formato': lambda v: f'{v:.2f}',
        'explicacion': lambda v: (
            f'La variación diaria de tu flujo de caja equivale a {v:.2f} veces tu ingreso promedio diario. '
            'Más volatilidad aumenta la probabilidad de quiebra (Ringeling, 2004).'
        ),
    },
}

GRUPO_VARIABLE = {
    'razon_corriente': 'liquidez', 'capital_trabajo_sobre_activos': 'liquidez',
    'leverage_total': 'endeudamiento',
    'roa_operacional': 'rentabilidad', 'margen_operacional': 'rentabilidad',
    'rotacion_activos': 'eficiencia',
    'volatilidad_flujo_caja': 'flujo de caja',
}

CONSEJOS_POR_GRUPO = {
    'liquidez': (
        'Acelera la cobranza, reduce inventario de lenta rotación o renegocia plazos con proveedores '
        'para que tus activos de corto plazo cubran tus deudas de corto plazo.'
    ),
    'endeudamiento': (
        'Reestructura deuda hacia el largo plazo y fortalece el patrimonio con capitalización de utilidades '
        'o aportes de socios para reducir la dependencia de financiamiento externo.'
    ),
    'rentabilidad': (
        'Revisa tu estructura de costos y gastos operacionales, y tu política de precios, '
        'para recuperar un resultado operacional positivo y sostenido.'
    ),
    'eficiencia': (
        'Evalúa vender o arrendar activos que generan pocos ingresos y enfoca la inversión '
        'en los que impulsan las ventas.'
    ),
    'flujo de caja': (
        'Suaviza tus flujos diarios: planifica pagos grandes, negocia cobros parciales '
        'y mantén un fondo de reserva para los días de menor venta.'
    ),
}


def tabla_variables_modelo(variables: dict) -> list:
    """Las 7 variables para la tabla de RF-10."""
    return [
        {'clave': clave, 'nombre': nombre, 'grupo': grupo, 'valor': variables[clave]}
        for clave, nombre, grupo in VARIABLES_MODELO
    ]


def analizar_contribucion_riesgo(variables: dict) -> list:
    """Las 3 variables que más suben el riesgo (RF-03): para cada una, cuánto
    baja la probabilidad de insolvencia si toma el valor de una empresa
    solvente típica (mediana de las empresas solventes de la CMF), dejando las
    demás iguales. V7 sin datos de caja no se considera."""
    _, metricas = _cargar_modelo_oficial()
    medianas = metricas['medianas_solventes']
    claves = [c for c in metricas['features_orden'] if variables.get(c) is not None]

    escenarios = [variables] + [{**variables, clave: medianas[clave]} for clave in claves]
    probabilidades = predecir_probabilidades(escenarios)

    resultados = []
    for clave, probabilidad_como_sana in zip(claves, probabilidades[1:]):
        impacto = round(float(probabilidades[0] - probabilidad_como_sana) * 100, 1)
        if impacto <= 0:
            continue
        texto = EXPLICACIONES[clave]
        valor = variables[clave]
        resultados.append({
            'key': clave,
            'label': texto['label'],
            'grupo': GRUPO_VARIABLE[clave],
            'valor': texto['formato'](valor),
            'impacto': impacto,
            'explicacion': texto['explicacion'](valor),
            'consejo': CONSEJOS_POR_GRUPO[GRUPO_VARIABLE[clave]],
        })
    return sorted(resultados, key=lambda r: r['impacto'], reverse=True)[:3]


RECOMENDACIONES_POR_ALERTA = {
    'Verde': {
        'titulo': 'Riesgo bajo: mantén el control',
        'mensaje': (
            'Tu situación financiera es sólida. Mantén el monitoreo periódico de tus ratios de liquidez '
            'y endeudamiento para conservar este nivel de riesgo.'
        ),
    },
    'Amarillo': {
        'titulo': 'Riesgo moderado: actúa de forma preventiva',
        'mensaje': (
            'Existen señales de alerta en algunos indicadores. Revisa los factores destacados abajo y aplica '
            'las recomendaciones asociadas antes de que el riesgo escale a un nivel crítico.'
        ),
    },
    'Rojo': {
        'titulo': 'Riesgo crítico: se requiere acción inmediata',
        'mensaje': (
            'Tu empresa presenta un riesgo alto de insolvencia. Prioriza de inmediato las recomendaciones '
            'de los factores con mayor impacto y considera asesoría financiera especializada.'
        ),
    },
}


def obtener_recomendacion_general(color: str) -> dict:
    return RECOMENDACIONES_POR_ALERTA.get(color, RECOMENDACIONES_POR_ALERTA['Amarillo'])
