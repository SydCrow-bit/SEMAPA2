/**
 * SEMAPA IoT - Dashboard Logic Final
 * Optimizado para ~17,000 registros con filtros de Servicio, Ubicación y Fecha.
 */

let map;
let capaPuntos;
let puntosOriginales = [];

document.addEventListener('DOMContentLoaded', function() {
    // 1. Inicialización de Fecha Actual en Cabecera
    const fechaElement = document.getElementById('fecha-actual');
    if (fechaElement) {
        fechaElement.innerText = new Date().toLocaleDateString('es-BO', { 
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
        });
    }

    // 2. Configuración Inicial del Mapa
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    try {
        // Extraer datos inyectados desde el backend (dataset de HTML)
        puntosOriginales = JSON.parse(mapElement.dataset.puntos);
        const consumoData = JSON.parse(mapElement.dataset.consumo);

        // Inicializar mapa usando preferCanvas para alto rendimiento
        map = L.map('map', { 
            preferCanvas: true,
            zoomControl: false 
        }).setView([-17.3935, -66.1570], 13);
        
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; SEMAPA IoT'
        }).addTo(map);

        capaPuntos = L.layerGroup().addTo(map);

        /**
         * 3. Función de Renderizado con Feedback de Carga
         */
        function renderizarPuntos(lista, esBusqueda = false) {
            const loadingOverlay = document.getElementById('map-loading-overlay');
            const contador = document.getElementById('contador-resultados');
            const aviso = document.getElementById('resultado-busqueda-info');

            // Mostrar estado de carga
            if (loadingOverlay) {
                loadingOverlay.classList.remove('d-none');
                loadingOverlay.classList.add('d-flex');
            }

            // Pequeño delay para permitir que el navegador procese el DOM del spinner
            setTimeout(() => {
                capaPuntos.clearLayers();
                
                // Actualizar banner de resultados
                if (esBusqueda || lista.length !== puntosOriginales.length) {
                    aviso.classList.remove('d-none');
                    if (contador) contador.innerText = lista.length.toLocaleString();
                } else {
                    aviso.classList.add('d-none');
                }

                if (lista.length === 0) {
                    finalizarEstadoCarga();
                    return;
                }

                // OPTIMIZACIÓN: Límites visuales para fluidez
                const limiteVisual = esBusqueda ? 5000 : 2000;
                const listaReducida = lista.length > limiteVisual ? lista.slice(0, limiteVisual) : lista;
                const bounds = [];

                listaReducida.forEach(p => {
                    if (!p.lat || !p.lng) return;
                    const posicion = [p.lat, p.lng];
                    bounds.push(posicion);

                    // Color dinámico según tipo de servicio
                    const colorPunto = p.servicio === 'Agua Industrial' ? '#e74c3c' : (esBusqueda ? "#3498db" : "#fd7e14");

                    L.circleMarker(posicion, {
                        radius: esBusqueda ? 6 : 4,
                        fillColor: colorPunto,
                        color: "#ffffff",
                        weight: 1,
                        fillOpacity: 0.8
                    }).addTo(capaPuntos).bindPopup(`
                        <div class="popup-container">
                            <strong class="popup-title">${p.nombre || 'SIN TITULAR'}</strong>
                            <div class="popup-data">
                                <b>Contrato:</b> ${p.numero_contrato}<br>
                                <b>Fecha:</b> ${p.fecha || 'No registrada'}<br>
                                <b>Distrito:</b> ${p.distrito}<br>
                                <b>Medidor:</b> <span class="badge bg-warning text-dark">${p.medidor || 'N/A'}</span><br>
                                <b>Servicio:</b> ${p.servicio}
                            </div>
                            <button class="btn-enviar-alerta btn btn-sm btn-primary w-100 mt-2" 
                                    data-contrato="${p.numero_contrato}" 
                                    data-titular="${p.nombre}">
                                <i class="fas fa-paper-plane me-1"></i> NOTIFICAR
                            </button>
                        </div>
                    `);
                });

                // Auto-zoom inteligente
                if (esBusqueda && bounds.length > 0) {
                    if (lista.length === 1) {
                        map.setView(bounds[0], 18);
                    } else {
                        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
                    }
                }

                finalizarEstadoCarga();
            }, 100); 
        }

        function finalizarEstadoCarga() {
            const loadingOverlay = document.getElementById('map-loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.classList.add('d-none');
                loadingOverlay.classList.remove('d-flex');
            }
            map.invalidateSize();
        }

        /**
         * 4. Lógica de Búsqueda y Filtrado (Cascada)
         */
        const ejecutarBusqueda = () => {
            const txt = document.getElementById('buscador-input').value.toLowerCase().trim();
            const serv = document.getElementById('filtro-servicio').value;
            const ubi = document.getElementById('filtro-ubicacion').value;
            const fechaFiltro = document.getElementById('filtro-fecha').value;

            let filtrados = puntosOriginales;

            // 1. Filtro por Ubicación (Distritos)
            if (ubi !== 'todos') {
                filtrados = filtrados.filter(p => p.distrito === ubi);
            }

            // 2. Filtro por Tipo de Servicio
            if (serv !== 'todos') {
                filtrados = filtrados.filter(p => p.servicio === serv);
            }

            // 3. Filtro por Fecha de Contrato
            if (fechaFiltro !== '') {
                filtrados = filtrados.filter(p => p.fecha === fechaFiltro);
            }

            // 4. Filtro por Texto (Contrato, Nombre o Medidor) - CORREGIDO INSENSITIVO A MAYÚSCULAS
            if (txt !== '') {
                filtrados = filtrados.filter(p => {
                    const contratoTexto = p.numero_contrato ? p.numero_contrato.toString().toLowerCase() : '';
                    const nombreTexto = p.nombre ? p.nombre.toLowerCase() : '';
                    const medidorTexto = p.medidor ? p.medidor.toString().toLowerCase() : '';

                    return contratoTexto.includes(txt) || 
                           nombreTexto.includes(txt) || 
                           medidorTexto.includes(txt);
                });
            }

            const huboCambio = (txt !== '' || ubi !== 'todos' || serv !== 'todos' || fechaFiltro !== '');
            renderizarPuntos(filtrados, huboCambio);
        };

        // Eventos de interacción
        document.getElementById('btn-buscar').addEventListener('click', ejecutarBusqueda);
        document.getElementById('buscador-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') ejecutarBusqueda();
        });

        // Filtros automáticos
        document.getElementById('filtro-servicio').addEventListener('change', ejecutarBusqueda);
        document.getElementById('filtro-ubicacion').addEventListener('change', ejecutarBusqueda);
        document.getElementById('filtro-fecha').addEventListener('change', ejecutarBusqueda);

        /**
         * 5. Gestión de Notificaciones y Cierre de Avisos
         */
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn-enviar-alerta');
            if (btn) {
                const { contrato, titular } = btn.dataset;
                console.log(`Enviando notificación a ${titular} (Contrato: ${contrato})`);
                alert(`Sistema SEMAPA:\nNotificación preparada para: ${titular}\nID Contrato: ${contrato}`);
            }
            
            if (e.target.closest('#cerrar-aviso-busqueda')) {
                document.getElementById('resultado-busqueda-info').classList.add('d-none');
            }
        });

        /**
         * 6. Gráfico de Consumo (Chart.js)
         */
        const ctx = document.getElementById('chartZonas');
        if (ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: consumoData.map(i => i.zona),
                    datasets: [{
                        label: 'Consumo m³',
                        data: consumoData.map(i => i.consumo),
                        backgroundColor: '#4e73df',
                        hoverBackgroundColor: '#2e59d9',
                        borderRadius: 5
                    }]
                },
                options: { 
                    indexAxis: 'y', 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        tooltip: { backgroundColor: '#333' }
                    },
                    scales: {
                        x: { grid: { display: false } },
                        y: { grid: { color: '#f8f9fc' } }
                    }
                }
            });
        }

        // 7. Botón de Reset (Limpiar Filtros)
        document.getElementById('btn-limpiar').addEventListener('click', () => {
            document.getElementById('buscador-input').value = '';
            document.getElementById('filtro-servicio').value = 'todos';
            document.getElementById('filtro-ubicacion').value = 'todos';
            document.getElementById('filtro-fecha').value = '';
            
            renderizarPuntos(puntosOriginales, false);
            map.setView([-17.3935, -66.1570], 13);
        });

        // Carga inicial
        renderizarPuntos(puntosOriginales, false);

    } catch (err) {
        console.error("Error crítico en el Dashboard JS:", err);
    }
});