from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# instancia Flask
app = Flask(__name__)
admin = Admin(app)

# lee la config desde el archivo config.py
app.config.from_pyfile('config.py')

# inicializa la base de datos con la config leida
db = SQLAlchemy(app)




# rutas disponibles
from routes import *
from models.models import Consulta, Resultados, Usuario, Errores

# Los modelos que queremos mostrar en el admin
admin.add_view(ModelView(Consulta, db.session))
admin.add_view(ModelView(Resultados, db.session))
admin.add_view(ModelView(Errores, db.session))
#Agrego el modelo Usuario al Flask Admin
admin.add_view(ModelView(Usuario, db.session))

# subimos el server (solo cuando se llama directamente a este archivo)
if __name__ == '__main__':
    app.run(debug=True)