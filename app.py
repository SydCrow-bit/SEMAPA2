from flask import Flask, redirect, url_for # Importa redirect y url_for
from routes.auth_routes import auth_bp
from scripts.cargar_contratos import cargar_bp
from routes.dashboard_routes import dashboard_bp
from routes.lecturas_routes import lecturas_bp
from routes.contratos_routes import contratos_bp
from routes.totem_routes import totem_bp

app = Flask(__name__)
app.secret_key = "passwoard" 

app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(cargar_bp)
app.register_blueprint(lecturas_bp)
app.register_blueprint(contratos_bp)
app.register_blueprint(totem_bp)

@app.route("/")
def inicio():
    # Esto hace que al entrar a http://127.0.0.1:5000/ te mande a /login
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)