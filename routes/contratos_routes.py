from flask import Blueprint, render_template, request, redirect, url_for, jsonify
# Importamos desde models.contrato_model (la carpeta y archivo correcto en singular)
from models.contrato_model import (
    obtener_contratos, obtener_contrato_por_id, 
    insertar_contrato, actualizar_contrato, eliminar_contrato_db
)

contratos_bp = Blueprint("contratos", __name__)

# ==========================================================================
#  RUTAS PARA LA WEB (Vistas HTML)
# ==========================================================================

@contratos_bp.route('/contratos/lista', methods=['GET'])
def lista_contratos():
    try:
        # Devuelve solo los últimos 10 ordenados por fecha
        datos = obtener_contratos()
        return render_template('contratos/lista.html', contratos=datos)
    except Exception as e:
        print(f"Error en vista HTML /contratos/lista: {e}")
        return render_template('contratos/lista.html', contratos=[])


# ==========================================================================
#  RUTAS DE API JSON (Manejadas por JS / Fetch API)
# ==========================================================================

# 1. OBTENER UN CONTRATO ESPECÍFICO (Para rellenar el modal de edición)
@contratos_bp.route('/api/contratos/<string:id>', methods=['GET'])
def api_obtener_contrato(id):
    try:
        contrato = obtener_contrato_por_id(id)
        if contrato:
            return jsonify({
                'status': 'success', 
                'contrato': contrato
            }), 200
        return jsonify({
            'status': 'error', 
            'message': 'Contrato no encontrado'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f"Error en el servidor: {str(e)}"
        }), 500


# 2. CREAR UN NUEVO CONTRATO
@contratos_bp.route('/api/contratos/crear', methods=['POST'])
def api_crear_contrato():
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON'}), 400
        
    numero_contrato = data.get('numero_contrato')
    if not numero_contrato:
        return jsonify({'status': 'error', 'message': 'El Número de Contrato es obligatorio'}), 400

    try:
        insertar_contrato(data)
        return jsonify({
            'status': 'success', 
            'message': f'Contrato {numero_contrato} registrado exitosamente'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f"Error al guardar: {str(e)}"
        }), 500


# 3. EDITAR UN CONTRATO EXISTENTE
@contratos_bp.route('/api/contratos/editar/<string:id>', methods=['POST'])
def api_editar_contrato(id):
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON'}), 400

    try:
        actualizar_contrato(id, data)
        return jsonify({
            'status': 'success', 
            'message': f'Contrato {id} actualizado con éxito'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f"Error al modificar: {str(e)}"
        }), 500


# 4. ELIMINAR UN CONTRATO
@contratos_bp.route('/api/contratos/eliminar/<string:id>', methods=['DELETE'])
def api_eliminar_contrato(id):
    try:
        eliminar_contrato_db(id)
        return jsonify({
            'status': 'success', 
            'message': f'Contrato {id} eliminado correctamente'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f"Error al eliminar de la base de datos: {str(e)}"
        }), 500