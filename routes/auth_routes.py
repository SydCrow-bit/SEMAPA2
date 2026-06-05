from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.usuario_model import obtener_usuario_por_username

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = obtener_usuario_por_username(username)

        # usuario[1] es username, usuario[2] es password (ajusta según tu tabla)
        if usuario and usuario[2] == password:
            session['user_id'] = usuario[0]
            session['username'] = usuario[1]
            session['rol'] = usuario[3]
            return redirect(url_for('dashboard.alcaldia'))
        else:
            # Si falla, mandamos un mensaje de error
            return render_template("login/login.html", error="Credenciales incorrectas")
            
    return render_template("login/login.html")