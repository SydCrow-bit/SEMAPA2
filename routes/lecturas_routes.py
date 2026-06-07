from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.lecturas_model import obtener_lecturas, insertar_lectura, eliminar_lectura
from database import get_connection # Lo necesitamos para una consulta rápida de la API

lecturas_bp = Blueprint("lecturas", __name__)

# ==========================================
#  RUTAS PARA LA WEB (Vistas HTML)
# ==========================================

@lecturas_bp.route("/lecturas/lista")
def lista_lecturas():
    query = request.args.get('q') 
    datos = obtener_lecturas(query)
    return render_template("lecturas/lista.html", lecturas=datos, busqueda=query)

@lecturas_bp.route("/lecturas/guardar", methods=['POST'])
def guardar():
    medidor = request.form.get('medidor')
    ant = request.form.get('lec_anterior')
    act = request.form.get('lec_actual')
    radio = request.form.get('radiobase')
    insertar_lectura(medidor, ant, act, radio)
    return redirect(url_for('lecturas.lista_lecturas'))

@lecturas_bp.route("/lecturas/eliminar/<int:id>")
def eliminar(id):
    eliminar_lectura(id)
    return redirect(url_for('lecturas.lista_lecturas'))


# ==========================================
#  RUTAS PARA LA APP MÓVIL (API JSON)
# ==========================================

# 1. RUTA PARA BUSCAR UN MEDIDOR DESDE EL CELULAR
# Cuando el inspector escanee el medidor en campo, la app llamará a esta ruta
# para saber cuál fue la última lectura registrada de ese medidor.
@lecturas_bp.route("/api/lecturas/buscar/<string:medidor_id>", methods=['GET'])
def api_buscar_medidor(medidor_id):
    conn = get_connection()
    cur = conn.cursor()
    
    # Buscamos la última lectura válida de ese medidor específico
    query = """
        SELECT lecturaactual 
        FROM lecturas 
        WHERE medidor_iot = %s AND lecturaactual IS NOT NULL 
        ORDER BY fechahoralectura DESC 
        LIMIT 1;
    """
    cur.execute(query, (medidor_id,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    
    # Si el medidor ya existe en el sistema, mandamos su última lectura como "Lectura Anterior"
    if resultado:
        return jsonify({
            "status": "success",
            "medidor_iot": medidor_id,
            "ultima_lectura": float(resultado[0])
        }), 200
    else:
        # Si es un medidor totalmente nuevo que no tiene historial
        return jsonify({
            "status": "success",
            "medidor_iot": medidor_id,
            "ultima_lectura": 0.0
        }), 200


# 2. RUTA PARA QUE LA APP REGISTRE LA LECTURA MANUAL
# La aplicación móvil enviará un paquete JSON mediante un método POST a esta ruta.
@lecturas_bp.route("/api/lecturas/registrar", methods=['POST'])
def api_registrar_lectura():
    # Obtenemos los datos que envía la app móvil en formato JSON
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No se recibieron datos JSON"}), 400
        
    medidor = data.get('medidor')
    lec_ant = data.get('lec_anterior')
    lec_act = data.get('lec_actual')
    radio = data.get('radiobase') # Opcional
    
    # Validaciones mínimas de seguridad
    if not medidor or lec_ant is None or lec_act is None:
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400
        
    # Validación comercial: La lectura actual no puede ser menor a la anterior
    if float(lec_act) < float(lec_ant):
        return jsonify({"status": "error", "message": "La lectura actual no puede ser menor a la anterior"}), 400

    try:
        # Reutilizamos tu función del modelo para insertar a la base de datos
        insertar_lectura(medidor, lec_ant, lec_act, radio)
        
        return jsonify({
            "status": "success", 
            "message": f"Lectura del medidor {medidor} guardada exitosamente"
        }), 201
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500
    
@lecturas_bp.route("/app/registrar")
def app_registrar_pantalla():
    # Esta ruta simplemente muestra la interfaz limpia para el celular del inspector
    return render_template("lecturas/app_registrar.html")