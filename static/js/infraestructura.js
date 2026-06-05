/**
 * ==========================================================================
 * MONITOR DE INFRAESTRUCTURA IOT - SEMAPA (infraestructura.js)
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("=== [IoT SEMAPA] Módulo de Infraestructura de Red Inicializado ===");

    // 1. Renderizar la fecha técnica actual con formato institucional
    inicializarFechaTecnica();

    // 2. Escuchar cambios en las pestañas para auditoría de soporte
    inicializarControlTabs();

    // 3. Agregar efectos dinámicos de telemetría a las antenas activas
    inicializarEfectosHardware();
});

/**
 * Genera la estampa de tiempo operativa en el encabezado del panel
 */
function inicializarFechaTecnica() {
    const fechaTag = document.getElementById('fecha-actual');
    if (fechaTag) {
        const opciones = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const fechaFormateada = new Date().toLocaleDateString('es-ES', opciones);
        fechaTag.innerHTML = `<i class="far fa-clock me-1 text-danger"></i> Mantenimiento: ${fechaFormateada}`;
    }
}

/**
 * Controla y reporta en consola los cambios entre Radio Bases y Catálogo de Errores
 */
function inicializarControlTabs() {
    const tabElms = document.querySelectorAll('#infraestructuraTabs button[data-bs-toggle="tab"]');
    
    tabElms.forEach(tabElm => {
        tabElm.addEventListener('shown.bs.tab', (event) => {
            const targetPane = event.target.getAttribute('data-bs-target');
            console.log(`[Soporte Técnico] Cambiando vista activa a panel: ${targetPane}`);
            
            // Aquí podrás registrar métricas o recargar datos asíncronos en el futuro
        });
    });
}

/**
 * Añade un efecto dinámico de parpadeo a los íconos de antenas "En Línea" 
 * simulando la recepción de paquetes de datos de los medidores en Cochabamba
 */
function inicializarEfectosHardware() {
    const insigniasActivas = document.querySelectorAll('.table tbody tr .badge.bg-success-subtle');
    
    insigniasActivas.forEach(badge => {
        const icono = badge.querySelector('i');
        if (icono) {
            // Añadimos una animación suave de pulso usando CSS nativo mediante JS
            icono.style.transition = "opacity 0.6s ease-in-out";
            
            setInterval(() => {
                icono.style.opacity = icono.style.opacity === "0.3" ? "1" : "0.3";
            }, 1200);
        }
    });
}