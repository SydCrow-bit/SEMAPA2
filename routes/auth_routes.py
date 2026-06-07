from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.usuario_model import obtener_usuario_por_username

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = obtener_usuario_por_username(username)

        if usuario and usuario[2] == password:
            session['user_id'] = usuario[0]
            session['username'] = usuario[1]
            session['rol'] = usuario[3]
            
            # --- DETECCIÓN DE DISPOSITIVO MÓVIL ---
            user_agent = request.headers.get('User-Agent', '').lower()
            es_movil = any(palabra in user_agent for palabra in ['mobile', 'android', 'iphone', 'blackberry'])
            
            if es_movil:
                # Si es celular, va directo a la interfaz de captura manual
                return redirect(url_for('lecturas.app_registrar_pantalla'))
            else:
                # Si es computadora, va al dashboard administrativo normal
                return redirect(url_for('dashboard.alcaldia'))
        else:
            return render_template("login/login.html", error="Credenciales incorrectas")
            
    return render_template("login/login.html")
# --- AGREGA ESTA FUNCIÓN AQUÍ ABAJO ---

@auth_bp.route("/logout")
def logout():
    # Limpiamos todos los datos de la sesión actual
    session.clear()
    # Redirigimos al usuario a la ruta login del Blueprint 'auth'
    return redirect(url_for("auth.login"))