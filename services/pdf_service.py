from datetime import datetime
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from database import get_connection


def generar_resumen_general_pdf():
    datos = _obtener_resumen_general()
    buffer = BytesIO()
    doc, styles, story = _crear_documento(buffer, "Reporte General SEMAPA IoT")

    story.append(_titulo("Reporte General SEMAPA IoT", styles))
    story.append(_subtitulo("Resumen comercial, infraestructura y consumo", styles))
    story.append(Spacer(1, 0.35 * cm))

    cards = [
        ["Total contratos", _fmt_num(datos["total_contratos"])],
        ["Contratos activos", _fmt_num(datos["contratos_activos"])],
        ["Predios registrados", _fmt_num(datos["total_predios"])],
        ["Medidores IoT", _fmt_num(datos["total_medidores"])],
        ["Consumo acumulado m3", _fmt_decimal(datos["consumo_total"])],
        ["Radiobases", _fmt_num(datos["total_radiobases"])],
    ]
    story.append(_tabla_info(cards, [7 * cm, 7 * cm]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(_seccion("Contratos por categoria", styles))
    story.append(_tabla(
        [["Categoria", "Cantidad"]] + datos["contratos_por_categoria"],
        [10 * cm, 4 * cm],
    ))
    story.append(Spacer(1, 0.45 * cm))

    story.append(_seccion("Ultimas lecturas registradas", styles))
    story.append(_tabla(
        [["Medidor", "Lect. anterior", "Lect. actual", "Consumo", "Fecha"]] + datos["ultimas_lecturas"],
        [3 * cm, 3 * cm, 3 * cm, 2.5 * cm, 4 * cm],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_contrato_pdf(numero_contrato):
    datos = _obtener_ficha_contrato(numero_contrato)
    if not datos:
        return None

    buffer = BytesIO()
    doc, styles, story = _crear_documento(buffer, f"Ficha Contrato {numero_contrato}")

    contrato = datos["contrato"]
    ultima = datos["ultima_lectura"]
    story.append(_titulo("Ficha de Contrato y Medidor", styles))
    story.append(_subtitulo(f"Contrato: {contrato.get('numero_contrato')}", styles))
    story.append(Spacer(1, 0.35 * cm))

    story.append(_seccion("Datos del titular", styles))
    story.append(_tabla_info([
        ["Titular", contrato.get("titular_contrato")],
        ["CI / NIT", contrato.get("ci_titular")],
        ["Estado", contrato.get("estado_contrato")],
        ["Fecha contrato", _fmt_fecha(contrato.get("fecha_contrato"))],
    ]))
    story.append(Spacer(1, 0.35 * cm))

    story.append(_seccion("Contrato, servicio e infraestructura", styles))
    story.append(_tabla_info([
        ["Numero contrato", contrato.get("numero_contrato")],
        ["Numero catastro", contrato.get("numero_catastro")],
        ["Categoria", contrato.get("categoria")],
        ["Subcategoria", contrato.get("subcategoria")],
        ["Tipo servicio", contrato.get("tipo_servicio")],
        ["Diametro conexion", contrato.get("diametro_conexion")],
        ["Medidor IoT", contrato.get("medidor_iot")],
        ["Direccion", contrato.get("direccion")],
        ["Zona", contrato.get("zona")],
        ["Distrito", contrato.get("distrito")],
    ]))
    story.append(Spacer(1, 0.35 * cm))

    story.append(_seccion("Ultima lectura", styles))
    if ultima:
        story.append(_tabla_info([
            ["Lectura anterior", _fmt_decimal(ultima.get("lecturaanterior"))],
            ["Lectura actual", _fmt_decimal(ultima.get("lecturaactual"))],
            ["Consumo m3", _fmt_decimal(ultima.get("consumo"))],
            ["Fecha lectura", _fmt_fecha(ultima.get("fechahoralectura"), con_hora=True)],
            ["Radiobase", ultima.get("radiobase")],
            ["Fecha pago", _fmt_fecha(ultima.get("fecha_pago"), con_hora=True)],
        ]))
    else:
        story.append(Paragraph("No existen lecturas registradas para este medidor.", styles["BodyText"]))

    story.append(Spacer(1, 0.35 * cm))
    story.append(_seccion("Historial reciente", styles))
    story.append(_tabla(
        [["Fecha", "Lectura anterior", "Lectura actual", "Consumo m3", "Radiobase"]]
        + datos["historial"],
        [4 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_consumo_zonas_pdf():
    filas = _obtener_consumo_zonas()
    buffer = BytesIO()
    doc, styles, story = _crear_documento(buffer, "Consumo por zona", pagesize=landscape(A4))

    story.append(_titulo("Reporte de Consumo por Zona y Distrito", styles))
    story.append(_subtitulo("Top zonas con mayor consumo acumulado", styles))
    story.append(Spacer(1, 0.45 * cm))
    story.append(_tabla(
        [["Zona", "Distrito", "Contratos", "Consumo m3", "Promedio m3"]]
        + filas,
        [7 * cm, 4 * cm, 3 * cm, 4 * cm, 4 * cm],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def _obtener_resumen_general():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM contratos")
        total_contratos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM contratos WHERE UPPER(COALESCE(estado_contrato, '')) = 'ACTIVO'")
        contratos_activos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM infraestructura")
        total_predios = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT medidor_iot) FROM contratos WHERE medidor_iot IS NOT NULL")
        total_medidores = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM radiobases")
        total_radiobases = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(lecturaactual - lecturaanterior), 0) FROM lecturas")
        consumo_total = cur.fetchone()[0]

        cur.execute("""
            SELECT COALESCE(categoria, 'SIN CATEGORIA') AS categoria, COUNT(*)
            FROM contratos
            GROUP BY categoria
            ORDER BY COUNT(*) DESC, categoria ASC
            LIMIT 8
        """)
        contratos_por_categoria = [[r[0], _fmt_num(r[1])] for r in cur.fetchall()]

        cur.execute("""
            SELECT medidor_iot, lecturaanterior, lecturaactual,
                   (lecturaactual - lecturaanterior) AS consumo,
                   fechahoralectura
            FROM lecturas
            WHERE medidor_iot IS NOT NULL
            ORDER BY fechahoralectura DESC NULLS LAST
            LIMIT 10
        """)
        ultimas_lecturas = [
            [
                r[0],
                _fmt_decimal(r[1]),
                _fmt_decimal(r[2]),
                _fmt_decimal(r[3]),
                _fmt_fecha(r[4], con_hora=True),
            ]
            for r in cur.fetchall()
        ]

        return {
            "total_contratos": total_contratos,
            "contratos_activos": contratos_activos,
            "total_predios": total_predios,
            "total_medidores": total_medidores,
            "total_radiobases": total_radiobases,
            "consumo_total": consumo_total,
            "contratos_por_categoria": contratos_por_categoria,
            "ultimas_lecturas": ultimas_lecturas,
        }
    finally:
        cur.close()
        conn.close()


def _obtener_ficha_contrato(numero_contrato):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT c.numero_contrato, c.numero_catastro, c.titular_contrato,
                   c.ci_titular, c.categoria, c.subcategoria, c.medidor_iot,
                   c.fecha_contrato, c.estado_contrato, c.diametro_conexion,
                   c.tipo_servicio, i.direccion, i.zona, i.distrito,
                   i.manzano, i.lote, i.latitud, i.longitud
            FROM contratos c
            LEFT JOIN infraestructura i ON c.numero_catastro = i.numero_catastro
            WHERE c.numero_contrato = %s
            LIMIT 1
        """, (numero_contrato,))
        row = cur.fetchone()
        if not row:
            return None

        cols = [d[0] for d in cur.description]
        contrato = dict(zip(cols, row))

        ultima_lectura = None
        historial = []
        if contrato.get("medidor_iot"):
            cur.execute("""
                SELECT lecturaanterior, lecturaactual,
                       (lecturaactual - lecturaanterior) AS consumo,
                       fechahoralectura, radiobase, fecha_pago
                FROM lecturas
                WHERE medidor_iot = %s
                ORDER BY fechahoralectura DESC NULLS LAST
                LIMIT 12
            """, (contrato["medidor_iot"],))
            rows = cur.fetchall()
            if rows:
                lectura_cols = [d[0] for d in cur.description]
                ultima_lectura = dict(zip(lectura_cols, rows[0]))
                historial = [
                    [
                        _fmt_fecha(r[3], con_hora=True),
                        _fmt_decimal(r[0]),
                        _fmt_decimal(r[1]),
                        _fmt_decimal(r[2]),
                        r[4] or "N/A",
                    ]
                    for r in rows
                ]

        return {
            "contrato": contrato,
            "ultima_lectura": ultima_lectura,
            "historial": historial or [["Sin datos", "N/A", "N/A", "N/A", "N/A"]],
        }
    finally:
        cur.close()
        conn.close()


def _obtener_consumo_zonas():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COALESCE(i.zona, 'SIN ZONA') AS zona,
                   COALESCE(i.distrito, 'SIN DISTRITO') AS distrito,
                   COUNT(DISTINCT c.numero_contrato) AS contratos,
                   COALESCE(SUM(l.lecturaactual - l.lecturaanterior), 0) AS consumo,
                   COALESCE(AVG(l.lecturaactual - l.lecturaanterior), 0) AS promedio
            FROM infraestructura i
            JOIN contratos c ON i.numero_catastro = c.numero_catastro
            LEFT JOIN lecturas l ON c.medidor_iot = l.medidor_iot
            GROUP BY i.zona, i.distrito
            ORDER BY consumo DESC
            LIMIT 30
        """)
        return [
            [r[0], r[1], _fmt_num(r[2]), _fmt_decimal(r[3]), _fmt_decimal(r[4])]
            for r in cur.fetchall()
        ]
    finally:
        cur.close()
        conn.close()


def _crear_documento(buffer, titulo, pagesize=A4):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
        title=titulo,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TituloSemapa",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f3d5e"),
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SubtituloSemapa",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#52616b"),
        alignment=TA_CENTER,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SeccionSemapa",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#16324f"),
        spaceBefore=4,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="RightSmall",
        parent=styles["Normal"],
        fontSize=8,
        alignment=TA_RIGHT,
    ))
    story = [Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["RightSmall"])]
    return doc, styles, story


def _titulo(texto, styles):
    return Paragraph(texto, styles["TituloSemapa"])


def _subtitulo(texto, styles):
    return Paragraph(texto, styles["SubtituloSemapa"])


def _seccion(texto, styles):
    return Paragraph(texto, styles["SeccionSemapa"])


def _tabla_info(filas, col_widths=None):
    if col_widths is None:
        col_widths = [5 * cm, 11 * cm]
    return _tabla([[_limpiar(k), _limpiar(v)] for k, v in filas], col_widths, header=False)


def _tabla(filas, col_widths, header=True):
    data = [[_limpiar(celda) for celda in fila] for fila in filas]
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d9e2ec")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3d5e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    else:
        style.extend([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef6fb")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#16324f")),
        ])
    table.setStyle(TableStyle(style))
    return table


def _fmt_decimal(valor):
    if valor is None:
        return "0.00"
    if isinstance(valor, Decimal):
        valor = float(valor)
    return f"{float(valor):,.2f}"


def _fmt_num(valor):
    return f"{int(valor or 0):,}"


def _fmt_fecha(valor, con_hora=False):
    if not valor:
        return "N/A"
    formato = "%d/%m/%Y %H:%M" if con_hora else "%d/%m/%Y"
    try:
        return valor.strftime(formato)
    except AttributeError:
        return str(valor)


def _limpiar(valor):
    if valor is None or valor == "":
        return "N/A"
    return str(valor)
