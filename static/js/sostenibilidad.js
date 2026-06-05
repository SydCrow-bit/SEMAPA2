document.addEventListener("DOMContentLoaded", function() {
    // 1. Buscamos el contenedor que tiene guardados los datos desde el HTML
    const contenedorDatos = document.getElementById('datos-sostenibilidad-json');
    if (!contenedorDatos) return;

    // 2. Parseamos el JSON de forma segura
    const datosDistritos = JSON.parse(contenedorDatos.textContent);

    // Ordenamiento estratégico de mayor a menor consumo
    datosDistritos.sort((a, b) => b.litros - a.litros);

    const etiquetas = datosDistritos.map(item => item.distrito);
    const valores = datosDistritos.map(item => item.litros);
    
    // Mapeo cromático según tu escala de niveles
    const coloresBarras = valores.map(litros => {
        if (litros <= 180) return 'rgba(40, 167, 69, 0.75)';   // Verdes (Nivel 1-2)
        if (litros <= 250) return 'rgba(255, 193, 7, 0.85)';   // Amarillo (Nivel 3)
        if (litros <= 300) return 'rgba(253, 126, 20, 0.85)';  // Naranja (Nivel 4)
        return 'rgba(220, 53, 69, 0.85)';                      // Rojos (Nivel 5-6)
    });

    // 3. Renderizamos el gráfico con Chart.js
    const ctx = document.getElementById('graficoSostenibilidad').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Litros hídricos consumidos',
                data: valores,
                backgroundColor: coloresBarras,
                borderColor: coloresBarras.map(c => c.replace('0.75', '1').replace('0.85', '1')),
                borderWidth: 1.5,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Litros / Persona / Día',
                        font: { weight: 'bold' }
                    }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
});