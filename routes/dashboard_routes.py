from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.contrato_model import buscar_por_servicio, buscar_contrato_especifico
from services.dashboard_service import (
    obtener_estadisticas_generales, 
    obtener_consumo_por_zona, 
    obtener_puntos_mapa,
    obtener_consumo_per_capita,
    obtener_resumen_errores,      # <-- NUEVA: Agregado para infraestructura
    obtener_estado_radiobases,    # <-- NUEVA: Agregado para infraestructura
    obtener_deuda_alcaldia        # <-- ¡AÑADIDA AQUÍ!: Para conectar la liquidación express con el tarifario SQL
)

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard/alcaldia")
def alcaldia():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template("dashboard/alcaldia.html", 
                           stats=obtener_estadisticas_generales(), 
                           consumo_zonas=obtener_consumo_por_zona(),
                           puntos=obtener_puntos_mapa())


@dashboard_bp.route("/dashboard/sostenibilidad")
def sostenibilidad():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # 1. Obtenemos los datos de consumo calculados con la población por distrito
    datos_sostenibilidad = obtener_consumo_per_capita()
    
    # 2. Enviamos los datos estructurados al template correspondiente
    return render_template("dashboard/sostenibilidad.html", datos=datos_sostenibilidad)


@dashboard_bp.route("/dashboard/infraestructura")
def infraestructura():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    try:
        # 1. Consumimos los datos técnicos reales de tu base de datos (9 errores y antenas)
        errores = obtener_resumen_errores()
        antenas = obtener_estado_radiobases()
        
        # 2. Generamos las métricas dinámicas automáticas basadas en tu BD para las tarjetas KPI
        stats_tecnicas = {
            "total_antenas": len(antenas),
            "tipos_error_registrados": len(errores), # Retornará 9 automáticamente por tus registros reales
            "alertas_criticas_hoy": 3  # Valor estático simulado de incidentes operativos diarios
        }
        
        # 3. Renderizamos la plantilla enviándole todas las colecciones de datos
        return render_template(
            "dashboard/infraestructura.html",
            errores=errores,
            antenas=antenas,
            stats=stats_tecnicas
        )
    except Exception as e:
        print(f"Error al cargar la vista de infraestructura: {e}")
        return "Error interno del servidor al procesar hardware IoT", 500


@dashboard_bp.route("/api/buscar")
def api_buscar():
    query = request.args.get('q')
    tipo = request.args.get('tipo') 
    
    if tipo == 'servicio':
        # Usamos la función masiva
        resultados = buscar_por_servicio(query)
        es_masivo = True
    else:
        # Usamos la función específica (nombre, contrato, medidor)
        resultados = buscar_contrato_especifico(query)
        es_masivo = False
    
    if resultados:
        return jsonify({
            'encontrado': True,
            'data': resultados,
            'es_masivo': es_masivo
        })
    return jsonify({'encontrado': False})


# =====================================================================
# NUEVO ENDPOINT: CONECTA PAGOS.JS CON EL TARIFARIO DINÁMICO SQL
# =====================================================================
@dashboard_bp.route("/api/deuda-alcaldia")
def api_deuda_alcaldia():
    """Endpoint asíncrono que retorna la liquidación express usando el número de contrato."""
    num_contrato = request.args.get('q', '').strip()
    
    if not num_contrato:
        return jsonify({
            "error": True, 
            "msg": "Por favor ingrese un número de contrato válido."
        }), 400
        
    try:
        # Pasa el número de contrato directo a tu servicio SQL
        resultado = obtener_deuda_alcaldia(num_contrato)
        
        if resultado:
            return jsonify({
                "error": False,
                "data": resultado
            }), 200
        else:
            return jsonify({
                "error": True,
                "msg": f"No se encontró ningún contrato activo bajo el código: '{num_contrato}'."
            }), 404
            
    except Exception as e:
        print(f"Error crítico en el enrutador de liquidaciones: {e}")
        return jsonify({
            "error": True,
            "msg": "Error interno del servidor al procesar las tarifas."
        }), 500