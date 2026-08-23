
TIPO_PROVEEDOR = (
    ('MP', 'Materia Prima'),
    ('PT', 'Producto Terminado'),
    ('EM', 'Embalaje'),
    ('EQ', 'Equipamiento'),
    ('SR', 'Servicio'),
)

ESTADO_PROVEEDOR = (
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
    ('BLOQUEADO', 'Bloqueado'),
)

EVALUACION_CALIDAD = (
    (1, '1 Estrella'),
    (2, '2 Estrellas'),
    (3, '3 Estrellas'),
    (4, '4 Estrellas'),
    (5, '5 Estrellas'),
)


CONDICIONES_PAGO = (
    ("CONTADO", "Contado"),
    ("30_DIAS", "30 días"),
    ("45_DIAS", "45 días"),
    ("60_DIAS", "60 días"),
    ("90_DIAS", "90 días"),
)

MONEDAS = (
    ("CLP", "CLP - Peso Chileno"),
    ("USD", "USD - Dólar Estadounidense"),
    ("EUR", "EUR - Euro"),
    ("ARS", "ARS - Peso Argentino"),
    ("BRL", "BRL - Real Brasileño"),
    ("COP", "COP - Peso Colombiano"),
    ("PEN", "PEN - Sol Peruano"),
    ("MXN", "MXN - Peso Mexicano"),
)
