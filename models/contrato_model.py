from database import get_connection

# FUNCION 1: Búsqueda general (CORREGIDA para forzar coincidencia de texto en número_contrato)
def buscar_contrato_especifico(query):
    conn = get_connection()
    cur = conn.cursor() 
    
    # Usamos CAST(c.numero_contrato AS TEXT) o c.numero_contrato::text 
    # para asegurar que el formato 'CT-000000XX' sea perfectamente comparable con LIKE
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

# FUNCION 2: Filtro por Tipo de Servicio (Manteniendo consistencia)
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

# FUNCION 3: Nueva función para Rango de Fechas
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