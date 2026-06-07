// Variable global para controlar si estamos creando o editando
let editMode = false;
let bootstrapModal;

document.addEventListener("DOMContentLoaded", () => {
    // Inicializar el modal de Bootstrap de forma segura
    const modalElement = document.getElementById('modalContrato');
    if (modalElement) {
        bootstrapModal = new bootstrap.Modal(modalElement);
    }

    // Calcular dinámicamente indicadores rápidos al cargar la vista
    calcularMedidoresIoT();

    // Filtro dinámico de búsqueda en tiempo real sobre la tabla
    const buscador = document.getElementById('tabla_buscar');
    if (buscador) {
        buscador.addEventListener('keyup', filtrarTabla);
    }
});

// Cuenta cuántos contratos tienen un medidor IoT asignado actualmente en la tabla
function calcularMedidoresIoT() {
    let count = 0;
    const filas = document.querySelectorAll('#tabla_cuerpo tr');
    
    filas.forEach(fila => {
        // Verifica si la celda de medidor IoT no está vacía o con texto de "No asignado"
        const celdaMedidor = fila.children[4]; // Quinta columna
        if (celdaMedidor && !celdaMedidor.innerText.includes("No asignado") && celdaMedidor.innerText.trim() !== "") {
            count++;
        }
    });
    
    const contadorBadge = document.getElementById('count_iot');
    if (contadorBadge) {
        contadorBadge.innerText = count;
    }
}

// Filtra las filas de la tabla según el texto ingresado
function filtrarTabla() {
    const valor = this.value.toLowerCase();
    const filas = document.querySelectorAll('#tabla_cuerpo tr');
    
    filas.forEach(f => {
        const texto = f.innerText.toLowerCase();
        f.style.display = texto.includes(valor) ? '' : 'none';
    });
}

// Prepara el formulario para un nuevo registro
function prepararCrear() {
    editMode = false;
    document.getElementById('modal_titulo').innerHTML = '<i class="fas fa-plus-circle me-2 text-info"></i>Nuevo Registro de Contrato';
    document.getElementById('form_contrato').reset();
    document.getElementById('m_contrato').disabled = false;
}

// Obtiene los datos de un contrato específico y abre el modal de edición
async function editarContrato(id) {
    editMode = true;
    document.getElementById('modal_titulo').innerHTML = '<i class="fas fa-edit me-2 text-warning"></i>Modificar Información del Contrato';
    document.getElementById('m_contrato').disabled = true;

    try {
        const res = await fetch(`/api/contratos/${id}`);
        const data = await res.json();
        
        if (data.status === 'success') {
            document.getElementById('m_contrato').value = data.contrato.numero_contrato;
            document.getElementById('m_catastro').value = data.contrato.numero_catastro || '';
            document.getElementById('m_titular').value = data.contrato.titular_contrato || '';
            document.getElementById('m_ci').value = data.contrato.ci_titular || '';
            document.getElementById('m_categoria').value = data.contrato.categoria || 'DOMESTICO';
            document.getElementById('m_subcategoria').value = data.contrato.subcategoria || '';
            document.getElementById('m_medidor').value = data.contrato.medidor_iot || '';
            document.getElementById('m_fecha').value = data.contrato.fecha_contrato || '';
            document.getElementById('m_diametro').value = data.contrato.diametro_conexion || '';
            document.getElementById('m_servicio').value = data.contrato.tipo_servicio || '';
            document.getElementById('m_estado').value = (data.contrato.estado_contrato || 'ACTIVO').toUpperCase();
            
            if (bootstrapModal) bootstrapModal.show();
        } else {
            alert("No se pudieron recuperar los detalles del contrato.");
        }
    } catch(e) { 
        console.error(e);
        alert("Error de red al consultar el contrato."); 
    }
}

// Envía el Payload al backend (Crear o Editar)
async function guardarContrato(e) {
    e.preventDefault();
    const id = document.getElementById('m_contrato').value.trim();
    
    const payload = {
        numero_catastro: document.getElementById('m_catastro').value.trim(),
        titular_contrato: document.getElementById('m_titular').value.trim(),
        ci_titular: document.getElementById('m_ci').value.trim(),
        categoria: document.getElementById('m_categoria').value,
        subcategoria: document.getElementById('m_subcategoria').value.trim(),
        medidor_iot: document.getElementById('m_medidor').value.trim(),
        fecha_contrato: document.getElementById('m_fecha').value,
        diametro_conexion: document.getElementById('m_diametro').value.trim(),
        tipo_servicio: document.getElementById('m_servicio').value.trim(),
        estado_contrato: document.getElementById('m_estado').value
    };

    const url = editMode ? `/api/contratos/editar/${id}` : '/api/contratos/crear';

    try {
        const respuesta = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const resData = await respuesta.json();
        
        if (resData.status === 'success') {
            if (bootstrapModal) bootstrapModal.hide();
            window.location.reload(); // Recarga la tabla de contratos
        } else { 
            alert(resData.message || "Operación fallida."); 
        }
    } catch(err) { 
        console.error(err);
        alert("Error al procesar el guardado."); 
    }
}

// Envía la petición DELETE al backend
async function eliminarContrato(id) {
    if (!confirm(`¿Está completamente seguro de eliminar el contrato comercial N° ${id}?`)) return;
    
    try {
        const res = await fetch(`/api/contratos/eliminar/${id}`, { method: 'DELETE' });
        const data = await res.json();
        
        if (data.status === 'success') {
            const fila = document.getElementById(`fila-${id}`);
            if (fila) fila.remove();
            // Actualizar contadores dinámicamente tras remover
            calcularMedidoresIoT();
        } else { 
            alert("No se pudo eliminar el registro desde el servidor."); 
        }
    } catch(e) { 
        console.error(e);
        alert("Error en comunicación de red."); 
    }
}