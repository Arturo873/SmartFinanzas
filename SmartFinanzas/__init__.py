from django.db.backends.mysql.base import DatabaseWrapper

# Permitir compatibilidad con versiones de MariaDB anteriores a 10.11 (ej: MariaDB 10.4 en XAMPP)
DatabaseWrapper.check_database_version_supported = lambda self: None

