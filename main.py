#!/usr/bin/env python3
"""
ADN Suma Get - Sistema de extracción de datos de aduanas
Punto de entrada principal de la aplicación
"""

import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli.commands import cli

if __name__ == '__main__':
    cli() 