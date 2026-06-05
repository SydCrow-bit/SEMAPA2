from database import get_connection

def obtener_usuario_por_username(username):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM usuarios
        WHERE username = %s
    """, (username,))

    usuario = cur.fetchone()

    cur.close()
    conn.close()

    return usuario