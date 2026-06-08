function agregarValor(valor) {
    const input = document.getElementById("valor_busqueda");
    input.value += valor;
}

function borrarValor() {
    const input = document.getElementById("valor_busqueda");

    input.value = input.value.slice(0, -1);
}

function limpiarValor() {
    document.getElementById("valor_busqueda").value = "";
}