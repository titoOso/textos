#!/usr/bin/env python
# -*- coding: utf-8 -*-

from appTextos import db
from models.models import Consulta, Resultados, Usuario, Errores

db.drop_all()
db.create_all()

#Usuarios
q_u1 = Usuario(name = "Ricardo", email = "rmoran@antel.com.uy", admin = True)
# el pass lo seteamos con el método set_password para que se guarde con hash
q_u1.set_password("ricardo");
# por defecto, el usuario no es admin
q_u2 = Usuario(name = "Tito", email = "mtito@antel.com.uy")
q_u2.set_password("12345");

# agregamos todo a la sesión y luego commmiteamos

db.session.add(q_u1)
db.session.add(q_u2)
db.session.commit()


#Creo un usuario administrador
admin = Usuario(name="Administrador",email="admin@app.com",admin=True)
admin.set_password("passwd")
db.session.add(admin)
db.session.commit()