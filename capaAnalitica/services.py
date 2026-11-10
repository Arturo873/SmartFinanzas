"""
Capa Analítica - Servicio Interno de Inferencia y Explicabilidad (SHAP).
SmartFinanzas - Arquitectura Monolito Modular.

Esta capa actúa como un servicio (Service Layer) puro, desacoplado de vistas HTML.
Carga el modelo pre-entrenado de Random Forest (.joblib), evalúa el vector de los
7 ratios financieros (X1 - X7) y calcula la explicabilidad local con SHAP.
"""

import os
import json
import time
import logging
from pathlib import Path
from decimal import Decimal
import numpy as np
import joblib
import shap
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Definición estándar de las 7 variables financieras del modelo de insolvencia
VARIABLES_FINANCIERAS = [
    {
        'codigo': 'X1',
        'clave': 'razon_corriente',
        'clave_etl': 'v1_razon_corriente',
        'nombre': 'Razón Corriente',
        'grupo': 'Liquidez',
        'unidad': 'x',
        'desc_alza': 'La sólida Razón Corriente fortalece la liquidez y reduce el riesgo',
        'desc_baja': 'La baja Razón Corriente debilitó la liquidez a corto plazo'
    },
    {
        'codigo': 'X2',
        'clave': 'capital_trabajo_sobre_activos',
        'clave_etl': 'v2_capital_trabajo_activos',
        'nombre': 'Capital de Trabajo sobre Activos',
        'grupo': 'Liquidez',
        'unidad': '%',
        'desc_alza': 'El excedente de Capital de Trabajo amortigua contingencias operativas',
        'desc_baja': 'El Ratio de Capital de Trabajo disminuyó drásticamente, incrementando el riesgo'
    },
    {
        'codigo': 'X3',
        'clave': 'leverage_total',
        'clave_etl': 'v3_leverage_total',
        'nombre': 'Leverage Total',
        'grupo': 'Endeudamiento',
        'unidad': 'x',
        'desc_alza': 'El elevado Leverage Total (endeudamiento) presiona la solvencia financiera',
        'desc_baja': 'El bajo apalancamiento financiero mantiene controlado el endeudamiento'
    },
    {
        'codigo': 'X4',
        'clave': 'roa_operacional',
        'clave_etl': 'v4_roa_operacional',
        'nombre': 'ROA Operacional',
        'grupo': 'Rentabilidad',
        'unidad': '%',
        'desc_alza': 'El buen rendimiento de activos (ROA) apoya la solidez del negocio',
        'desc_baja': 'La baja rentabilidad de activos (ROA) limita la capacidad de solvencia'
    },
    {
        'codigo': 'X5',
        'clave': 'margen_operacional',
        'clave_etl': 'v5_margen_operacional',
        'nombre': 'Margen Operacional',
        'grupo': 'Rentabilidad',
        'unidad': '%',
        'desc_alza': 'El sólido Margen Operacional genera un flujo saludable para el negocio',
        'desc_baja': 'La caída del Margen Operacional aportó directamente al riesgo'
    },
    {
        'codigo': 'X6',
        'clave': 'rotacion_activos',
        'clave_etl': 'v6_rotacion_activos',
        'nombre': 'Rotación de Activos',
        'grupo': 'Eficiencia',
        'unidad': 'x',
        'desc_alza': 'La alta Rotación de Activos demuestra eficiencia comercial y operativa',
        'desc_baja': 'La baja Rotación de Activos refleja menor productividad de las ventas'
    },
    {
        'codigo': 'X7',
        'clave': 'volatilidad_flujo_caja',
        'clave_etl': 'v7_volatilidad_flujo',
        'nombre': 'Volatilidad del Flujo de Caja',
        'grupo': 'Flujo de Caja',
        'unidad': 'ratio',
        'desc_alza': 'La alta dispersión en los flujos diarios de caja aumenta la incertidumbre',
        'desc_baja': 'La regularidad y estabilidad del flujo de caja mitiga el riesgo'
    },
]

ORDEN_CLAVES_MODELO = [v['clave'] for v in VARIABLES_FINANCIERAS]


class MotorRiesgo:
    """
    Motor de Inferencia de Riesgo Financiero y Explicabilidad SHAP.
    Carga el modelo Scikit-Learn Random Forest persistido en .joblib y realiza
    inferencias server-side sin exponer pesos ni árboles internos.
    """

    def __init__(self, model_path=None):
        """
        Inicializa el motor cargando el modelo pre-entrenado en memoria.
        """
        self.model_path = self._resolver_ruta_modelo(model_path)
        self.metricas_path = self._resolver_ruta_metricas()
        try:
            self.model = joblib.load(self.model_path)
            logger.info("Modelo Random Forest cargado exitosamente desde %s", self.model_path)
        except Exception as e:
            logger.error("Error al cargar el modelo ML desde %s: %s", self.model_path, e)
            raise RuntimeError(f"No fue posible cargar el modelo Random Forest: {e}")

        # Cargar metadatos y métricas si están disponibles
        self.metricas = {}
        if self.metricas_path and os.path.exists(self.metricas_path):
            try:
                self.metricas = joblib.load(self.metricas_path)
            except Exception as e:
                logger.warning("No se pudieron cargar las métricas complementarias: %s", e)

        # Inicialización del explicador TreeExplainer de SHAP
        try:
            self.explainer = shap.TreeExplainer(self.model)
        except Exception as e:
            logger.warning("No se pudo preinicializar TreeExplainer: %s", e)
            self.explainer = None

    def _resolver_ruta_modelo(self, model_path):
        if model_path and os.path.exists(model_path):
            return str(model_path)

        nombre_config = (
            getattr(settings, 'MODELO_ML_NOMBRE', None)
            or getattr(settings, 'ML_MODEL_NAME', None)
            or 'ModeloSmartfinanzas.joblib'
        )

        nombres_a_buscar = [nombre_config]
        if not nombre_config.endswith(('.joblib', '.pkl')):
            nombres_a_buscar.extend([f"{nombre_config}.joblib", f"{nombre_config}.pkl"])
        else:
            nombres_a_buscar.append(Path(nombre_config).stem)

        for extra in ['ModeloSmartfinanzas.joblib', 'ModeloSmartfinanzas']:
            if extra not in nombres_a_buscar:
                nombres_a_buscar.append(extra)

        rutas_candidatas = []
        for n in nombres_a_buscar:
            n_clean = n.strip()
            p = Path(n_clean)
            if p.is_absolute() and p.exists():
                return str(p)
            rutas_candidatas.extend([
                settings.BASE_DIR / 'capaAnalitica' / 'modelo' / n_clean,
                settings.BASE_DIR / 'AppWeb' / 'modelo_oficial' / n_clean,
                settings.BASE_DIR / 'capaAnalitica' / n_clean,
                settings.BASE_DIR / n_clean,
            ])

        # Rutas candidatas de respaldo histórico
        rutas_candidatas.extend([
            settings.BASE_DIR / 'capaAnalitica' / 'modelo' / 'modelo_riesgo_v11.joblib',
            settings.BASE_DIR / 'capaAnalitica' / 'modelo' / 'random_forest_model.joblib',
            settings.BASE_DIR / 'AppWeb' / 'modelo_oficial' / 'modelo_riesgo_v11.joblib',
            settings.BASE_DIR / 'capaAnalitica' / 'random_forest_model.joblib',
        ])

        for ruta in rutas_candidatas:
            if ruta.exists():
                return str(ruta)

        if model_path:
            return str(model_path)

        # Retornar la ruta canónica por defecto en la capa analítica
        return str(settings.BASE_DIR / 'capaAnalitica' / 'modelo' / 'ModeloSmartfinanzas.joblib')

    def _resolver_ruta_metricas(self):
        rutas = [
            settings.BASE_DIR / 'capaAnalitica' / 'modelo' / 'metricas_trimestral_optimizado.joblib',
            settings.BASE_DIR / 'capaAnalitica' / 'modelo' / 'metricas_v11.joblib',
            settings.BASE_DIR / 'capaAnalitica' / 'modelo' / 'metricas.joblib',
            settings.BASE_DIR / 'AppWeb' / 'modelo_oficial' / 'metricas_v11.joblib',
        ]
        for r in rutas:
            if r.exists():
                return str(r)
        return None

    def _extraer_vector_ratios(self, vector_ratios):
        """
        Convierte cualquier formato de entrada (dict, RatioFinanciero, list/tuple)
        en una lista ordenada con las 7 variables numéricas [X1, X2, X3, X4, X5, X6, X7].
        """
        if hasattr(vector_ratios, 'v1_razon_corriente'):
            # Instancia de RatioFinanciero (Django Model)
            return [
                float(vector_ratios.v1_razon_corriente if vector_ratios.v1_razon_corriente is not None else 1.0),
                float(vector_ratios.v2_capital_trabajo_activos if vector_ratios.v2_capital_trabajo_activos is not None else 0.0),
                float(vector_ratios.v3_leverage_total if vector_ratios.v3_leverage_total is not None else 1.0),
                float(vector_ratios.v4_roa_operacional if vector_ratios.v4_roa_operacional is not None else 0.0),
                float(vector_ratios.v5_margen_operacional if vector_ratios.v5_margen_operacional is not None else 0.0),
                float(vector_ratios.v6_rotacion_activos if vector_ratios.v6_rotacion_activos is not None else 1.0),
                float(vector_ratios.v7_volatilidad_flujo if vector_ratios.v7_volatilidad_flujo is not None else 0.0),
            ]

        if isinstance(vector_ratios, dict):
            # Diccionario con claves arbitrarias o canónicas
            valores = []
            for item in VARIABLES_FINANCIERAS:
                clave = item['clave']
                clave_etl = item['clave_etl']
                cod = item['codigo'].lower()
                cod_u = item['codigo'].upper()

                # Búsqueda de la clave en el diccionario
                val = None
                for k in (clave, clave_etl, cod, cod_u, clave.replace('_', ' ')):
                    if k in vector_ratios and vector_ratios[k] is not None:
                        val = vector_ratios[k]
                        break

                if val is None:
                    # Valor neutro por defecto
                    val = 0.0
                valores.append(float(val))
            return valores

        if isinstance(vector_ratios, (list, tuple, np.ndarray)):
            # Lista plana o array
            elementos = list(vector_ratios)
            if len(elementos) == 1 and isinstance(elementos[0], (list, tuple, np.ndarray)):
                elementos = list(elementos[0])
            if len(elementos) < 7:
                elementos = elementos + [0.0] * (7 - len(elementos))
            return [float(x if x is not None else 0.0) for x in elementos[:7]]

        raise ValueError(f"Formato no admitido para vector_ratios: {type(vector_ratios)}")

    def evaluar_riesgo(self, vector_ratios):
        """
        Evalúa el riesgo financiero y calcula la explicabilidad SHAP.

        Parámetros:
            vector_ratios: lista o diccionario con las 7 variables financieras (X1 a X7).

        Retorna:
            dict con:
                - score: Probabilidad de clase 1 (Insolvencia) * 100 (rango 0-100).
                - nivel: "Rojo" (score > 70), "Amarillo" (35 < score <= 70), "Verde" (score <= 35).
                - top_3_variables: Lista con el Top-3 de variables con mayor impacto absoluto SHAP.
                - shap_values: Diccionario completo de valores SHAP calculados.
                - vector_input: Lista de los 7 valores numéricos procesados.
        """
        # 1. Normalización y conversión estricta a NumPy 2D array (1, -1)
        lista_valores = self._extraer_vector_ratios(vector_ratios)
        array_input = np.array(lista_valores, dtype=float).reshape(1, -1)

        # 2. Inferencia de probabilidad con el modelo Scikit-Learn
        probabilidades = self.model.predict_proba(array_input)
        
        # En clasificación binaria, la clase 1 representa 'Insolvencia / Riesgo Alto'
        clases = list(getattr(self.model, 'classes_', [0, 1]))
        if 1 in clases:
            idx_clase_1 = clases.index(1)
        else:
            idx_clase_1 = 1 if len(clases) > 1 else 0

        p_insolvencia = float(probabilidades[0][idx_clase_1])
        score = round(p_insolvencia * 100.0, 2)

        # 3. Lógica estática de semáforo de riesgo
        if score > 70.0:
            nivel = "Rojo"
        elif score > 35.0:
            nivel = "Amarillo"
        else:
            nivel = "Verde"

        # 4. Módulo de Explicabilidad (SHAP)
        # TreeExplainer calcula las contribuciones de cada feature para la predicción
        explainer = self.explainer or shap.TreeExplainer(self.model)
        shap_raw = explainer.shap_values(array_input)

        # Extracción de valores SHAP para la clase 1 (Insolvencia)
        if isinstance(shap_raw, list):
            # Formato clásico de SHAP para clasificadores binarios: lista de arrays [clase 0, clase 1]
            if len(shap_raw) > 1:
                sv_clase_1 = np.asarray(shap_raw[1])[0]
            else:
                sv_clase_1 = np.asarray(shap_raw[0])[0]
        elif isinstance(shap_raw, np.ndarray):
            if shap_raw.ndim == 3:
                # Formato moderno de SHAP: (samples, features, classes) -> (1, 7, 2)
                sv_clase_1 = shap_raw[0, :, idx_clase_1]
            elif shap_raw.ndim == 2:
                sv_clase_1 = shap_raw[0]
            else:
                sv_clase_1 = shap_raw
        else:
            sv_clase_1 = np.zeros(7)

        # 5. Cálculo del impacto de cada una de las 7 variables
        variables_impacto = []
        shap_dict = {}

        for i, meta in enumerate(VARIABLES_FINANCIERAS):
            shap_val = float(sv_clase_1[i])
            impacto_pct = round(shap_val * 100.0, 2)
            impacto_abs = abs(impacto_pct)
            valor_actual = lista_valores[i]

            # Redacción explicativa contextualizada
            if impacto_pct >= 0:
                # Aporta al riesgo (lo empuja hacia insolvencia)
                signo = "+"
                plantilla_desc = meta['desc_baja']
                texto = f"{plantilla_desc} (aportó un +{impacto_pct:.1f}% al riesgo)"
            else:
                # Mitiga o reduce el riesgo (lo aleja de insolvencia)
                signo = ""
                plantilla_desc = meta['desc_alza']
                texto = f"{plantilla_desc} (redujo un {abs(impacto_pct):.1f}% el riesgo)"

            # Versión concisa orientada al informe
            texto_resumen = f"La variación de {meta['nombre']} aportó un {signo}{impacto_pct:.1f}% al riesgo"

            item_info = {
                'codigo': meta['codigo'],
                'clave': meta['clave'],
                'nombre': meta['nombre'],
                'grupo': meta['grupo'],
                'valor': valor_actual,
                'unidad': meta['unidad'],
                'impacto_shap': shap_val,
                'impacto_pct': impacto_pct,
                'impacto_abs': impacto_abs,
                'texto': texto,
                'texto_resumen': texto_resumen,
                'aumenta_riesgo': impacto_pct >= 0,
            }
            variables_impacto.append(item_info)
            shap_dict[meta['clave']] = item_info

        # 6. Extracción del Top-3 con mayor impacto absoluto
        top_3_variables = sorted(variables_impacto, key=lambda x: x['impacto_abs'], reverse=True)[:3]

        return {
            'score': score,
            'nivel': nivel,
            'top_3_variables': top_3_variables,
            'shap_values': shap_dict,
            'vector_input': lista_valores,
            'version_modelo': self.metricas.get('version', 'v11'),
        }


def evaluar_vector_financiero(vector_ratios):
    """
    Función de conveniencia para invocar el MotorRiesgo directamente.
    """
    motor = MotorRiesgo()
    return motor.evaluar_riesgo(vector_ratios)


def ejecutar_y_persistir_prediccion(ratio_obj_o_id, usuario=None, empresa=None):
    """
    Servicio de alto nivel invocado cuando el usuario ejecuta una predicción.
    Evalúa los ratios financieros y persiste la instancia de PrediccionRiesgo en el sistema.
    """
    from moduloETL.models import RatioFinanciero
    from capaAnalitica.models import PrediccionRiesgo

    t_inicio = time.time()

    if isinstance(ratio_obj_o_id, (int, str)):
        ratio_obj = RatioFinanciero.objects.get(pk=ratio_obj_o_id)
    else:
        ratio_obj = ratio_obj_o_id

    # Si no se suministra empresa, obtenerla del ratio o del usuario
    if not empresa and ratio_obj and ratio_obj.empresa:
        empresa = ratio_obj.empresa
    elif not empresa and usuario and hasattr(usuario, 'empresa'):
        empresa = usuario.empresa

    motor = MotorRiesgo()
    resultado = motor.evaluar_riesgo(ratio_obj)
    tiempo_ms = int((time.time() - t_inicio) * 1000)

    # Persistencia en tabla 'prediccionriesgo'
    prediccion = PrediccionRiesgo.objects.create(
        ratio=ratio_obj,
        fecha_prediccion=timezone.now(),
        score_riesgo=Decimal(str(resultado['score'])),
        nivel_semaforo=resultado['nivel'],
        variables_influyentes=json.dumps(resultado['top_3_variables'], ensure_ascii=False),
        impacto_variables=json.dumps(resultado['shap_values'], ensure_ascii=False),
        version_modelo=str(resultado.get('version_modelo', '1.1'))[:50],
        tiempo_inferencia_ms=tiempo_ms,
        ejecutada_por_usuario=usuario,
        empresa=empresa,
    )

    # Persistir inmediatamente las recomendaciones vinculadas al ID de la predicción
    try:
        generar_o_recuperar_recomendaciones_prediccion(prediccion, forzar_recalculo=True)
    except Exception as e:
        logger.warning(f"Error al generar recomendaciones tras predicción #{prediccion.id}: {e}")

    return prediccion, resultado


def generar_o_recuperar_recomendaciones_prediccion(
    prediccion_obj,
    score_proyectado=None,
    ratios_dict=None,
    forzar_recalculo=False
) -> dict:
    """
    Recupera las recomendaciones persistidas en la tabla 'recomendacion' vinculadas
    al 'prediccion_obj.id' (período actual), o las genera y persiste si no existen aún.
    Garantiza trazabilidad histórica ligada al ID del período analizado.
    """
    from capaAnalitica.models import Recomendacion
    from capaAnalitica.catalogo_recomendaciones import (
        seleccionar_recomendaciones_para_periodo,
        clasificar_nivel
    )

    if not prediccion_obj:
        return seleccionar_recomendaciones_para_periodo(
            score_actual=35.0,
            score_proyectado=score_proyectado or 35.0,
            variables_dict=ratios_dict or {}
        )

    sc_act = float(prediccion_obj.score_riesgo if prediccion_obj.score_riesgo is not None else 35.0)
    sc_proy = float(score_proyectado) if score_proyectado is not None else sc_act

    # 1. Si ya tiene recomendaciones guardadas y no forzamos recálculo, leerlas
    qs_existentes = Recomendacion.objects.filter(prediccion=prediccion_obj).order_by('id')
    if qs_existentes.exists() and not forzar_recalculo:
        macro_item = None
        tacticas_items = []
        for rec in qs_existentes:
            try:
                data = json.loads(rec.texto) if rec.texto else {}
            except Exception:
                data = {
                    'titulo': rec.texto or 'Acción Financiera',
                    'que_hacer': rec.texto or '',
                    'fuente': 'Chile Financial Distress Model'
                }

            if rec.variable_origen == 'macro_transicion':
                macro_item = data
            else:
                tacticas_items.append(data)

        if macro_item and tacticas_items:
            delta = round(sc_proy - sc_act, 1)
            return {
                'macro': macro_item,
                'tacticas': tacticas_items,
                'meta': {
                    'prediccion_id': prediccion_obj.id,
                    'periodo': prediccion_obj.ratio.periodo if (prediccion_obj.ratio and prediccion_obj.ratio.periodo) else 'Actual',
                    'score_actual': sc_act,
                    'score_proyectado': sc_proy,
                    'nivel_actual': prediccion_obj.nivel_semaforo or clasificar_nivel(sc_act),
                    'nivel_proyectado': clasificar_nivel(sc_proy),
                    'delta_riesgo': delta,
                    'tendencia': 'Deterioro' if delta > 1.5 else ('Mejora' if delta < -1.5 else 'Estable'),
                }
            }

    # 2. Si no existen o se forzó recálculo, generarlas desde el catálogo
    top_3_vars = []
    if prediccion_obj.variables_influyentes:
        try:
            top_3_vars = json.loads(prediccion_obj.variables_influyentes)
        except Exception:
            top_3_vars = []

    vars_eval = dict(ratios_dict or {})
    if prediccion_obj.ratio:
        r = prediccion_obj.ratio
        vars_eval.setdefault('razon_corriente', float(r.v1_razon_corriente or 1.0))
        vars_eval.setdefault('capital_trabajo_sobre_activos', float(r.v2_capital_trabajo_activos or 0.1))
        vars_eval.setdefault('leverage_total', float(r.v3_leverage_total or 1.0))
        vars_eval.setdefault('roa_operacional', float(r.v4_roa_operacional or 0.05))
        vars_eval.setdefault('margen_operacional', float(r.v5_margen_operacional or 0.08))
        vars_eval.setdefault('rotacion_activos', float(r.v6_rotacion_activos or 1.0))
        vars_eval.setdefault('volatilidad_flujo_caja', float(r.v7_volatilidad_flujo or 0.5))

    resultado = seleccionar_recomendaciones_para_periodo(
        score_actual=sc_act,
        score_proyectado=sc_proy,
        variables_dict=vars_eval,
        top_3_variables=top_3_vars
    )
    resultado['meta']['prediccion_id'] = prediccion_obj.id
    resultado['meta']['periodo'] = prediccion_obj.ratio.periodo if (prediccion_obj.ratio and prediccion_obj.ratio.periodo) else 'Actual'

    # 3. Persistencia en tabla 'recomendacion' vinculada a prediccion_obj.id
    try:
        Recomendacion.objects.filter(prediccion=prediccion_obj).delete()

        # Guardar Macro
        Recomendacion.objects.create(
            prediccion=prediccion_obj,
            variable_origen='macro_transicion',
            grupo_riesgo=str(resultado['macro'].get('tipo', 'Macro'))[:40],
            prioridad=str(resultado['macro'].get('prioridad', 'Alta'))[:10],
            texto=json.dumps(resultado['macro'], ensure_ascii=False)
        )

        # Guardar Tácticas
        for tac in resultado['tacticas']:
            Recomendacion.objects.create(
                prediccion=prediccion_obj,
                variable_origen=str(tac.get('variable_origen', 'tactica'))[:50],
                grupo_riesgo=str(tac.get('grupo_riesgo', 'Operativo'))[:40],
                prioridad=str(tac.get('prioridad', 'Media'))[:10],
                texto=json.dumps(tac, ensure_ascii=False)
            )
    except Exception as e:
        logger.warning(f"No se pudieron persistir recomendaciones para predicción #{prediccion_obj.id}: {e}")

    return resultado

