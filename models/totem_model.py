from database import get_connection


# =====================================
# CONSULTA POR NUMERO DE CONTRATO
# =====================================
def buscar_contrato_totem(numero_contrato):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                c.numero_contrato,
                c.titular_contrato,
                c.ci_titular,
                c.categoria,
                c.subcategoria,
                c.medidor_iot,
                c.estado_contrato,
                l.lecturaanterior,
                l.lecturaactual,
                l.fechahoralectura
            FROM contratos c
            JOIN lecturas l
                ON c.medidor_iot = l.medidor_iot
            WHERE c.numero_contrato = %s
            ORDER BY l.fechahoralectura DESC
            LIMIT 1
        """, (numero_contrato,))

        row = cur.fetchone()

        if not row:
            return None

        consumo = float(row[8]) - float(row[7])

        return {
            "contrato": row[0],
            "titular": row[1],
            "ci": row[2],
            "categoria": row[3],
            "subcategoria": row[4],
            "medidor": row[5],
            "estado": row[6],
            "lectura_anterior": row[7],
            "lectura_actual": row[8],
            "consumo": round(consumo, 2),
            "fecha": row[9].strftime("%d/%m/%Y %H:%M")
        }

    finally:
        cur.close()
        conn.close()


# =====================================
# HISTORIAL DE CONSUMO
# =====================================
def obtener_historial_consumo(medidor_iot):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                fechahoralectura,
                lecturaanterior,
                lecturaactual,
                (lecturaactual - lecturaanterior) AS consumo
            FROM lecturas
            WHERE medidor_iot = %s
            ORDER BY fechahoralectura DESC
            LIMIT 12
        """, (medidor_iot,))

        rows = cur.fetchall()

        historial = []

        for row in rows:

            historial.append({
                "fecha": row[0].strftime("%d/%m/%Y"),
                "lectura_anterior": row[1],
                "lectura_actual": row[2],
                "consumo": round(float(row[3]), 2)
            })

        return historial

    finally:
        cur.close()
        conn.close()


# =====================================
# BUSQUEDA POR MEDIDOR
# =====================================
def buscar_por_medidor(medidor):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                c.numero_contrato,
                c.titular_contrato,
                c.ci_titular,
                c.categoria,
                c.subcategoria,
                c.medidor_iot,
                c.estado_contrato,
                l.lecturaanterior,
                l.lecturaactual,
                l.fechahoralectura
            FROM contratos c
            JOIN lecturas l
                ON c.medidor_iot = l.medidor_iot
            WHERE c.medidor_iot = %s
            ORDER BY l.fechahoralectura DESC
            LIMIT 1
        """, (medidor,))

        row = cur.fetchone()

        if not row:
            return None

        consumo = float(row[8]) - float(row[7])

        return {
            "contrato": row[0],
            "titular": row[1],
            "ci": row[2],
            "categoria": row[3],
            "subcategoria": row[4],
            "medidor": row[5],
            "estado": row[6],
            "lectura_anterior": row[7],
            "lectura_actual": row[8],
            "consumo": round(consumo, 2),
            "fecha": row[9].strftime("%d/%m/%Y %H:%M")
        }

    finally:
        cur.close()
        conn.close()


# =====================================
# BUSQUEDA POR CI
# =====================================
def buscar_por_ci(ci):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                c.numero_contrato,
                c.titular_contrato,
                c.ci_titular,
                c.categoria,
                c.subcategoria,
                c.medidor_iot,
                c.estado_contrato,
                l.lecturaanterior,
                l.lecturaactual,
                l.fechahoralectura
            FROM contratos c
            JOIN lecturas l
                ON c.medidor_iot = l.medidor_iot
            WHERE c.ci_titular = %s
            ORDER BY l.fechahoralectura DESC
            LIMIT 1
        """, (ci,))

        row = cur.fetchone()

        if not row:
            return None

        consumo = float(row[8]) - float(row[7])

        return {
            "contrato": row[0],
            "titular": row[1],
            "ci": row[2],
            "categoria": row[3],
            "subcategoria": row[4],
            "medidor": row[5],
            "estado": row[6],
            "lectura_anterior": row[7],
            "lectura_actual": row[8],
            "consumo": round(consumo, 2),
            "fecha": row[9].strftime("%d/%m/%Y %H:%M")
        }

    finally:
        cur.close()
        conn.close()