from database import get_connection

# ==========================================================================
# 1. FUNCIONES EXISTENTES (Búsqueda, Filtros Geográficos e Infraestructura)
# ==========================================================================

def buscar_contrato_especifico(query):
    conn = get_connection()
    cur = conn.cursor() 
    
    cur.execute("""
        SELECT c.numero_contrato, c.titular_contrato, i.latitud, i.longitud, 
               c.medidor_iot, c.tipo_servicio, c.categoria, i.distrito,
               c.fecha_contrato
        FROM contratos c
        JOIN infraestructura i ON c.numero_catastro = i.numero_catastro
        WHERE CAST(c.numero_contrato AS TEXT) LIKE %s 
           OR c.titular_contrato LIKE %s 
           OR c.medidor_iot LIKE %s
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    rows = cur.fetchall()
    resultados = []
    for row in rows:
        resultados.append({
            'numero_contrato': row[0], 
            'nombre': row[1], 
            'lat': row[2], 
            'lng': row[3], 
            'medidor': row[4], 
            'servicio': row[5], 
            'categoria': row[6], 
            'distrito': row[7],
            'fecha': str(row[8]) if row[8] else None
        })
    cur.close()
    conn.close()
    return resultados

def buscar_por_servicio(servicio):
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("""
        SELECT c.numero_contrato, c.titular_contrato, i.latitud, i.longitud, 
               c.medidor_iot, c.tipo_servicio, c.categoria, i.distrito,
               c.fecha_contrato
        FROM contratos c
        JOIN infraestructura i ON c.numero_catastro = i.numero_catastro
        WHERE c.tipo_servicio = %s
    """, (servicio,))
    
    rows = cur.fetchall()
    resultados = []
    for row in rows:
        resultados.append({
            'numero_contrato': row[0], 
            'nombre': row[1], 
            'lat': row[2], 
            'lng': row[3], 
            'medidor': row[4], 
            'servicio': row[5], 
            'categoria': row[6],
            'distrito': row[7],
            'fecha': str(row[8]) if row[8] else None
        })
    cur.close()
    conn.close()
    return resultados

def buscar_por_rango_fechas(fecha_inicio, fecha_fin):
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("""
        SELECT c.numero_contrato, c.titular_contrato, i.latitud, i.longitud, 
               c.medidor_iot, c.tipo_servicio, c.categoria, i.distrito,
               c.fecha_contrato
        FROM contratos c
        JOIN infraestructura i ON c.numero_catastro = i.numero_catastro
        WHERE c.fecha_contrato BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    
    rows = cur.fetchall()
    resultados = []
    for row in rows:
        resultados.append({
            'numero_contrato': row[0], 
            'nombre': row[1], 
            'lat': row[2], 
            'lng': row[3], 
            'medidor': row[4], 
            'servicio': row[5], 
            'categoria': row[6], 
            'distrito': row[7],
            'fecha': str(row[8]) if row[8] else None
        })
    cur.close()
    conn.close()
    return resultados


# ==========================================================================
# 2. FUNCIONES PARA LA TABLA GENERAL Y CRUD (Últimos 10 por fecha)
# ==========================================================================

def obtener_contratos():
    """Obtiene únicamente los 10 últimos contratos ordenados por fecha de contrato"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT numero_contrato, numero_catastro, titular_contrato, ci_titular, 
               categoria, subcategoria, medidor_iot, fecha_contrato, 
               estado_contrato, diametro_conexion, tipo_servicio 
        FROM contratos 
        ORDER BY fecha_contrato DESC
        LIMIT 10;
    """
    cur.execute(query)
    
    columnas = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    
    # Mapeamos a diccionario para compatibilidad directa con Jinja2 en lista.html
    contratos = [dict(zip(columnas, fila)) for fila in rows]
    
    cur.close()
    conn.close()
    return contratos

def obtener_contrato_por_id(numero_contrato):
    """Obtiene los campos de un contrato específico (Corregido nombre sin la 'c' intrusa)"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = "SELECT * FROM contratos WHERE numero_contrato = %s;"
    cur.execute(query, (numero_contrato,))
    
    columnas = [desc[0] for desc in cur.description]
    row = cur.fetchone()
    
    contrato = dict(zip(columnas, row)) if row else None
    
    cur.close()
    conn.close()
    return contrato

def insertar_contrato(datos):
    """Guarda un nuevo contrato comercial en la base de datos"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        INSERT INTO contratos (
            numero_contrato, numero_catastro, titular_contrato, ci_titular, 
            categoria, subcategoria, medidor_iot, fecha_contrato, 
            diametro_conexion, tipo_servicio, estado_contrato
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cur.execute(query, (
        datos.get('numero_contrato'), datos.get('numero_catastro'), datos.get('titular_contrato'),
        datos.get('ci_titular'), datos.get('categoria'), datos.get('subcategoria'),
        datos.get('medidor_iot') or None, datos.get('fecha_contrato') or None,
        datos.get('diametro_conexion'), datos.get('tipo_servicio'), datos.get('estado_contrato')
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def actualizar_contrato(numero_contrato, datos):
    """Modifica los campos del contrato seleccionado"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        UPDATE contratos SET 
            numero_catastro=%s, titular_contrato=%s, ci_titular=%s, categoria=%s, 
            subcategoria=%s, medidor_iot=%s, fecha_contrato=%s, diametro_conexion=%s, 
            tipo_servicio=%s, estado_contrato=%s
        WHERE numero_contrato=%s;
    """
    cur.execute(query, (
        datos.get('numero_catastro'), datos.get('titular_contrato'), datos.get('ci_titular'),
        datos.get('categoria'), datos.get('subcategoria'), datos.get('medidor_iot') or None,
        datos.get('fecha_contrato') or None, datos.get('diametro_conexion'),
        datos.get('tipo_servicio'), datos.get('estado_contrato'), numero_contrato
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def eliminar_contrato_db(numero_contrato):
    """Elimina definitivamente un registro de contrato de la base de datos"""
    conn = get_connection()
    cur = conn.cursor()
    
    query = "DELETE FROM contratos WHERE numero_contrato = %s;"
    cur.execute(query, (numero_contrato,))
    
    conn.commit()
    cur.close()
    conn.close()