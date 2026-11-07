"""
Capa de Presentación Gerencial (Dashboard).

Siguiendo las directrices arquitectónicas del sistema:
Esta app NO define modelos propios.
Consume información mediante dependencias de lectura de las otras aplicaciones:
- moduloETL (RatioFinanciero)
- moduloTransaccional (Venta, CierreCaja)
- capaAnalitica (PrediccionRiesgo)
- usuarios (Usuario, Empresa)
"""

# No models defined here. Pure presentation layer.
