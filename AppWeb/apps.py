from django.apps import AppConfig


class AppwebConfig(AppConfig):
    name = 'AppWeb'

    def ready(self):
        # Carga el modelo al iniciar el servidor, para que la primera
        # predicción no pague el tiempo de lectura del archivo (RNF-05 < 3 s).
        from .viewsML import _cargar_modelo_oficial
        _cargar_modelo_oficial()
