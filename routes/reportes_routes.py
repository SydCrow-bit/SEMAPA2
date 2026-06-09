from flask import Blueprint, abort, render_template, send_file

from services.pdf_service import (
    generar_consumo_zonas_pdf,
    generar_contrato_pdf,
    generar_resumen_general_pdf,
)


reportes_bp = Blueprint("reportes", __name__)


@reportes_bp.route("/reportes")
def index_reportes():
    return render_template("reportes/index.html")


@reportes_bp.route("/reportes/pdf/resumen")
def descargar_resumen_general():
    archivo = generar_resumen_general_pdf()
    return send_file(
        archivo,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="reporte_general_semapa.pdf",
    )


@reportes_bp.route("/reportes/pdf/contrato/<string:numero_contrato>")
def descargar_ficha_contrato(numero_contrato):
    archivo = generar_contrato_pdf(numero_contrato)
    if archivo is None:
        abort(404, description="Contrato no encontrado")

    return send_file(
        archivo,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"contrato_{numero_contrato}.pdf",
    )


@reportes_bp.route("/reportes/pdf/consumo-zonas")
def descargar_consumo_zonas():
    archivo = generar_consumo_zonas_pdf()
    return send_file(
        archivo,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="consumo_por_zona.pdf",
    )
