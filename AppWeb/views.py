from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
import io

def home(request):
    """Vista de inicio"""
    return render(request, 'AppWeb/index.html')

def carga_datos(request):
    """Vista para procesar la carga masiva de Excel o CSV usando Pandas"""
    if request.method == 'POST':
        if 'archivo_datos' not in request.FILES:
            messages.error(request, 'No se seleccionó ningún archivo.')
            return render(request, 'AppWeb/cargaDatos.html')
            
        archivo = request.FILES['archivo_datos']
        tipo_documento = request.POST.get('tipo_documento') # balance o resultados
        
        # Validar extensión del archivo
        if not (archivo.name.endswith('.csv') or archivo.name.endswith('.xlsx')):
            messages.error(request, 'Formato no soportado. Por favor suba un archivo .csv o .xlsx')
            return render(request, 'AppWeb/cargaDatos.html')

        try:
            # 1. Cargar en Pandas DataFrame en memoria
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            errores = []
            
            # 2. Validación de Estructura (Nombres de Columnas base)
            # Esto puede ajustarse según la plantilla real exigida.
            columnas_esperadas = ['Cuenta', 'Monto']
            if not all(col in df.columns for col in columnas_esperadas):
                errores.append(f"El archivo no posee la estructura correcta. Faltan las columnas base: {columnas_esperadas}")
            else:
                # 3. Detección de Nulos / Celdas Vacías
                nulos = df.isnull().sum().sum()
                if nulos > 0:
                    errores.append(f"Se detectaron {nulos} celda(s) vacía(s) o nulas. Complete toda la información contable requerida.")
                else:
                    # 4. Validación de Tipos de Datos (Monto debe ser numérico)
                    if not pd.api.types.is_numeric_dtype(df['Monto']):
                        # Intentar convertir si vienen como string
                        try:
                            # Quitar posibles miles y convertir a número
                            if df['Monto'].dtype == object:
                                df['Monto'] = df['Monto'].astype(str).str.replace(',', '', regex=False).astype(float)
                        except Exception:
                            errores.append("La columna 'Monto' contiene valores no numéricos que no se pueden procesar.")

            if errores:
                for error in errores:
                    messages.error(request, error)
                messages.warning(request, 'El archivo no fue guardado debido a los errores encontrados. Corríjalos y vuelva a intentar.')
            else:
                # 5. Descuadres Numéricos Contables (Regla de negocio simple)
                if tipo_documento == 'balance':
                    # Regla simple: si la suma es != 0 asumiendo Activo(+) y Pasivo/Patrimonio(-)
                    suma_total = df['Monto'].sum()
                    if abs(suma_total) > 0.01:
                        messages.warning(request, f"Advertencia de Descuadre Numérico: El balance general muestra una diferencia de {suma_total:.2f}. Revise su ecuación contable.")
                
                messages.success(request, f'¡Archivo "{archivo.name}" validado correctamente con Pandas! Datos en memoria listos para predicción.')
                
        except Exception as e:
            messages.error(request, f'Hubo un error al procesar el archivo: {str(e)}')
            
        return render(request, 'AppWeb/cargaDatos.html')
        
    return render(request, 'AppWeb/cargaDatos.html')

def calculo_capm(request):
    """Vista para configurar el sector industrial de la empresa y calcular el CAPM."""
    # Coeficientes Beta referenciales del mercado chileno por sector (Ejemplo representativo)
    sectores_beta = {
        'Minería': 1.15,
        'Retail': 0.85,
        'Energía': 0.90,
        'Sector Bancario y Financiero': 1.05,
        'Telecomunicaciones': 0.75,
        'Agrícola y Forestal': 0.80,
        'Tecnología': 1.20,
        'Construcción e Inmobiliario': 1.10
    }
    
    contexto = {
        'sectores': sectores_beta.keys()
    }

    if request.method == 'POST':
        sector_seleccionado = request.POST.get('sector')
        
        if sector_seleccionado in sectores_beta:
            beta_mercado = sectores_beta[sector_seleccionado]
            
            # Variables de ejemplo para el modelo CAPM en Chile:
            # Ke = Rf + Beta(Rm - Rf)
            # Rf: Tasa Libre de Riesgo (ej. Bonos Banco Central BCU) -> 4.5%
            # Rm - Rf: Prima por riesgo de mercado esperada -> 6.0%
            tasa_libre_riesgo = 4.5
            prima_riesgo_mercado = 6.0
            
            costo_patrimonio = tasa_libre_riesgo + (beta_mercado * prima_riesgo_mercado)
            
            contexto['sector_seleccionado'] = sector_seleccionado
            contexto['beta'] = beta_mercado
            contexto['costo_patrimonio'] = round(costo_patrimonio, 2)
            
            messages.success(request, f'Se ha asignado el coeficiente Beta de {beta_mercado} para el sector {sector_seleccionado}.')
        else:
            messages.error(request, 'Por favor, seleccione un sector industrial válido.')

    return render(request, 'AppWeb/capm.html', contexto)

def extraer_monto(df, nombre_cuenta):
    """Utilidad para buscar dinámicamente un valor contable dentro del DataFrame de validación."""
    try:
        # Asume que el Excel/CSV tiene columnas ['Cuenta', 'Monto']
        fila = df[df['Cuenta'].str.contains(nombre_cuenta, case=False, na=False)]
        if not fila.empty:
            return float(fila.iloc[0]['Monto'])
    except Exception:
        pass
    return 0.0

def calcular_ratios_liquidez(df):
    """
    Motor de cálculo en memoria (Pandas) para extraer y parametrizar
    los principales ratios de liquidez previos al ML.
    """
    # 1. Extracción de variables base del DataFrame en Memoria
    activo_circulante = extraer_monto(df, 'Activo Circulante')
    pasivo_circulante = extraer_monto(df, 'Pasivo Circulante')
    inventario = extraer_monto(df, 'Inventario')
    caja_y_bancos = extraer_monto(df, 'Caja y Bancos') # o Equivalentes
    flujo_caja_operativo = extraer_monto(df, 'Flujo de Caja Operativo')
    pasivo_total = extraer_monto(df, 'Pasivo Total')
    activo_total = extraer_monto(df, 'Activo Total')
    cuentas_por_cobrar = extraer_monto(df, 'Cuentas por Cobrar')
    
    # 2. Computación de Ratios (Evitar ZeroDivisionError)
    eps = 1e-6 # Margen de seguridad matemático
    denominador_pasivo = pasivo_circulante if pasivo_circulante > 0 else eps
    
    ratios = {
        'razon_corriente': activo_circulante / denominador_pasivo,
        'prueba_acida': (activo_circulante - inventario) / denominador_pasivo,
        'ratio_caja': caja_y_bancos / denominador_pasivo,
        'cobertura_operacional': flujo_caja_operativo / denominador_pasivo,
        'capital_trabajo': activo_circulante - pasivo_circulante,
        'endeudamiento_corto_plazo': pasivo_circulante / (pasivo_total if pasivo_total > 0 else eps),
        'liquidez_inmediata': (caja_y_bancos + cuentas_por_cobrar) / denominador_pasivo,
        'solvencia_general': activo_total / (pasivo_total if pasivo_total > 0 else eps)
    }
    
    # Redondeamos a 2 decimales para la reportería
    return {k: round(v, 4) for k, v in ratios.items()}


def ejecutar_prediccion(request):
    """Vista que activa el pipeline predictivo: Ratios + CAPM -> ML Scikit-Learn"""
    if request.method == 'POST':
        # 1. Recuperar los datos desde memoria/caché (Para efectos prácticos, simularemos el df)
        try:
            # En el flujo ideal, el DF se pasa serializado, en una variable de sesión o se re-carga el archivo.
            # Aquí lo simularemos asumiendo la inyección.
            
            # --- SIMULACIÓN DEL DATAFRAME CARGADO (HU1/HU2) ---
            datos_dummy = {
                'Cuenta': ['Activo Circulante', 'Pasivo Circulante', 'Inventario', 'Caja y Bancos', 'Flujo de Caja Operativo', 'Pasivo Total', 'Activo Total', 'Cuentas por Cobrar'],
                'Monto': [50000, 30000, 15000, 10000, 5000, 80000, 120000, 8000]
            }
            df_contable = pd.DataFrame(datos_dummy)
            
            # 2. Calcular 8 Ratios de Liquidez (Parametrización)
            ratios_empresa = calcular_ratios_liquidez(df_contable)
            
            # 3. Extraer el CAPM asociado a la empresa (Ejemplo estático: Sector Retail Beta 0.85)
            beta_sector = 0.85 
            
            # 4. Inyección a Scikit-Learn (Simulado)
            import joblib
            import os
            # Generar feature vector esperado por el modelo:
            # features = [[ratios_empresa['razon_corriente'], ratios_empresa['prueba_acida'], ..., beta_sector]]
            # modelo = joblib.load('ruta/al/modelo.pkl')
            # probabililidad_quiebra = modelo.predict_proba(features)[0][1]
            
            # Simulación de puntaje inferido:
            puntaje_riesgo = 75.4 # De 0 a 100
            
            # Determinar color de semáforo
            if puntaje_riesgo <= 35:
                riesgo, color = 'Bajo', 'Verde'
            elif puntaje_riesgo <= 70:
                riesgo, color = 'Moderado', 'Amarillo'
            else:
                riesgo, color = 'Crítico', 'Rojo'
                
            messages.success(request, f'Análisis predictivo completado. Ratios calculados con éxito.')
            
            contexto = {
                'ratios': ratios_empresa,
                'beta': beta_sector,
                'score': puntaje_riesgo,
                'riesgo': riesgo,
                'color': color
            }
            return render(request, 'AppWeb/resultado_prediccion.html', contexto)
            
        except Exception as e:
            messages.error(request, f"Error en la predicción: {str(e)}")
            return redirect('home')
            
    return redirect('home')


