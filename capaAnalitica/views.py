"""
Capa Analítica - Capa de Servicio Interno de Inferencia ML y SHAP.

Siguiendo las directrices arquitectónicas del sistema:
Esta app actúa como un servicio interno (Service Layer en services.py) invocado
por otras aplicaciones del monolito (moduloETL, dashboard, etc.).
NO contiene vistas HTML ni renderizado de plantillas.
"""

# Capa de Servicio desacoplada: Toda la lógica de inferencia reside en services.py
