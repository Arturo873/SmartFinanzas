from django.core.management.base import BaseCommand

from AppWeb.datos_macro import RUTA_CSV_MACRO, actualizar_csv_macro


class Command(BaseCommand):
    help = 'Descarga del Banco Central de Chile las series trimestrales de V8 (PIB, tasa UF, TCR).'

    def add_arguments(self, parser):
        parser.add_argument('--desde', type=int, default=2009, help='Año inicial de las series')

    def handle(self, *args, **opciones):
        df = actualizar_csv_macro(opciones['desde'])
        self.stdout.write(self.style.SUCCESS(
            f'{len(df)} trimestres guardados en {RUTA_CSV_MACRO} ({df.index[0]} a {df.index[-1]}).'
        ))
