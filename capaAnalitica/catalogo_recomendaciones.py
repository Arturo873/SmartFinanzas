"""
Catálogo Maestro de Recomendaciones Financieras y Planes de Acción Preventivos.
SmartFinanzas - Capa Analítica.

Enfoque de Redacción: Lenguaje Ejecutivo Accesible (Business Plain Spanish).
  - Tono formal, serio y profesional de nivel gerencial.
  - Sin jerga técnica compleja ni anglicismos innecesarios.
  - Explicaciones basadas en cifras cotidianas (proporciones por cada $1.000 o $100.000).
  - Acciones concretas, viables y respaldadas en la realidad empresarial y normativa chilena.

Fundamentación Teórica y Empírica Basada en Literatura Chilena:
  - Zurita, F. (2008). "La predicción de la insolvencia de empresas chilenas". Economía Chilena, Banco Central de Chile.
  - Ringeling, E. (2004). "Análisis comparativo de modelos de predicción de quiebra y la probabilidad de bancarrota". Universidad de Chile.
  - Riquelme, V. (2018). "Evaluación de la capacidad de pronóstico de modelos predictivos de quiebra en Chile y Brasil". Universidad del Bío-Bío.
  - Ley 20.720 (modernizada por Ley 21.563 de 2023). "Ley de Reorganización y Liquidación de Empresas y Personas". República de Chile.
  - Altman, E. I. (1983). "Corporate Financial Distress". Formulación para Mercados Emergentes (EMS).
"""

# ==============================================================================
# 1. MATRIZ DE RECOMENDACIONES MACRO ESTRATÉGICAS (Transición Q_t -> Q_{t+1})
# ==============================================================================

RECOMENDACIONES_MACRO_TRANSICION = {
    ('Verde', 'Verde'): {
        'id_codigo': 'MACRO-V-V',
        'transicion': 'Estable (Solvente -> Solvente)',
        'tipo': 'Consolidación y Crecimiento Prudente',
        'prioridad': 'Estratégica',
        'clase_badge': 'badge-status-solvente',
        'icono': 'bi-shield-check',
        'titulo': 'Consolidación de la Estabilidad Financiera y Reinversión Prudente',
        'resumen_transicion': 'La empresa mantiene una posición financiera sólida y la proyección a 90 días anticipa continuidad en este nivel de solvencia.',
        'accion_principal': (
            'Aprovechar la buena salud del negocio para negociar mejores condiciones de crédito con los bancos '
            '(menores tasas de interés) y constituir un fondo de reserva en la cuenta de la empresa equivalente '
            'a 30 o 45 días de gastos habituales, protegiendo las operaciones ante posibles meses de baja venta.'
        ),
        'procedimiento_pasos': [
            '1. Revisar con las instituciones financieras la posibilidad de rebajar tasas de interés aprovechando el buen historial.',
            '2. Destinar un porcentaje de los excedentes mensuales a una reserva de seguridad para imprevistos.',
            '3. Evaluar reinversiones en mejoras operativas o tecnología que permitan vender más con los mismos recursos.',
        ],
        'cita_fuente': 'Prácticas de solvencia patrimonial en empresas chilenas (Zurita, 2008; Riquelme, 2018).',
    },
    ('Verde', 'Amarillo'): {
        'id_codigo': 'MACRO-V-A',
        'transicion': 'Alerta Preventiva (Solvente -> En Riesgo Moderado)',
        'tipo': 'Alerta Preventiva Temprana',
        'prioridad': 'Alta',
        'clase_badge': 'badge-status-alerta',
        'icono': 'bi-exclamation-triangle-fill',
        'titulo': 'Alerta Preventiva: Contención de Liquidez ante Deterioro Proyectado',
        'resumen_transicion': 'Aunque la empresa mantiene actualmente estabilidad en sus operaciones, el modelo predictivo proyecta un incremento en las presiones de pago durante los próximos 90 días si se mantiene el nivel de gasto actual.',
        'accion_principal': (
            'Suspender temporalmente inversiones no esenciales y priorizar la recaudación de fondos para '
            'asegurar la cobertura de las obligaciones operativas del próximo trimestre, evitando que el riesgo '
            'se traslade a un nivel crítico de difícil manejo.'
        ),
        'procedimiento_pasos': [
            '1. Control de inversiones: Postergar la compra de maquinaria, vehículos o mejoras que no generen ingresos inmediatos en los próximos 90 días.',
            '2. Supervisión semanal de tesorería: Revisar todos los lunes el saldo real en bancos frente a los compromisos de la semana (sueldos, cheques y cuotas).',
            '3. Acuerdos de pago con proveedores: Solicitar a los proveedores habituales una extensión en los plazos de vencimiento de 30 a 60 días para aliviar el flujo de caja.',
        ],
        'cita_fuente': 'Control de volatilidad de caja y capital de trabajo (Ringeling, 2004; Zurita, 2008).',
    },
    ('Verde', 'Rojo'): {
        'id_codigo': 'MACRO-V-R',
        'transicion': 'Alerta Severa (Solvente -> Riesgo Crítico)',
        'tipo': 'Freno de Emergencia Financiero',
        'prioridad': 'Alta',
        'clase_badge': 'badge-status-critico',
        'icono': 'bi-lightning-charge-fill',
        'titulo': 'Freno de Emergencia: Blindaje Inmediato de Caja por Deterioro Acelerado',
        'resumen_transicion': 'El modelo anticipa un cambio abrupto hacia un nivel de riesgo crítico en los próximos 90 días, lo que podría comprometer la capacidad de pago de la empresa.',
        'accion_principal': (
            'Convocar de inmediato a la administración para aplicar un plan de contingencia urgente. '
            'Detener de forma estricta todo gasto no imprescindible, asegurar el pago prioritario de remuneraciones '
            'y obligaciones tributarias, y gestionar con el banco líneas de apoyo antes de que se endurezcan las condiciones de crédito.'
        ),
        'procedimiento_pasos': [
            '1. Congelar inmediatamente cualquier desembolso que no sea indispensable para mantener la empresa abierta.',
            '2. Ofrecer incentivos o descuentos por pronto pago (2% a 3%) a clientes confiables para adelantar la entrada de dinero en efectivo.',
            '3. Contactar a los ejecutivos bancarios para asegurar que las líneas de crédito habituales se mantengan disponibles.',
        ],
        'cita_fuente': 'Medidas de blindaje financiero de emergencia (Zurita, 2008; Ley 20.720).',
    },
    ('Amarillo', 'Verde'): {
        'id_codigo': 'MACRO-A-V',
        'transicion': 'Mejora Proyectada (En Riesgo Moderado -> Solvente)',
        'tipo': 'Consolidación de Recuperación',
        'prioridad': 'Media',
        'clase_badge': 'badge-status-solvente',
        'icono': 'bi-arrow-up-right-circle-fill',
        'titulo': 'Consolidación del Retorno a la Zona de Seguridad',
        'resumen_transicion': 'La empresa venía operando con estrechez de recursos, pero las proyecciones indican una recuperación de la solvencia para los siguientes 90 días.',
        'accion_principal': (
            'Mantener la moderación en los gastos y no relajar las condiciones de cobro a clientes. '
            'Destinar los primeros excedentes de caja a pagar las deudas más costosas (líneas de sobregiro o créditos rápidos), '
            'asegurando que la recuperación sea permanente y no solo un alivio momentáneo.'
        ),
        'procedimiento_pasos': [
            '1. Mantener las medidas de control de gasto hasta confirmar al menos dos trimestres consecutivos en zona de seguridad.',
            '2. Pagar con prioridad los créditos o líneas bancarias que cobran mayores intereses mensuales.',
            '3. Restablecer paulatinamente el capital de trabajo de la empresa sin asumir nuevas deudas.',
        ],
        'cita_fuente': 'Estabilización y saneamiento operativo (Riquelme, 2018; Altman, 1983).',
    },
    ('Amarillo', 'Amarillo'): {
        'id_codigo': 'MACRO-A-A',
        'transicion': 'Riesgo Moderado Persistente',
        'tipo': 'Mitigación y Reprogramación de Pasivos',
        'prioridad': 'Media',
        'clase_badge': 'badge-status-alerta',
        'icono': 'bi-cone-striped',
        'titulo': 'Mitigación de Vulnerabilidad y Reprogramación de Vencimientos',
        'resumen_transicion': 'La empresa opera continuamente con poco margen de maniobra, sin colchón suficiente para responder ante caídas de ventas o cobros atrasados.',
        'accion_principal': (
            'Acercarse a las instituciones financieras y proveedores para reprogramar pagos que vencen este mes '
            'hacia cuotas de mayor plazo (24 a 36 meses). Esto permitirá reducir el monto que sale de la cuenta cada mes '
            'y dar respiro a las operaciones del negocio.'
        ),
        'procedimiento_pasos': [
            '1. Negociar con el banco la conversión de deudas de corto plazo en un crédito comercial en cuotas mensuales más accesibles.',
            '2. Liquidar existencias de productos de lenta rotación mediante ventas especiales para convertirlos en dinero en efectivo.',
            '3. Acordar con los 5 principales proveedores un calendario de pagos escalonado a 60 días plazo.',
        ],
        'cita_fuente': 'Gestión de vencimientos de pasivo circulante (Ringeling, 2004; Zurita, 2008).',
    },
    ('Amarillo', 'Rojo'): {
        'id_codigo': 'MACRO-A-R',
        'transicion': 'Alerta Crítica (En Riesgo Moderado -> Riesgo Crítico)',
        'tipo': 'Alerta Crítica de Insolvencia',
        'prioridad': 'Alta',
        'clase_badge': 'badge-status-critico',
        'icono': 'bi-exclamation-octagon-fill',
        'titulo': 'Alerta Crítica: Reestructuración Urgente de Deudas Exigibles',
        'resumen_transicion': 'El deterioro se agravará durante el próximo trimestre, situando a la empresa en una posición donde las deudas superarán la capacidad real de pago.',
        'accion_principal': (
            'La administración debe tomar medidas correctivas inmediatas en el período actual: solicitar a los bancos '
            'períodos de gracia para el pago de capital, ordenar los vencimientos más urgentes y proteger el flujo de caja '
            'para no caer en atrasos que deriven en acciones judiciales o cierre de cuentas corrientes.'
        ),
        'procedimiento_pasos': [
            '1. Armar un presupuesto semanal detallado de ingresos y gastos para los próximos 3 meses, auditado directamente por la gerencia.',
            '2. Solicitar formalmente a las entidades crediticias una reprogramación de cuotas con meses de gracia.',
            '3. Asegurar con prioridad absoluta el pago de imposiciones previsionales y remuneraciones del personal.',
        ],
        'cita_fuente': 'Reestructuración preventiva de pasivos bancarios y comerciales (Zurita, 2008; Ley 20.720).',
    },
    ('Rojo', 'Verde'): {
        'id_codigo': 'MACRO-R-V',
        'transicion': 'Recuperación Favorable (Riesgo Crítico -> Solvente)',
        'tipo': 'Recuperación Excepcional',
        'prioridad': 'Alta',
        'clase_badge': 'badge-status-solvente',
        'icono': 'bi-graph-up-arrow',
        'titulo': 'Sostenimiento de la Recuperación y Protección de la Caja',
        'resumen_transicion': 'Las medidas de orden implementadas muestran un efecto positivo que proyecta sacar a la empresa del tramo de riesgo crítico.',
        'accion_principal': (
            'Proteger con rigor los recursos recuperados. No asumir nuevas obligaciones financieras ni compromisos '
            'de gasto innecesarios hasta verificar que el negocio mantiene su estabilidad de forma continua en el tiempo.'
        ),
        'procedimiento_pasos': [
            '1. Respetar al pie de la letra los acuerdos de pago convenidos con acreedores e instituciones financieras.',
            '2. Mantener la política de control de gastos sin flexibilizar los controles operativos.',
            '3. Fortalecer el patrimonio de la empresa reinvirtiendo las utilidades que se generen.',
        ],
        'cita_fuente': 'Sostenibilidad de procesos de saneamiento empresarial (Riquelme, 2018).',
    },
    ('Rojo', 'Amarillo'): {
        'id_codigo': 'MACRO-R-A',
        'transicion': 'Desescalamiento de Riesgo (Riesgo Crítico -> Riesgo Moderado)',
        'tipo': 'Desescalamiento de Insolvencia',
        'prioridad': 'Alta',
        'clase_badge': 'badge-status-alerta',
        'icono': 'bi-arrow-down-right-circle-fill',
        'titulo': 'Desescalamiento de Insolvencia: Cumplimiento de Acuerdos de Pago',
        'resumen_transicion': 'La empresa comienza a reducir su nivel de peligro pero permanece en una zona de alta vulnerabilidad financiera.',
        'accion_principal': (
            'Continuar firmemente con el plan de ordenamiento de deudas. Mantener una comunicación fluida y transparente '
            'con los bancos y proveedores para resguardar la continuidad de los suministros y la operatividad del negocio.'
        ),
        'procedimiento_pasos': [
            '1. Informar puntualmente a las entidades financieras sobre el avance del plan de orden interno.',
            '2. Reducir costos fijos mediante la optimización de procesos y la renegociación de contratos de arriendo o servicios.',
            '3. Llevar un control diario del saldo en cuenta corriente para evitar giros sin respaldo.',
        ],
        'cita_fuente': 'Control de tesorería y acuerdos comerciales (Ringeling, 2004; Ley 20.720).',
    },
    ('Rojo', 'Rojo'): {
        'id_codigo': 'MACRO-R-R',
        'transicion': 'Insolvencia Crítica Continuada',
        'tipo': 'Plan de Emergencia Concursal',
        'prioridad': 'Alta',
        'clase_badge': 'badge-status-critico',
        'icono': 'bi-shield-slash-fill',
        'titulo': 'Plan de Emergencia: Reorganización Legal Preventiva (Ley 20.720)',
        'resumen_transicion': 'Situación de insolvencia severa continua: la empresa proyecta mantenerse en una zona crítica donde las obligaciones superan largamente los ingresos.',
        'accion_principal': (
            'Evaluar con asesoría profesional especializada la activación del procedimiento de Reorganización Judicial '
            'o Extrajudicial contemplado en la Ley 20.720. Esta herramienta legal entrega Protección Financiera Concursal, '
            'deteniendo juicios de cobranza y embargos mientras se acuerda formalmente con los acreedores un plan de pagos viable.'
        ),
        'procedimiento_pasos': [
            '1. Consultar con asesoría legal o contable sobre los requisitos para acogerse a la Reorganización de la Ley 20.720.',
            '2. Detener inmediatamente pagos o traspasos de recursos que perjudiquen la igualdad entre acreedores.',
            '3. Proponer a los acreedores una fórmula de pago que incluya plazos razonables y meses de gracia para viabilizar la empresa.',
        ],
        'cita_fuente': 'Ley 20.720 de Reorganización y Liquidación de Empresas; Riquelme (2018).',
    },
}


# ==============================================================================
# 2. CATÁLOGO DE RECOMENDACIONES TÁCTICAS OPERATIVAS (LENGUAJE PROFESIONAL ACCESIBLE)
# ==============================================================================

RECOMENDACIONES_TACTICAS = {
    'razon_corriente': {
        'critico': {
            'id_codigo': 'TACT-RC-CRIT',
            'variable_origen': 'razon_corriente',
            'grupo_riesgo': 'Liquidez',
            'prioridad': 'Alta',
            'icono': 'bi-droplet-half',
            'titulo': 'Aceleración de Cobranza y Fortalecimiento de la Caja Inmediata',
            'plantilla_diagnostico': (
                'Por cada $1.000 que la empresa debe pagar en el corto plazo, dispone de apenas ${cobertura_pesos} en recursos disponibles. '
                'Esta holgura es insuficiente: cualquier atraso en el pago de clientes generará dificultades para cumplir con los compromisos del mes.'
            ),
            'que_hacer': (
                'Contactar formalmente a clientes con facturas que superen los 30 días de antigüedad para pactar fechas de cancelación o incentivos por pago anticipado. '
                'En caso de requerir liquidez urgente, evaluar la cesión de facturas por cobrar mediante servicios de anticipo (factoring) bancario para financiar la operación del mes.'
            ),
            'procedimiento': '1. Cobrar con prioridad las facturas vencidas con más de 30 días. 2. Ofrecer un 2% de descuento a clientes que paguen esta semana. 3. Acordar con proveedores plazos de pago a 60 días.',
            'fuente': 'Gestión de tesorería y pasivo circulante (Ringeling, 2004; Altman, 1983).',
        },
        'alerta': {
            'id_codigo': 'TACT-RC-ALER',
            'variable_origen': 'razon_corriente',
            'grupo_riesgo': 'Liquidez',
            'prioridad': 'Media',
            'icono': 'bi-droplet',
            'titulo': 'Sincronización del Calendario de Cobros y Pagos del Mes',
            'plantilla_diagnostico': (
                'Por cada $1.000 en compromisos inmediatos, la empresa dispone de ${cobertura_pesos}. '
                'La cobertura es justa y deja poco margen ante imprevistos operativos.'
            ),
            'que_hacer': (
                'Organizar el calendario de pagos a proveedores de modo que coincida con las fechas en que entran los pagos de clientes. '
                'Evitar comprometer pagos en semanas donde no se tenga certeza de recaudación.'
            ),
            'procedimiento': '1. Ajustar plazos de crédito a clientes nuevos a un máximo de 30 días. 2. Realizar promociones para vender mercadería que lleva tiempo en bodega.',
            'fuente': 'Control de ciclo de caja (Ringeling, 2004).',
        },
        'solvente': {
            'id_codigo': 'TACT-RC-SOLV',
            'variable_origen': 'razon_corriente',
            'grupo_riesgo': 'Liquidez',
            'prioridad': 'Baja',
            'icono': 'bi-droplet-fill',
            'titulo': 'Mantenimiento de la Cobertura de Caja y Aprovechamiento de Descuentos',
            'plantilla_diagnostico': (
                'La empresa dispone de ${cobertura_pesos} por cada $1.000 en deudas inmediatas, '
                'lo que representa una posición de liquidez cómoda y tranquila.'
            ),
            'que_hacer': (
                'Mantener el colchón de seguridad en la cuenta bancaria y aprovechar esta holgura para solicitar '
                'a los proveedores descuentos por pago al contado o anticipado, reduciendo costos de compra.'
            ),
            'procedimiento': '1. Mantener reservas de caja para imprevistos. 2. Negociar rebajas de precios con proveedores pagando al contado.',
            'fuente': 'Administración prudente de liquidez (Zurita, 2008).',
        },
    },

    'capital_trabajo_sobre_activos': {
        'critico': {
            'id_codigo': 'TACT-CT-CRIT',
            'variable_origen': 'capital_trabajo_sobre_activos',
            'grupo_riesgo': 'Liquidez',
            'prioridad': 'Alta',
            'icono': 'bi-wallet2',
            'titulo': 'Reconstitución del Fondo de Maniobra para la Operación',
            'plantilla_diagnostico': (
                'El capital de trabajo de la empresa es muy reducido o negativo ({valor_pct}% de los activos), '
                'lo que significa que los recursos disponibles en el corto plazo no alcanzan a financiar el ritmo habitual de trabajo.'
            ),
            'que_hacer': (
                'Se requiere convertir deudas urgentes de corto plazo en créditos en cuotas de mayor plazo (2 a 3 años), '
                'de manera que los ingresos del mes no se destinen por completo a pagar deudas inmediatas.'
            ),
            'procedimiento': '1. Solicitar al banco consolidar deudas corrientes en un crédito comercial a 36 meses. 2. No realizar retiros de dinero de los socios hasta recuperar la estabilidad.',
            'fuente': 'Preservación de capital de trabajo neto (Altman, 1983; Ringeling, 2004).',
        },
        'alerta': {
            'id_codigo': 'TACT-CT-ALER',
            'variable_origen': 'capital_trabajo_sobre_activos',
            'grupo_riesgo': 'Liquidez',
            'prioridad': 'Media',
            'icono': 'bi-wallet',
            'titulo': 'Ajuste del Fondo de Reserva para Operaciones',
            'plantilla_diagnostico': (
                'El capital disponible para el día a día representa el {valor_pct}% del total de recursos de la empresa, '
                'un nivel que aconseja prudencia en la programación de compras.'
            ),
            'que_hacer': (
                'Planificar las compras de mercadería e insumos de acuerdo a las ventas reales del mes, '
                'evitando comprar en exceso para no dejar dinero inmovilizado en bodegas.'
            ),
            'procedimiento': '1. Comprar solo lo necesario para el mes. 2. Monitorear semanalmente la diferencia entre lo que se tiene por cobrar y lo que se debe pagar.',
            'fuente': 'Fondo de maniobra operativo (Altman, 1983).',
        },
        'solvente': {
            'id_codigo': 'TACT-CT-SOLV',
            'variable_origen': 'capital_trabajo_sobre_activos',
            'grupo_riesgo': 'Liquidez',
            'prioridad': 'Baja',
            'icono': 'bi-wallet-fill',
            'titulo': 'Preservación de la Holgura Operativa del Negocio',
            'plantilla_diagnostico': (
                'El capital de trabajo representa el {valor_pct}% de los activos, '
                'entregando un respaldo seguro para solventar las operaciones habituales.'
            ),
            'que_hacer': (
                'Conservar esta holgura como base de estabilidad y asegurar que las nuevas ventas mantengan '
                'plazos de cobro razonables para no comprometer el capital de trabajo acumulado.'
            ),
            'procedimiento': '1. Conservar fondos de reserva para contingencias. 2. Mantener relaciones comerciales estables con clientes cumplidores.',
            'fuente': 'Solvencia en empresas operativas (Zurita, 2008).',
        },
    },

    'leverage_total': {
        'critico': {
            'id_codigo': 'TACT-LEV-CRIT',
            'variable_origen': 'leverage_total',
            'grupo_riesgo': 'Endeudamiento',
            'prioridad': 'Alta',
            'icono': 'bi-bank',
            'titulo': 'Reprogramación de Deudas de Corto Plazo a Mayor Plazo',
            'plantilla_diagnostico': (
                'El nivel de deuda actual supera en {veces_deuda} veces el patrimonio aportado por los dueños de la empresa. '
                'Gran parte del negocio está financiado por bancos y proveedores, lo que genera cuotas mensuales que absorben los ingresos.'
            ),
            'que_hacer': (
                'Solicitar a las instituciones financieras la consolidación de líneas de crédito y deudas de corto plazo '
                'en un crédito comercial a 24 o 36 meses, reduciendo el monto de la cuota mensual. '
                'Si existen obligaciones tributarias pendientes (IVA o declaraciones anuales), solicitar su pago en cuotas '
                'ante la Tesorería General de la República (TGR) para evitar cobros judiciales o restricciones bancarias.'
            ),
            'procedimiento': '1. Acudir al banco para unificar deudas caras en un crédito a 3 años. 2. Solicitar convenio de pago en cuotas ante la Tesorería (TGR) para deudas fiscales. 3. Suspender retiros de utilidades hasta que el endeudamiento baje.',
            'fuente': 'Estructuración prudencial del pasivo y alargamiento de plazos (Zurita, 2008; Ley 20.720).',
        },
        'alerta': {
            'id_codigo': 'TACT-LEV-ALER',
            'variable_origen': 'leverage_total',
            'grupo_riesgo': 'Endeudamiento',
            'prioridad': 'Media',
            'icono': 'bi-bank2',
            'titulo': 'Control de Nuevo Endeudamiento y Reemplazo de Deudas Caras',
            'plantilla_diagnostico': (
                'Las deudas equivalen a {veces_deuda} veces el patrimonio de los socios, '
                'un nivel que requiere no asumir nuevos créditos a corto plazo.'
            ),
            'que_hacer': (
                'Evitar tomar nuevos créditos de consumo o usar líneas de sobregiro costosas. '
                'Revisar si es posible sustituir compromisos caros por financiamiento con tasas preferenciales o garantías estatales de apoyo a pymes.'
            ),
            'procedimiento': '1. Consultar en la banca por opciones de refinanciamiento con garantía estatal (FOGAPE). 2. Pagar con prioridad las deudas con mayor costo financiero.',
            'fuente': 'Prudencia en la estructura de pasivos (Zurita, 2008).',
        },
        'solvente': {
            'id_codigo': 'TACT-LEV-SOLV',
            'variable_origen': 'leverage_total',
            'grupo_riesgo': 'Endeudamiento',
            'prioridad': 'Baja',
            'icono': 'bi-check-circle',
            'titulo': 'Mantenimiento de un Nivel de Deuda Equilibrado y Sostenible',
            'plantilla_diagnostico': (
                'El endeudamiento es moderado ({veces_deuda} veces el patrimonio), '
                'lo que demuestra que la empresa se financia de manera equilibrada y con bajo riesgo financiero.'
            ),
            'que_hacer': (
                'Mantener esta disciplina de financiamiento, recurriendo al crédito bancario únicamente '
                'para proyectos o compras que demuestren capacidad directa de generar su propio pago.'
            ),
            'procedimiento': '1. Mantener al día los compromisos bancarios para conservar una excelente calificación comercial.',
            'fuente': 'Estructura de financiamiento saludable (Zurita, 2008).',
        },
    },

    'roa_operacional': {
        'critico': {
            'id_codigo': 'TACT-ROA-CRIT',
            'variable_origen': 'roa_operacional',
            'grupo_riesgo': 'Rentabilidad',
            'prioridad': 'Alta',
            'icono': 'bi-graph-down',
            'titulo': 'Recuperación de la Rentabilidad de los Bienes y Equipos de la Empresa',
            'plantilla_diagnostico': (
                'Los bienes, maquinarias y recursos de la empresa están rindiendo muy poco ({valor_pct}% de rentabilidad sobre activos), '
                'lo que significa que la infraestructura instalada no está generando los ingresos esperados.'
            ),
            'que_hacer': (
                'Revisar si existen instalaciones, bodegas o maquinarias que no se estén utilizando para evaluar '
                'su venta o arriendo a terceros, transformando activos ociosos en dinero para pagar deudas o mejorar las operaciones.'
            ),
            'procedimiento': '1. Hacer inventario de maquinarias o vehículos sin uso. 2. Poner en arriendo o vender bienes ociosos para generar caja.',
            'fuente': 'Rendimiento y productividad de activos (Riquelme, 2018; Altman, 1983).',
        },
        'alerta': {
            'id_codigo': 'TACT-ROA-ALER',
            'variable_origen': 'roa_operacional',
            'grupo_riesgo': 'Rentabilidad',
            'prioridad': 'Media',
            'icono': 'bi-graph-up',
            'titulo': 'Aumento en el Uso y Productividad de las Instalaciones',
            'plantilla_diagnostico': (
                'El rendimiento de los activos se sitúa en un nivel modesto ({valor_pct}%), '
                'lo que indica que se puede producir o vender más con la misma infraestructura que ya se tiene.'
            ),
            'que_hacer': (
                'Buscar alternativas para aumentar el volumen de ventas utilizando las mismas máquinas, locales o personal, '
                'reduciendo los costos fijos por cada producto vendido.'
            ),
            'procedimiento': '1. Optimizar los horarios y turnos de trabajo. 2. Enfocar las ventas en los productos de mayor rotación.',
            'fuente': 'Eficiencia en activos empresariales (Riquelme, 2018).',
        },
        'solvente': {
            'id_codigo': 'TACT-ROA-SOLV',
            'variable_origen': 'roa_operacional',
            'grupo_riesgo': 'Rentabilidad',
            'prioridad': 'Baja',
            'icono': 'bi-graph-up-arrow',
            'titulo': 'Sostenimiento de la Alta Productividad de los Recursos',
            'plantilla_diagnostico': (
                'Los bienes y equipos de la empresa presentan un buen rendimiento ({valor_pct}%), '
                'generando resultados operacionales sólidos para el negocio.'
            ),
            'que_hacer': (
                'Mantener el buen cuidado y mantenimiento preventivo de las maquinarias y equipos '
                'para evitar fallas que detengan las ventas o generen gastos imprevistos.'
            ),
            'procedimiento': '1. Calendarizar mantenimientos periódicos. 2. Respaldar a las áreas de trabajo con mejor desempeño.',
            'fuente': 'Rendimiento operativo sostenible (Riquelme, 2018).',
        },
    },

    'margen_operacional': {
        'critico': {
            'id_codigo': 'TACT-MAR-CRIT',
            'variable_origen': 'margen_operacional',
            'grupo_riesgo': 'Rentabilidad',
            'prioridad': 'Alta',
            'icono': 'bi-percent',
            'titulo': 'Revisión de Precios de Venta y Eliminación de Ventas a Pérdida',
            'plantilla_diagnostico': (
                'Por cada $100.000 que la empresa vende, le quedan apenas ${ganancia_100k} de ganancia neta tras pagar los costos de operación. '
                'Este margen es demasiado estrecho: cualquier gasto no previsto deja al negocio en números rojos.'
            ),
            'que_hacer': (
                'Revisar con urgencia los precios de venta en los productos y servicios con menor margen para ajustarlos a los costos reales de compra o producción. '
                'Suspender descuentos comerciales extraordinarios que comprometan la rentabilidad de las ventas y auditar gastos innecesarios del día a día.'
            ),
            'procedimiento': '1. Revisar los precios de los productos que dejan menos margen y subirlos o descontinuarlos. 2. Eliminar descuentos comerciales automáticos a clientes. 3. Renegociar precios con los principales proveedores de insumos.',
            'fuente': 'Márgenes de ganancia y viabilidad empresarial (Riquelme, 2018).',
        },
        'alerta': {
            'id_codigo': 'TACT-MAR-ALER',
            'variable_origen': 'margen_operacional',
            'grupo_riesgo': 'Rentabilidad',
            'prioridad': 'Media',
            'icono': 'bi-percent',
            'titulo': 'Ajuste en Márgenes de Ganancia y Control de Gastos Hormiga',
            'plantilla_diagnostico': (
                'Por cada $100.000 vendidos, a la empresa le quedan ${ganancia_100k} de ganancia, '
                'un margen ajustado que aconseja controlar rigurosamente los gastos de administración.'
            ),
            'que_hacer': (
                'Revisar las compras pequeñas y gastos administrativos habituales para suprimir sobrecostos. '
                'Motivar al equipo de ventas a priorizar aquellos productos o servicios que dejan mayor ganancia limpia.'
            ),
            'procedimiento': '1. Incentivar la venta de los productos con mejor margen. 2. Controlar gastos de oficina y compras de última hora.',
            'fuente': 'Eficiencia operacional en ventas (Riquelme, 2018).',
        },
        'solvente': {
            'id_codigo': 'TACT-MAR-SOLV',
            'variable_origen': 'margen_operacional',
            'grupo_riesgo': 'Rentabilidad',
            'prioridad': 'Baja',
            'icono': 'bi-percent',
            'titulo': 'Defensa de los Márgenes Saludables y Compras por Volumen',
            'plantilla_diagnostico': (
                'La empresa mantiene un margen saludable, quedándose con ${ganancia_100k} limpios por cada $100.000 vendidos.'
            ),
            'que_hacer': (
                'Cuidar los márgenes actuales ante posibles alzas de precios en los insumos, '
                'negociando compras programadas con proveedores para congelar costos en períodos de varios meses.'
            ),
            'procedimiento': '1. Cotizar insumos con anticipación. 2. Mantener la estructura de precios sin ceder a guerras de precios desfavorables.',
            'fuente': 'Preservación de márgenes comerciales (Riquelme, 2018).',
        },
    },

    'rotacion_activos': {
        'critico': {
            'id_codigo': 'TACT-ROT-CRIT',
            'variable_origen': 'rotacion_activos',
            'grupo_riesgo': 'Eficiencia',
            'prioridad': 'Alta',
            'icono': 'bi-arrow-repeat',
            'titulo': 'Liquidación de Mercadería Estancada y Dinamización Comercial',
            'plantilla_diagnostico': (
                'Los activos de la empresa rotan a baja velocidad ({veces_rotacion}x al año), '
                'lo que significa que hay demasiado dinero inmovilizado en bodegas o inventarios en comparación con las ventas generadas.'
            ),
            'que_hacer': (
                'Realizar ventas especiales para liquidar mercadería que lleva más de 3 meses sin venderse, '
                'convirtiendo inventario quieto en dinero en efectivo para pagar compromisos del negocio.'
            ),
            'procedimiento': '1. Revisar inventarios y detectar productos estancados. 2. Realizar promociones de liquidación para recuperar el dinero invertido. 3. Comprar solo mercadería que tenga salida comprobada.',
            'fuente': 'Rotación de existencias y dinamismo comercial (Altman, 1983; Riquelme, 2018).',
        },
        'alerta': {
            'id_codigo': 'TACT-ROT-ALER',
            'variable_origen': 'rotacion_activos',
            'grupo_riesgo': 'Eficiencia',
            'prioridad': 'Media',
            'icono': 'bi-arrow-repeat',
            'titulo': 'Aceleración de Salida de Mercadería y Entrega a Clientes',
            'plantilla_diagnostico': (
                'La rotación de los recursos es moderada ({veces_rotacion}x al año), '
                'existiendo espacio para hacer que los productos salgan con mayor rapidez al mercado.'
            ),
            'que_hacer': (
                'Reducir los tiempos de entrega a los clientes y evitar comprar mercadería con mucha antelación '
                'para no acumular inventario que demore en transformarse en ventas cobradas.'
            ),
            'procedimiento': '1. Agilizar los despachos para cobrar antes. 2. Mantener inventarios más ajustados al consumo real semanal.',
            'fuente': 'Gestión ágil de existencias (Altman, 1983).',
        },
        'solvente': {
            'id_codigo': 'TACT-ROT-SOLV',
            'variable_origen': 'rotacion_activos',
            'grupo_riesgo': 'Eficiencia',
            'prioridad': 'Baja',
            'icono': 'bi-arrow-repeat',
            'titulo': 'Alta Agilidad en la Venta y Salida de Productos',
            'plantilla_diagnostico': (
                'La empresa mueve sus recursos con gran agilidad ({veces_rotacion}x al año), '
                'lo que demuestra una excelente dinámica comercial y adecuada rotación de existencias.'
            ),
            'que_hacer': (
                'Cuidar que la rapidez de las operaciones no genere quiebres de stock o retrasos de entrega '
                'en los productos estrella que sostienen el negocio.'
            ),
            'procedimiento': '1. Mantener stock de seguridad en los productos más demandados.',
            'fuente': 'Rotación óptima de activos (Zurita, 2008).',
        },
    },

    'volatilidad_flujo_caja': {
        'critico': {
            'id_codigo': 'TACT-VOL-CRIT',
            'variable_origen': 'volatilidad_flujo_caja',
            'grupo_riesgo': 'Flujo de Caja',
            'prioridad': 'Alta',
            'icono': 'bi-activity',
            'titulo': 'Estabilización de Entradas de Dinero y Diversificación de Clientes',
            'plantilla_diagnostico': (
                'Los ingresos diarios de la empresa tienen fluctuaciones muy marcadas, '
                'con días de mucha entrada seguidos de días de caja vacía, lo que genera tensiones en fechas de sueldos o pago de impuestos.'
            ),
            'que_hacer': (
                'Pactar con los clientes principales anticipos comerciales o pagos en fechas escalonadas, '
                'evitando depender de un solo cliente grande cuyo atraso pueda paralizar la cuenta bancaria de la empresa.'
            ),
            'procedimiento': '1. Pedir anticipos del 30% a 50% al tomar pedidos grandes. 2. Buscar nuevos clientes para no depender de pocos compradores. 3. Llevar un control diario de lo que entra y sale de la cuenta.',
            'fuente': 'Estabilidad de flujo diario de tesorería (Ringeling, 2004).',
        },
        'alerta': {
            'id_codigo': 'TACT-VOL-ALER',
            'variable_origen': 'volatilidad_flujo_caja',
            'grupo_riesgo': 'Flujo de Caja',
            'prioridad': 'Media',
            'icono': 'bi-activity',
            'titulo': 'Planificación de Pagos Fuertes y Fondo de Emergencia',
            'plantilla_diagnostico': (
                'Los ingresos presentan variaciones que pueden generar momentos de estrechez a fin de mes.'
            ),
            'que_hacer': (
                'Diseñar un presupuesto semanal para tener previsto cómo se pagarán los gastos más pesados '
                '(sueldos, imposiciones y pagos de IVA) con al menos 15 días de anticipación.'
            ),
            'procedimiento': '1. Separar con tiempo los fondos para remuneraciones e impuestos. 2. Coordinar fechas de cobro con clientes clave.',
            'fuente': 'Previsibilidad en el flujo de caja (Ringeling, 2004).',
        },
        'solvente': {
            'id_codigo': 'TACT-VOL-SOLV',
            'variable_origen': 'volatilidad_flujo_caja',
            'grupo_riesgo': 'Flujo de Caja',
            'prioridad': 'Baja',
            'icono': 'bi-activity',
            'titulo': 'Regularidad y Tranquilidad en los Ingresos de Caja',
            'plantilla_diagnostico': (
                'Las entradas de dinero en la empresa son regulares y constantes a lo largo del mes, '
                'lo que permite planificar compromisos y compras con alta tranquilidad.'
            ),
            'que_hacer': (
                'Mantener acuerdos comerciales de largo plazo que aseguren la continuidad de los ingresos '
                'y faciliten el cumplimiento ordenado de todos los pagos.'
            ),
            'procedimiento': '1. Fidelizar a los clientes cumplidores con buen servicio y atención.',
            'fuente': 'Constancia en recaudación operativa (Ringeling, 2004).',
        },
    },
}


# ==============================================================================
# 3. FUNCIONES DE SELECCIÓN DINÁMICA DE RECOMENDACIONES
# ==============================================================================

def clasificar_nivel(score: float) -> str:
    """Clasifica un score continuo (0-100) en el semáforo gerencial."""
    if score is None:
        return 'Sin Datos'
    try:
        s = float(score)
    except (ValueError, TypeError):
        return 'Sin Datos'

    if s <= 35.0:
        return 'Verde'
    elif s <= 70.0:
        return 'Amarillo'
    else:
        return 'Rojo'


def evaluar_severidad_variable(var_clave: str, v_dict: dict, nivel_proy: str, nivel_act: str) -> str:
    """
    Evalúa la severidad específica de una variable financiera contrastando su valor real
    contra umbrales empíricos de solvencia chilena y considerando el semáforo global proyectado.
    """
    if nivel_proy == 'Rojo':
        return 'critico'

    if var_clave == 'razon_corriente':
        val = float(v_dict.get('razon_corriente', v_dict.get('v1_razon_corriente', 1.5)) or 1.5)
        if val < 1.05:
            return 'critico'
        if val < 1.35 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    elif var_clave == 'capital_trabajo_sobre_activos':
        val = float(v_dict.get('capital_trabajo_sobre_activos', v_dict.get('v2_capital_trabajo_activos', 0.1)) or 0.1)
        if val < 0.05:
            return 'critico'
        if val < 0.18 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    elif var_clave == 'leverage_total':
        val = float(v_dict.get('leverage_total', v_dict.get('v3_leverage_total', 1.0)) or 1.0)
        if val > 2.5:
            return 'critico'
        if val > 1.4 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    elif var_clave == 'roa_operacional':
        val = float(v_dict.get('roa_operacional', v_dict.get('v4_roa_operacional', 0.05)) or 0.05)
        if val < 0.02:
            return 'critico'
        if val < 0.07 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    elif var_clave == 'margen_operacional':
        val = float(v_dict.get('margen_operacional', v_dict.get('v5_margen_operacional', 0.08)) or 0.08)
        if val < 0.03:
            return 'critico'
        if val < 0.08 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    elif var_clave == 'rotacion_activos':
        val = float(v_dict.get('rotacion_activos', v_dict.get('v6_rotacion_activos', 1.0)) or 1.0)
        if val < 0.6:
            return 'critico'
        if val < 1.1 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    elif var_clave == 'volatilidad_flujo_caja':
        val = float(v_dict.get('volatilidad_flujo_caja', v_dict.get('v7_volatilidad_flujo', 0.5)) or 0.5)
        if val > 1.2:
            return 'critico'
        if val > 0.6 or nivel_proy == 'Amarillo':
            return 'alerta'
        return 'solvente'

    if nivel_proy == 'Amarillo' or nivel_act == 'Amarillo':
        return 'alerta'
    return 'solvente'


def seleccionar_recomendaciones_para_periodo(
    score_actual: float,
    score_proyectado: float,
    variables_dict: dict = None,
    top_3_variables: list = None,
) -> dict:
    """
    Selecciona las recomendaciones estratégicas y operativas en Lenguaje Ejecutivo Accesible
    a partir del par (Score_Q_t, Score_Q_{t+1}) y del vector de variables financieras reales.

    Retorna un diccionario estructurado con:
      - 'macro': Recomendación Macro Estratégica (1)
      - 'tacticas': Lista de Recomendaciones Tácticas Operativas con diagnósticos cuantitativos (2 o 3)
      - 'meta': Información de niveles, scores y tendencia.
    """
    if score_actual is None:
        score_actual = 35.0
    if score_proyectado is None:
        score_proyectado = score_actual

    nivel_act = clasificar_nivel(score_actual)
    nivel_proy = clasificar_nivel(score_proyectado)

    # 1. Recomendación Macro de Transición
    clave_macro = (nivel_act, nivel_proy)
    rec_macro = dict(RECOMENDACIONES_MACRO_TRANSICION.get(
        clave_macro,
        RECOMENDACIONES_MACRO_TRANSICION.get(('Amarillo', 'Amarillo'))
    ))

    # 2. Selección de Variables Críticas
    variables_a_evaluar = []

    # Prioridad A: variables SHAP con impacto adverso
    if top_3_variables and isinstance(top_3_variables, list):
        for var_item in top_3_variables:
            if isinstance(var_item, dict):
                cod = var_item.get('clave') or var_item.get('codigo')
                for clave_cat in RECOMENDACIONES_TACTICAS.keys():
                    if cod and clave_cat in str(cod).lower():
                        if clave_cat not in variables_a_evaluar:
                            variables_a_evaluar.append(clave_cat)

    # Prioridad B: variables deducidas por valores observados
    v_dict = dict(variables_dict or {})
    rc = float(v_dict.get('razon_corriente', v_dict.get('v1_razon_corriente', 1.5)) or 1.5)
    if rc < 1.2 and 'razon_corriente' not in variables_a_evaluar:
        variables_a_evaluar.append('razon_corriente')

    lev = float(v_dict.get('leverage_total', v_dict.get('v3_leverage_total', 1.0)) or 1.0)
    if lev > 1.8 and 'leverage_total' not in variables_a_evaluar:
        variables_a_evaluar.append('leverage_total')

    marg = float(v_dict.get('margen_operacional', v_dict.get('v5_margen_operacional', 0.08)) or 0.08)
    if marg < 0.05 and 'margen_operacional' not in variables_a_evaluar:
        variables_a_evaluar.append('margen_operacional')

    ct = float(v_dict.get('capital_trabajo_sobre_activos', v_dict.get('v2_capital_trabajo_activos', 0.1)) or 0.1)
    if ct < 0.05 and 'capital_trabajo_sobre_activos' not in variables_a_evaluar:
        variables_a_evaluar.append('capital_trabajo_sobre_activos')

    vol = float(v_dict.get('volatilidad_flujo_caja', v_dict.get('v7_volatilidad_flujo', 0.5)) or 0.5)
    if vol > 1.2 and 'volatilidad_flujo_caja' not in variables_a_evaluar:
        variables_a_evaluar.append('volatilidad_flujo_caja')

    # Rellenar con dimensiones básicas si faltan
    dimensiones_defecto = ['razon_corriente', 'leverage_total', 'margen_operacional']
    for d in dimensiones_defecto:
        if d not in variables_a_evaluar:
            variables_a_evaluar.append(d)

    claves_seleccionadas = variables_a_evaluar[:3]

    # Construir recomendaciones tácticas personalizadas con valores cuantitativos reales
    tacticas_seleccionadas = []
    for var_clave in claves_seleccionadas:
        catalogo_var = RECOMENDACIONES_TACTICAS.get(var_clave)
        if not catalogo_var:
            continue

        # Nivel de severidad calibrado empíricamente según ratio y proyección
        sev = evaluar_severidad_variable(var_clave, v_dict, nivel_proy, nivel_act)

        base_tact = catalogo_var.get(sev) or catalogo_var.get('alerta')
        if not base_tact:
            continue

        rec_tact = dict(base_tact)

        # Inyectar datos cuantitativos reales en la plantilla de diagnóstico
        cobertura_pesos = f"${int(rc * 1000):,}".replace(',', '.') if rc > 0 else "$0"
        valor_pct = f"{ct * 100:.1f}" if ct is not None else "0.0"
        veces_deuda = f"{lev:.1f}" if lev is not None else "1.0"
        ganancia_100k = f"${int(max(0, marg * 100000)):,}".replace(',', '.') if marg is not None else "$0"
        rot = float(v_dict.get('rotacion_activos', v_dict.get('v6_rotacion_activos', 1.0)) or 1.0)
        veces_rot = f"{rot:.2f}"

        plantilla = rec_tact.get('plantilla_diagnostico', '')
        if plantilla:
            diagnostico_texto = plantilla.format(
                cobertura_pesos=cobertura_pesos,
                valor_pct=valor_pct,
                veces_deuda=veces_deuda,
                ganancia_100k=ganancia_100k,
                veces_rotacion=veces_rot,
            )
            rec_tact['diagnostico_operativo'] = diagnostico_texto
        else:
            rec_tact['diagnostico_operativo'] = rec_tact.get('que_hacer', '')

        tacticas_seleccionadas.append(rec_tact)

    delta = round(float(score_proyectado) - float(score_actual), 1)

    return {
        'macro': rec_macro,
        'tacticas': tacticas_seleccionadas,
        'meta': {
            'score_actual': round(float(score_actual), 1),
            'score_proyectado': round(float(score_proyectado), 1),
            'nivel_actual': nivel_act,
            'nivel_proyectado': nivel_proy,
            'delta_riesgo': delta,
            'tendencia': 'Deterioro' if delta > 1.5 else ('Mejora' if delta < -1.5 else 'Estable'),
        }
    }
