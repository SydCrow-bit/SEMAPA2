from database import get_connection

def obtener_lecturas(medidor_query=None):
    conn = get_connection()
    cur = conn.cursor()
    
    # Filtro base para limpiar registros basura
    filtro_limpieza = "WHERE medidor_iot IS NOT NULL AND fechahoralectura IS NOT NULL"
    
    if medidor_query:
        # Búsqueda por medidor + Filtro de limpieza
        query = f"""
            SELECT id_lectura, medidor_iot, lecturaanterior, lecturaactual, 
                   fechahoralectura, radiobase, fecha_pago
            FROM lecturas
            {filtro_limpieza} AND medidor_iot ILIKE %s
            ORDER BY fechahoralectura DESC;
        """
        cur.execute(query, (f'%{medidor_query}%',))
    else:
        # Consulta por defecto: solo registros limpios y recientes
        query = f"""
            SELECT id_lectura, medidor_iot, lecturaanterior, lecturaactual, 
                   fechahoralectura, radiobase, fecha_pago
            FROM lecturas
            {filtro_limpieza}
            ORDER BY fechahoralectura DESC
            LIMIT 10;
        """
        cur.execute(query)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def insertar_lectura(medidor, lec_ant, lec_act, radiobase):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO lecturas (medidor_iot, lecturaanterior, lecturaactual, fechahoralectura, radiobase) 
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
    """, (medidor, lec_ant, lec_act, radiobase))
    conn.commit()
    cur.close()
    conn.close()

def eliminar_lectura(id_lectura):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM lecturas WHERE id_lectura = %s", (id_lectura,))
    conn.commit()
    cur.close()
    conn.close()