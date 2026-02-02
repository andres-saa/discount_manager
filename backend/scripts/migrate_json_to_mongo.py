#!/usr/bin/env python3
"""Script de migración JSON -> MongoDB (deprecado).

El backend ahora usa archivos JSON locales en data/ por defecto.
Este script requiere pymongo y MONGODB_URI para migrar a MongoDB.
"""
import sys

if __name__ == "__main__":
    print("El backend usa almacenamiento JSON local (data/*.json).")
    print("Este script de migración a MongoDB está desactivado.")
    print("Para usar MongoDB, restaura database.py y pymongo, y configura MONGODB_URI.")
    sys.exit(0)
