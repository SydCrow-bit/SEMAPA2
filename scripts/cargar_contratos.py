import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from flask import Blueprint, request, jsonify, render_template_string
from database import get_connection 

cargar_bp = Blueprint("cargar", __name__)

@cargar_bp.route("/importar-contratos", methods=['GET', 'POST'])
def importar_contratos():
    # VISTA PARA EL NAVEGADOR
    if request.method == 'GET':
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>SEMAPA - Carga de Datos</title>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 50px; background-color: #f4f4f9; }
                    .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
                    h2 { color: #2c3e50; }
                    input[type="file"] { margin: 20px 0; }
                    button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
                    button:hover { background: #2980b9; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Cargar Excel de Contratos</h2>
                    <p>Asegúrese de que el archivo contenga las columnas exactas de la tabla.</p>
                    <form method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".xlsx, .xls, .csv" required>
                        <br>
                        <button type="submit">Iniciar Carga Masiva</button>
                    </form>
                </div>
            </body>
            </html>
        ''')

    # LÓGICA DE CARGA (POST)
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No seleccionaste ningún archivo"}), 400

    try:
        # 1. Leer el archivo (Soporta Excel y CSV)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # 2. CORRECCIÓN DE FECHAS (Aquí se soluciona tu error)
        # Convertimos la columna a un formato que PostgreSQL entienda (YYYY-MM-DD)
        if 'fecha_contrato' in df.columns:
            df['fecha_contrato'] = pd.to_datetime(df['fecha_contrato'], errors='coerce')

        # 3. Limpieza general: Convertir celdas vacías (NaN) a None (NULL en SQL)
        df = df.where(pd.notnull(df), None)

        # 4. Columnas que coinciden con tu nueva tabla plana
        columnas_db = [
            'numero_contrato', 'numero_catastro', 'titular_contrato', 
            'ci_titular', 'categoria', 'subcategoria', 'medidor_iot', 
            'fecha_contrato', 'estado_contrato', 'diametro_conexion', 'tipo_servicio'
        ]
        
        # Verificar que el Excel tenga lo necesario
        faltantes = [c for c in columnas_db if c not in df.columns]
        if faltantes:
            return jsonify({"error": f"Faltan columnas en el archivo: {faltantes}"}), 400

        # 5. Preparar los datos para la inserción
        valores = [tuple(fila) for fila in df[columnas_db].values]

        # 6. Conexión e Inserción
        conn = get_connection()
        cur = conn.cursor()
        
        # Usamos ON CONFLICT para que si el numero_contrato ya existe, no de error y solo ignore la fila
        query = f"""
            INSERT INTO contratos ({', '.join(columnas_db)}) 
            VALUES %s 
            ON CONFLICT (numero_contrato) DO NOTHING
        """
        
        execute_values(cur, query, valores)
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "mensaje": f"Proceso finalizado. Se intentaron cargar {len(valores)} registros."
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "detalle": str(e)
        }), 500

@cargar_bp.route("/importar-infraestructura", methods=['GET', 'POST'])
def importar_infraestructura():
    if request.method == 'GET':
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head><title>SEMAPA - Infraestructura</title></head>
            <body style="font-family: sans-serif; margin: 50px; background-color: #f4f4f9;">
                <div style="background: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: auto;">
                    <h2>Cargar Excel de Infraestructura (Catastro)</h2>
                    <form method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".xlsx, .xls, .csv" required>
                        <br><br>
                        <button type="submit" style="background: #27ae60; color: white; border: none; padding: 10px 20px; cursor: pointer;">Cargar Datos Geográficos</button>
                    </form>
                </div>
            </body>
            </html>
        ''')

    if 'file' not in request.files:
        return jsonify({"error": "No hay archivo"}), 400
    
    file = request.files['file']

    try:
        # 1. Leer el archivo con manejo de codificación para evitar errores de caracteres especiales
        if file.filename.endswith('.csv'):
            try:
                # Intentamos primero con utf-8
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                # Si falla (error 0xd1), usamos 'latin-1' que soporta la Ñ y tildes de Excel
                file.seek(0) # Reiniciamos el puntero del archivo
                df = pd.read_csv(file, encoding='latin-1')
        else:
            # Los archivos .xlsx no suelen tener este problema de encoding
            df = pd.read_excel(file)
        
        # 2. Limpieza de datos numéricos (Coordenadas y áreas)
        # Convertimos a número y lo que no sea número lo pone como None
        columnas_numericas = ['superficie_terreno', 'area_construida', 'valor_catastral', 'impuesto_anual', 'latitud', 'longitud']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. Limpieza general de nulos
        df = df.where(pd.notnull(df), None)

        # 4. Columnas exactas de tu tabla 'infraestructura'
        columnas_db = [
            'numero_catastro', 'propietario', 'ci', 'direccion', 'zona', 
            'distrito', 'manzano', 'lote', 'superficie_terreno', 
            'area_construida', 'uso_suelo', 'matricula_ddrr', 
            'valor_catastral', 'impuesto_anual', 'latitud', 'longitud'
        ]
        
        # Verificar columnas
        faltantes = [c for c in columnas_db if c not in df.columns]
        if faltantes:
            return jsonify({"error": f"Faltan columnas: {faltantes}"}), 400

        # 5. Preparar valores
        valores = [tuple(fila) for fila in df[columnas_db].values]

        # 6. Inserción en la DB
        conn = get_connection()
        cur = conn.cursor()
        
        # ON CONFLICT para el numero_catastro (que es la PK)
        query = f"""
            INSERT INTO infraestructura ({', '.join(columnas_db)}) 
            VALUES %s 
            ON CONFLICT (numero_catastro) DO UPDATE SET
                propietario = EXCLUDED.propietario,
                direccion = EXCLUDED.direccion,
                latitud = EXCLUDED.latitud,
                longitud = EXCLUDED.longitud
        """
        
        execute_values(cur, query, valores)
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success", "mensaje": f"Se procesaron {len(valores)} predios correctamente."})

    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500

@cargar_bp.route("/importar-lecturas", methods=['GET', 'POST'])
def importar_lecturas():
    # 1. VISTA HTML PARA CARGA
    if request.method == 'GET':
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head><title>Carga de Lecturas IoT</title></head>
            <body style="font-family: sans-serif; padding: 50px;">
                <h2>Subir Archivo de Lecturas (Excel/CSV)</h2>
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".xlsx, .xls, .csv" required>
                    <button type="submit">Importar Datos</button>
                </form>
            </body>
            </html>
        ''')

    # 2. VALIDACIONES DE ARCHIVO
    if 'file' not in request.files:
        return jsonify({"error": "No se subió ningún archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Archivo no seleccionado"}), 400

    try:
        # 3. LECTURA SEGURA (Encoding)
        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin-1')
        else:
            df = pd.read_excel(file)

        # 4. VALIDACIÓN DE COLUMNAS (Lo que le faltaba)
        columnas_db = [
            'medidor_iot', 'lecturaAnterior', 'LecturaActual', 
            'fechaHoraLectura', 'radiobase', 'fecha_pago'
        ]
        
        faltantes = [col for col in columnas_db if col not in df.columns]
        if faltantes:
            return jsonify({"error": f"Faltan columnas en el archivo: {faltantes}"}), 400

        # 5. PROCESAMIENTO DE DATOS
        # Fechas: Convertir y arreglar NaT para PostgreSQL
        for col in ['fechaHoraLectura', 'fecha_pago']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        df = df.replace({pd.NaT: None})

        # Números: Asegurar valores válidos
        df['lecturaAnterior'] = pd.to_numeric(df['lecturaAnterior'], errors='coerce').fillna(0)
        df['LecturaActual'] = pd.to_numeric(df['LecturaActual'], errors='coerce').fillna(0)

        # Nulos generales
        df = df.where(pd.notnull(df), None)

        # 6. INSERCIÓN MASIVA
        valores = [tuple(fila) for fila in df[columnas_db].values]
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Tip: Si quieres evitar cargar exactamente lo mismo dos veces si re-suben el archivo, 
        # podrías añadir un ON CONFLICT aquí si tuvieras una llave única compuesta.
        query = f"INSERT INTO lecturas ({', '.join(columnas_db)}) VALUES %s"
        
        execute_values(cur, query, valores)
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "success", 
            "mensaje": f"Se cargaron {len(valores)} registros de lectura correctamente."
        })

    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500