let chartSesion;

// Función para obtener el gráfico de una sesión específica
const getOptionChartSesion = async(sesionId) => {
    try {
        const response = await fetch(`/obtener_grafico_sesion_paciente/${sesionId}/`);
        return await response.json();
    } catch (ex) {
        alert("Error al obtener los datos del gráfico: " + ex);
    }
};

// Función para inicializar el gráfico de la sesión en el modal
const initChartSesion = async(sesionId) => {
    const chartData = await getOptionChartSesion(sesionId);
    if (!chartData) return;

    // Inicializar el gráfico solo si hay datos válidos
    const chartContainer = document.getElementById("chart_sesion");
    if (!chartSesion) {
        chartSesion = echarts.init(chartContainer);
    }
    chartSesion.setOption(chartData.chart);
    chartSesion.resize();
};

// Función para mostrar el modal y cargar el gráfico
const enviarIdSesion = async(sesionId) => {
    const modal = document.getElementById("popupModal");
    modal.style.display = "block";  // Mostrar el modal

    // Inicializar el gráfico
    await initChartSesion(sesionId);
};

// Cerrar el modal cuando el usuario haga clic en "x"
document.querySelector(".close").onclick = () => {
    document.getElementById("popupModal").style.display = "none";
};

// Cerrar el modal cuando el usuario haga clic fuera de él
window.onclick = (event) => {
    const modal = document.getElementById("popupModal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

// Redimensionar el gráfico cuando la ventana cambie de tamaño
window.addEventListener('resize', () => {
    if (chartSesion) chartSesion.resize();
});
