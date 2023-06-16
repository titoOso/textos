# coding=utf-8
# importamos la instancia de Flask (app)
from lecturaArchivo import lecturaArchivo
from appTextos import app
from forms.consultaTexto import consultaTexto
from forms.login import LoginForm
from forms.register import RegisterForm
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask import render_template, redirect, url_for, flash, request, session, jsonify, abort
from datetime import datetime
from sqlalchemy import func
from appTextos import db


# importamos los modelos a usar
from models.models import Consulta, Resultados, Usuario

from flask import render_template, session, redirect, url_for


# para poder usar Flask-Login
login_manager = LoginManager(app)
parrafoMaximo = 100000

@app.route('/busquedaEnArchivoTexto', methods=['GET'])
def index():
    inicializo()
    return render_template('index.html', tiempo=tiempoDeConsulta())

@app.route('/busquedaEnArchivoTexto/consultar', methods=['GET','POST'])
def consultar():
    form = consultaTexto()
    if form.validate_on_submit():
        # nodo = StringField('Nodo', validators=[InputRequired()])
        # path = StringField('Path', validators=[InputRequired()])
        # nombreArchivo = StringField('Nombre Archivo', validators=[InputRequired()])
        # fechaLog = StringField('Fecha log Archivo', validators=[InputRequired()])
        # valores = StringField('Valores', validators=[InputRequired()])
        # filtros = StringField('Fitros', validators=[InputRequired()])
        # merge = StringField('Merge', validators=[InputRequired()])
        # pathArchivoMerge = StringField('Path Archivo Merge', validators=[InputRequired()])
        # nombreArchivoMerge = StringField('Nombre Archivo Merge', validators=[InputRequired()])
        #user = Usuario.get_by_email(form.email.data)
        ( resultado, frase_por_prefijo_busqueda , todas_las_coincidencias) = lecturaArchivo(form)
        if resultado:
            grabarConsulta(form, frase_por_prefijo_busqueda, todas_las_coincidencias)
            return render_template("verResultados.html", resultados=frase_por_prefijo_busqueda)
        else:
            return render_template("errores.html", mensaje=session["mensaje"],tiempo=tiempoDeConsulta())
    return render_template("consultaTexto.html", form=form)


def grabarConsulta(form, frase_por_prefijo_busqueda, todas_las_coincidencias):
    # id = db.Column(db.Integer, primary_key=True)
    # tipo = db.Column(db.String(30), nullable=True)
    # valores = db.Column(db.String(160), nullable True)
    # fecha = db.Column(db.DateTime, nullable=False)
    # ambiente = db.Column(db.String(30), nullable=True)
    # nodo = db.Column(db.Integer, nullable=True)
    # nombreArchivo = db.Column(db.String(80), nullable=False)
    # fechalog = db.Column(db.Date, nullable=False)
    # resultado = db.Column(db.Boolean, nullable=False)
    # resultados = db.relationship('Resultado', backref='consulta', lazy='dynamic')
    valorFecha = datetime.today()
    fechalogstr = form.fechaLog.data
    fechalog = datetime.strptime(fechalogstr, '%Y-%m-%d')
    consulta = db.session.query(func.max(Consulta.id)).first()
    consulta = Consulta(fecha=valorFecha, valores=form.valores.data, filtros=form.filtros.data, servidor=form.servidor.data
                        , ambiente=form.ambiente.data, fechalog=fechalog, resultado=True, nodo=int(form.nodo.data))
    nombreArchivo = form.path.data+form.nombreArchivo.data
    consulta.nombreArchivo = nombreArchivo
    # resultados de la consulta
    for clave in frase_por_prefijo_busqueda:
        resultado = Resultados()
        hora = str(datetime.strptime(clave, '%H:%M:%S,%f')).split(" ")[1]
        resultado.hora = hora
        coincidencias = " ".join(todas_las_coincidencias[clave])
        resultado.coincidencias = coincidencias
        resultado.parrafo = frase_por_prefijo_busqueda[clave]
        if (len(resultado.parrafo)> parrafoMaximo):
            resultado.parrafo = resultado.parrafo[:parrafoMaximo]

        consulta.resultados.append(resultado)
    consulta.save()

@app.route('/busquedaEnArchivoTexto/verResultadoConsulta/<id_consulta>', methods=['GET'])
def resultadoConsulta(id_consulta):
    consulta = Consulta.query.filter_by(id=id_consulta).first()
    resultados = Resultados.query.filter_by(consulta_id=id_consulta).all()
    return render_template("resultados.html", resultados=resultados,consulta=consulta)

@app.route('/busquedaEnArchivoTexto/consultas', methods=['GET'])
def listaConsultas():
    consultas = Consulta.query.all()
    return render_template('resultado.html', consultas=consultas)

def inicializo():
    session.clear()
    session["inicio"] = datetime.today()
    session["mensaje"] = " "

def termino():
    return True

def tiempoDeConsulta():
    tzinfo = session["inicio"].tzinfo

    return str(datetime.now(tzinfo) - session["inicio"]).split(".")[0]

# controles de acceso a trivia con login, register y la herramienta
@app.route('/busquedaEnArchivoTexto/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('index.html', tiempo=tiempoDeConsulta())
    form = LoginForm()
    if form.validate_on_submit():
        #get by email valida
        user = Usuario.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            # funcion provista por Flask-Login, el segundo parametro gestion el "recordar"
 #           login_user(user, remember=form.remember_me.data)
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page:
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Usuario o contraseña invalido')
            return redirect(url_for('login'))
    # no loggeado, dibujamos el login con el forms vacio
    return render_template('login.html', form=form)

#le decimos a Flask-Login como obtener un usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))


@app.route("/busquedaEnArchivoTexto/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return render_template('index.html', tiempo=tiempoDeConsulta())
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = Usuario.get_by_email(email)
        if user is not None:
            flash('El email {} ya está siendo utilizado por otro usuario'.format(email))
        else:
            # Creamos el usuario y lo guardamos
            user = Usuario(name=username, email=email, admin=False)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
#            return redirect(url_for('index'))
            return render_template('index.html', tiempo=tiempoDeConsulta())
    return render_template("register.html", form=form)

@app.route("/busquedaEnArchivoTexto/logout")
@login_required
def logout():
    logout_user()
    return render_template('index.html', tiempo=tiempoDeConsulta())
#    return redirect(url_for('index'))
