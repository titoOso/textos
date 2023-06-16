import os

# configuraciones. True para que el servidor pueda ser levantado en modo debug
DEBUG = True

# configuracion BD

POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres',
    'db': 'datostextos',
    'host': '172.18.0.2',
    'port': '5432',
}


SECRET_KEY =  'CLAVE SECRETA'

SQLALCHEMY_TRACK_MODIFICATIONS = False

#postgresql://username:password@hostname/database
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:ricardo@172.18.0.2:5432/datostextos"
"""SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES['user']}:" \
                          f"{POSTGRES['pw']}@{POSTGRES['host']}:" \
                          f"{POSTGRES['port']}/{POSTGRES['db']}"
"""
