let currentWeekStartDate = new Date();
currentWeekStartDate.setDate(currentWeekStartDate.getDate() - (currentWeekStartDate.getDay() + 6) % 7); // Establece el inicio de la semana (Lunes)

function generateWeekView() {
    const monthYearElement = document.getElementById("monthYear");
    const calendarBody = document.getElementById("calendar-body");

    // Limpiar el calendario actual
    calendarBody.innerHTML = '';

    const startOfWeek = new Date(currentWeekStartDate);
    const endOfWeek = new Date(currentWeekStartDate);
    endOfWeek.setDate(startOfWeek.getDate() + 6); // Fin de la semana

    // Actualizar el encabezado con el rango de fechas (en formato DD/MM/YYYY)
    monthYearElement.innerText = `${startOfWeek.getDate().toString().padStart(2, '0')}/${(startOfWeek.getMonth() + 1).toString().padStart(2, '0')}/${startOfWeek.getFullYear()} - ${endOfWeek.getDate().toString().padStart(2, '0')}/${(endOfWeek.getMonth() + 1).toString().padStart(2, '0')}/${endOfWeek.getFullYear()}`;

    // Bucle a través de las horas de 8:00 a 17:00
    for (let hour = 8; hour <= 17; hour++) {
        const row = document.createElement('tr');
        row.innerHTML = `<td class="hora">${hour}:00</td>`;

        // Bucle a través de los días de la semana
        for (let day = 0; day < 7; day++) {
            const currentDate = new Date(startOfWeek);
            currentDate.setDate(startOfWeek.getDate() + day);
            const formattedDate = currentDate.toISOString().split('T')[0]; // Formato YYYY-MM-DD

            // Agrega una celda clicable
            row.innerHTML += `<td class="dia" onclick="mostrarPopupSem(${day}, '${hour}:00', '${formattedDate}')"></td>`;
        }

        calendarBody.appendChild(row);
    }
}

function cambiarSemana(direccion) {
    // Cambio entre semanas
    currentWeekStartDate.setDate(currentWeekStartDate.getDate() + (direccion * 7));
    generateWeekView();
}

// Función para ir al día actual
function irAHoy() {
    // Obtener la fecha actual
    const hoy = new Date();
    // Establecer el inicio de la semana al lunes de esta semana
    hoy.setDate(hoy.getDate() - (hoy.getDay() + 6) % 7);
    currentWeekStartDate = hoy;
    generateWeekView();
}

function mostrarPopupSem(dia, hora, fecha) {
    document.getElementById("hora").value = hora;
    document.getElementById("fecha").value = fecha;
    document.getElementById("overlay").style.display = "block"; // Mostrar el overlay
    document.getElementById("popupSem").style.display = "block"; // Mostrar el popup
}

function cerrarPopupSem() {
    document.getElementById("overlay").style.display = "none"; // Ocultar el overlay
    document.getElementById("popupSem").style.display = "none"; // Ocultar el popup
}

// Inicializar el calendario al cargar la página
window.onload = function() {
    generateWeekView();
    
    // Añadir evento al botón "Hoy"
    document.getElementById("today").addEventListener("click", irAHoy);
};