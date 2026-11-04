from django.db.backends.mysql.base import DatabaseWrapper

# Permitir compatibilidad con versiones de MariaDB anteriores a 10.11 (ej: MariaDB 10.4 en XAMPP)
DatabaseWrapper.check_database_version_supported = lambda self: None

# Compatibilidad de Django 4.2 con Python 3.14 (copia de contexto en pruebas y depuración)
try:
    from django.template.context import BaseContext
    def _base_context_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.dicts = self.dicts[:]
        return duplicate
    BaseContext.__copy__ = _base_context_copy
except Exception:
    pass
