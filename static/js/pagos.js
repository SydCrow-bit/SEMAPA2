/**
 * SEMAPA - Módulo de Liquidación Express y Control de Pagos IoT
 * Maneja la lógica asíncrona para calcular deudas basadas en el tarifario SQL
 * utilizando el Número de Contrato único como clave de consulta.
 */
document.addEventListener("DOMContentLoaded", function() {
    const btnCalcular = document.getElementById('btnCalcularAlcaldia');
    const inputCriterio = document.getElementById('txtCriterioAlcaldia');
    const panel = document.getElementById('panelResultadoAlcaldia');

    // Validar si los elementos existen en la vista actual antes de colgar los listeners
    if (!btnCalcular || !inputCriterio || !panel) return;

    // Captura el evento Enter en la barra de entrada de texto
    inputCriterio.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            btnCalcular.click();
        }
    });

    // Manejador del click para procesar el cálculo con la API del Backend
    btnCalcular.addEventListener('click', function() {
        const contratoVal = inputCriterio.value.trim();
        
        // Validación para exigir específicamente el Número de Contrato
        if (!contratoVal) {
            alert('Por favor, introduzca un número de contrato oficial válido (Ej: CT-00000001).');
            return;
        }

        // Petición asíncrona enviando el código de contrato al endpoint
        fetch(`/api/deuda-alcaldia?q=${encodeURIComponent(contratoVal)}`)
            .then(response => response.json())
            .then(res => {
                if (!res.error) {
                    // Inyección de variables calculadas dinámicamente por SQL
                    document.getElementById('resTitular').innerText = res.data.titular;
                    document.getElementById('resConsumo').innerText = res.data.consumo;
                    document.getElementById('resSubcat').innerText = `Tarifa Oficial: ${res.data.subcategoria}`;
                    document.getElementById('resMonto').innerText = Number(res.data.monto_bs).toFixed(2);
                    
                    // Sistema de Indicadores Visuales en base al saldo calculado
                    const wrapperEstado = document.getElementById('wrapperEstado');
                    if (res.data.monto_bs > 0) {
                        wrapperEstado.innerHTML = `
                            <span class="badge bg-danger-subtle text-danger border border-danger border-opacity-25 rounded-pill px-3 py-1.5 fw-bold shadow-sm animate-pulse">
                                <i class="fas fa-exclamation-triangle me-1"></i> Cuenta con Deuda
                            </span>
                            <span class="text-muted d-block small mt-1">Pendiente de pago</span>
                        `;
                    } else {
                        wrapperEstado.innerHTML = `
                            <span class="badge bg-success-subtle text-success border border-success border-opacity-25 rounded-pill px-3 py-1.5 fw-bold shadow-sm">
                                <i class="fas fa-check-circle me-1"></i> Saldo al Día
                            </span>
                            <span class="text-muted d-block small mt-1">Sin cobros pendientes</span>
                        `;
                    }

                    // Revelar el panel de resultados y hacer scroll suave hacia él
                    panel.classList.remove('d-none');
                    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    // Muestra el mensaje de error controlado enviado por Flask (ej: Contrato no encontrado)
                    alert(res.msg);
                    panel.classList.add('d-none');
                }
            })
            .catch(err => {
                console.error("Error en liquidación por API:", err);
                alert("No se pudo conectar con el servicio de tarifas SQL de la alcaldía.");
            });
    });
});