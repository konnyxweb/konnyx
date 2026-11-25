import os
import sys

# Asegurar que el directorio de la aplicación esté en sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación Flask para cPanel / Passenger WSGI
from app import app as application
