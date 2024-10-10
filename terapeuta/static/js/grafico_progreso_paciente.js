// Variables globales para los gráficos
let chartAngulos;
let chartVelocidad;

const getOptionChart = async(paciente_id) => {
    try {
        const response = await fetch(`/obtener_grafico_progreso_paciente/${paciente_id}/`);
        const data = await response.json();

        // Verificar si la respuesta contiene un mensaje de error
        if (data.mensaje) {
            // Mostrar mensaje en lugar del gráfico
            document.getElementById("chart").innerHTML = `<div class="contenedor-mensaje"><p>${data.mensaje}</p></div>`;
            document.getElementById("chart_velocidad").innerHTML = `<div class="contenedor-mensaje"><p>${data.mensaje}</p></div>`;
            return null; // No continuar con la configuración del gráfico
        }

        return data; // Devolver la configuración de ambos gráficos
    } catch(ex) {
        alert(ex);
    }
};

const initCharts = async(paciente_id) => {
    const chartsData = await getOptionChart(paciente_id);
    
    if (!chartsData) return; // Si no hay datos, salir

    // Inicializar el gráfico de ángulos
    chartAngulos = echarts.init(document.getElementById("chart")); // Ahora es global
    chartAngulos.setOption(chartsData.chart);
    chartAngulos.resize();

    // Inicializar el gráfico de velocidad
    chartVelocidad = echarts.init(document.getElementById("chart_velocidad")); // Ahora es global
    chartVelocidad.setOption(chartsData.chart_velocidad);
    chartVelocidad.resize();
};

// Escuchar el redimensionamiento de la ventana para que ambos gráficos se ajusten
window.addEventListener('resize', function() {
    if (chartAngulos) chartAngulos.resize();  // Redimensiona el gráfico de ángulos
    if (chartVelocidad) chartVelocidad.resize(); // Redimensiona el gráfico de velocidad
});

window.addEventListener('load', async() => {
    const pacienteId = document.getElementById("chart").getAttribute("data-paciente-id");
    await initCharts(pacienteId);
});
