from flask import Blueprint, render_template, request

from models.totem_model import (
    buscar_contrato_totem,
    obtener_historial_consumo,
    buscar_por_medidor,
    buscar_por_ci
)

totem_bp = Blueprint("totem", __name__)


# ======================================
# MENU PRINCIPAL
# ======================================
@totem_bp.route("/totem")
def inicio_totem():
    return render_template("totem/inicio.html")


# ======================================
# CONSULTA POR CONTRATO
# ======================================
@totem_bp.route("/totem/contrato")
def consulta_contrato():

    return render_template(
        "totem/consulta.html",
        resultado=None,
        historial=[],
        buscado=False
    )


# ======================================
# BUSCAR CONTRATO
# ======================================
@totem_bp.route("/totem/buscar", methods=["POST"])
def buscar():

    numero_contrato = request.form["numero_contrato"]

    resultado = buscar_contrato_totem(numero_contrato)

    historial = []

    if resultado:
        historial = obtener_historial_consumo(
            resultado["medidor"]
        )

    return render_template(
        "totem/consulta.html",
        resultado=resultado,
        historial=historial,
        buscado=True
    )


# ======================================
# CONSULTA POR MEDIDOR
# ======================================
@totem_bp.route("/totem/medidor")
def consulta_medidor():

    return render_template(
        "totem/medidor.html",
        resultado=None,
        historial=[],
        buscado=False
    )


# ======================================
# BUSCAR MEDIDOR
# ======================================
@totem_bp.route("/totem/buscar-medidor", methods=["POST"])
def buscar_medidor():

    medidor = request.form["valor_busqueda"]

    resultado = buscar_por_medidor(medidor)

    historial = []

    if resultado:
        historial = obtener_historial_consumo(
            resultado["medidor"]
        )

    return render_template(
        "totem/medidor.html",
        resultado=resultado,
        historial=historial,
        buscado=True
    )


# ======================================
# CONSULTA POR CI
# ======================================
@totem_bp.route("/totem/ci")
def consulta_ci():

    return render_template(
        "totem/ci.html",
        resultado=None,
        historial=[],
        buscado=False
    )


# ======================================
# BUSCAR CI
# ======================================
@totem_bp.route("/totem/buscar-ci", methods=["POST"])
def buscar_ci():

    ci = request.form["valor_busqueda"]

    resultado = buscar_por_ci(ci)

    historial = []

    if resultado:
        historial = obtener_historial_consumo(
            resultado["medidor"]
        )

    return render_template(
        "totem/ci.html",
        resultado=resultado,
        historial=historial,
        buscado=True
    )