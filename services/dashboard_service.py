from database import get_connection
from decimal import Decimal

def obtener_estadisticas_generales():
    """Obtiene los totales para las tarjetas superiores del dashboard."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Total Predios
        cur.execute("SELECT COUNT(*) FROM infraestructura")
        total_predios = cur.fetchone()[0]
        
        # 2. Total Contratos
        cur.execute("SELECT COUNT(*) FROM contratos")
        total_contratos = cur.fetchone()[0]
        
        # 3. Consumo Total Acumulado
        cur.execute("SELECT SUM(lecturaactual - lecturaanterior) FROM lecturas")
        res_consumo = cur.fetchone()[0]
        consumo_total = float(res_consumo) if res_consumo else 0.0

        return {
            "predios": total_predios,
            "contratos": total_contratos,
            "consumo": round(consumo_total, 2)
        }
    except Exception as e:
        print(f"Error en estadísticas: {e}")
        return {"predios": 0, "contratos": 0, "consumo": 0}
    finally:
        cur.close()
        conn.close()

def obtener_consumo_por_zona():
    """Datos para el gráfico de barras horizontales (Top 10 zonas)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = """
            SELECT i.zona, SUM(l.lecturaactual - l.lecturaanterior) as consumo
            FROM infraestructura i
            JOIN contratos c ON i.numero_catastro = c.numero_catastro
            JOIN lecturas l ON c.medidor_iot = l.medidor_iot
            WHERE i.zona IS NOT NULL
            GROUP BY i.zona
            ORDER BY consumo DESC
            LIMIT 10;
        """
        cur.execute(query)
        datos = cur.fetchall()
        return [{"zona": d[0], "consumo": float(d[1])} for d in datos]
    except Exception as e:
        print(f"Error en consumo por zona: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def obtener_puntos_mapa():
    """Trae los datos incluyendo distrito y ahora la fecha de contrato."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Agregamos c.fecha_contrato a la consulta SQL
        query = """
            SELECT 
                i.latitud, i.longitud, c.titular_contrato, c.numero_contrato, 
                c.medidor_iot, c.tipo_servicio, c.categoria, i.distrito,
                c.fecha_contrato
            FROM infraestructura i
            INNER JOIN contratos c ON i.numero_catastro = c.numero_catastro
            WHERE i.latitud IS NOT NULL
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        puntos = []
        for r in rows:
            # 2. Procesamos la fecha (índice 8) para que sea compatible con JSON y JS
            fecha_valor = r[8]
            fecha_str = ""
            if fecha_valor:
                try:
                    # Intentamos formatear si es objeto date/datetime
                    fecha_str = fecha_valor.strftime('%Y-%m-%d')
                except AttributeError:
                    fecha_str = str(fecha_valor)

            puntos.append({
                "lat": float(r[0]),
                "lng": float(r[1]),
                "nombre": r[2],
                "numero_contrato": r[3],
                "medidor": r[4],
                "servicio": r[5],
                "categoria": r[6] or "General",
                "distrito": r[7],
                "fecha": fecha_str if fecha_str else None
            })
        return puntos
    except Exception as e:
        print(f"Error en puntos mapa: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def obtener_consumo_per_capita():
    """Calcula el consumo de litros por persona al día para cada distrito."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        query = """
            SELECT 
                i.distrito, 
                SUM(l.lecturaactual - l.lecturaanterior) as total_m3,
                p.habitantes,
                (SUM(l.lecturaactual - l.lecturaanterior) * 1000.0 / NULLIF(p.habitantes, 0)) as litros_persona_dia
            FROM infraestructura i
            JOIN contratos c ON i.numero_catastro = c.numero_catastro
            JOIN lecturas l ON c.medidor_iot = l.medidor_iot
            JOIN poblacion_distrital p ON i.distrito = p.distrito
            GROUP BY i.distrito, p.habitantes
            ORDER BY litros_persona_dia DESC;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        resultados = []
        for r in rows:
            resultados.append({
                "distrito": r[0],
                "total_m3": float(r[1]) if r[1] else 0.0,
                "habitantes": r[2],
                "litros_persona_dia": float(r[3]) if r[3] else 0.0
            })
        return resultados
        
    except Exception as e:
        print(f"Error en obtener_consumo_per_capita: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def obtener_resumen_errores():
    """Trae los 9 errores técnicos del catálogo registrado en SEMAPA."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT id_error, descripcion_error 
        FROM catalogo_errores 
        ORDER BY id_error ASC;
    """
    try:
        cur.execute(query)
        rows = cur.fetchall()
        
        resultados = []
        for r in rows:
            resultados.append({
                "id_error": r[0],
                "descripcion_error": r[1]
            })
        return resultados
    except Exception as e:
        print(f"Error en obtener_resumen_errores: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def obtener_estado_radiobases():
    """Trae el listado de antenas concentradoras (radiobases)."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT radiobases 
        FROM radiobases
        ORDER BY radiobases ASC;
    """
    try:
        cur.execute(query)
        rows = cur.fetchall()
        
        resultados = []
        for r in rows:
            resultados.append({
                "id_antena": float(r[0]) if isinstance(r[0], Decimal) else r[0]
            })
            
        # PLAN DE RESPALDO: Si la tabla sigue vacía en la base de datos, 
        # inyectamos los datos por defecto para evitar pantallas en blanco.
        if len(resultados) == 0:
            resultados = [
                {"id_antena": 101.5},
                {"id_antena": 102.8},
                {"id_antena": 105.2}
            ]
        return resultados
    except Exception as e:
        print(f"Error en obtener_estado_radiobases: {e}")
        return [
            {"id_antena": 101.5},
            {"id_antena": 102.8},
            {"id_antena": 105.2}
        ]
    finally:
        cur.close()
        conn.close()

# =====================================================================
# NUEVA FUNCIÓN: FACTURACIÓN DINÁMICA MEDIANTE SQL REESTRUCTURADO
# =====================================================================
def obtener_deuda_alcaldia(num_contrato):
    """
    Busca un contrato por su Número de Contrato único, calcula el consumo real del medidor IoT 
    y computa la pre-facturación extrayendo los multiplicadores de la tabla tarifario.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Consulta optimizada que filtra rigurosamente por el número de contrato único
    query = """
        SELECT 
            c.titular_contrato,
            c.subcategoria,
            COALESCE(l.lecturaAnterior, 0) as lec_ant,
            COALESCE(l.lecturaActual, 0) as lec_act,
            t.cargo_fijo_usd,
            t.rango_13_25, t.rango_26_50, t.rango_51_75, 
            t.rango_76_100, t.rango_101_150, t.rango_mayor_151
        FROM contratos c
        LEFT JOIN lecturas l ON c.medidor_iot = l.medidor_iot
        INNER JOIN tarifario t ON c.subcategoria = t.subcategoria
        WHERE c.numero_contrato = %s
        LIMIT 1;
    """
    
    try:
        cur.execute(query, (num_contrato,))
        row = cur.fetchone()
        if not row:
            return None
            
        # Desestructuración de la base de datos
        titular, subcat, lec_ant, lec_act, cargo_fijo, r1, r2, r3, r4, r5, r6 = row
        
        # 1. Cálculo del consumo bruto mensual
        consumo = float(lec_act) - float(lec_ant)
        if consumo < 0: 
            consumo = 0.0
        
        # 2. Inicializamos el acumulador monetario con el Cargo Fijo Base ($us)
        monto_usd = float(cargo_fijo)
        
        # 3. Aplicación del álgebra de rangos escalonados si excede el mínimo de 12 m3/mes
        if consumo > 12:
            excedente = consumo - 12
            
            # Mapeo ordenado de topes de bloques y tarifas por m3
            bloques = [
                (25, float(r1)),          # Bloque de 13 a 25 m3
                (50, float(r2)),          # Bloque de 26 a 50 m3
                (75, float(r3)),          # Bloque de 51 a 75 m3
                (100, float(r4)),         # Bloque de 76 a 100 m3
                (150, float(r5)),         # Bloque de 101 a 150 m3
                (float('inf'), float(r6)) # Bloque superior a 151 m3
            ]
            
            limite_anterior = 12
            for limite_superior, precio_m3 in bloques:
                if consumo <= limite_superior:
                    # Multiplica el remanente real del excedente por el precio del bloque actual
                    monto_usd += excedente * precio_m3
                    break
                else:
                    # Si cubre todo el bloque completo, calcula su capacidad máxima
                    capacidad_bloque = limite_superior - limite_anterior
                    monto_usd += capacidad_bloque * precio_m3
                    excedente -= capacidad_bloque
                    limite_anterior = limite_superior

        # 4. Conversión oficial al tipo de cambio de Bolivia (6.96)
        TIPO_CAMBIO = 6.96
        monto_bs = monto_usd * TIPO_CAMBIO
        
        return {
            "titular": titular,
            "consumo": round(consumo, 2),
            "subcategoria": subcat,
            "monto_bs": round(monto_bs, 2)
        }
    except Exception as e:
        print(f"Error crítico en el cálculo de deuda SQL: {e}")
        return None
    finally:
        cur.close()
        conn.close()