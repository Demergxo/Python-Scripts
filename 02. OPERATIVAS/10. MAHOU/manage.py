#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logistica.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y disponible en tu entorno?\n"
            "Activa tu entorno virtual o instala Django con `pip install django`."
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

