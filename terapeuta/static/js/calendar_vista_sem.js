let currentWeekStartDate = new Date();
currentWeekStartDate.setDate(currentWeekStartDate.getDate() - (currentWeekStartDate.getDay() + 6) % 7); // Establece el inicio de la semana (Lunes)

function generateWeekView(citas) {
    const monthYearElement = document.getElementById("monthYear");
    const calendarBody = document.getElementById("calendar-body");

    // Crear un fragmento para el DOM
    const fragment = document.createDocumentFragment();

    const startOfWeek = new Date(currentWeekStartDate);
    const endOfWeek = new Date(currentWeekStartDate);
    endOfWeek.setDate(startOfWeek.getDate() + 6); // Fin de la semana

    // Actualizar el encabezado con el rango de fechas
    monthYearElement.innerText = `${startOfWeek.getDate().toString().padStart(2, '0')}/${(startOfWeek.getMonth() + 1).toString().padStart(2, '0')}/${startOfWeek.getFullYear()} - ${endOfWeek.getDate().toString().padStart(2, '0')}/${(endOfWeek.getMonth() + 1).toString().padStart(2, '0')}/${endOfWeek.getFullYear()}`;

    // Bucle a través de las horas de 8:00 a 17:00
    for (let hour = 8; hour <= 17; hour++) {
    const row = document.createElement('tr');
    const hourFormatted = hour.toString().padStart(2, '0'); // Asegura que la hora tenga dos dígitos
    row.innerHTML = `<td class="hora">${hourFormatted}:00</td>`;

    for (let day = 0; day < 7; day++) {
        const currentDate = new Date(startOfWeek);
        currentDate.setDate(startOfWeek.getDate() + day);

        currentDate.setHours(0, 0, 0, 0);
        const formattedDate = currentDate.toISOString().split('T')[0]; // Formato YYYY-MM-DD

        // Filtrar todas las citas del día
        const citasDia = citas.filter(cita => cita.fecha === formattedDate);
        const citaEncontrada = citasDia.find(cita => cita.hora === `${hourFormatted}:00`);

        if (citaEncontrada) {
            row.innerHTML += `<td class="dia" style="background-color: rgba(0, 140, 171, 0.5);" onclick="mostrarCitasDelDia(${JSON.stringify(citasDia)}, '${formattedDate}')"></td>`;
        } else {
            row.innerHTML += `<td class="dia" onclick="mostrarPopupSem(${day}, '${hourFormatted}:00', '${formattedDate}')"></td>`;
        }
    }

    fragment.appendChild(row);
}

    // Limpiar el calendario actual y agregar el fragmento
    calendarBody.innerHTML = '';
    calendarBody.appendChild(fragment);
}

// Función para mostrar el popup
function mostrarPopupSem(dia, hora, fecha) {
    // Solo muestra el popup si se hace clic en celdas disponibles
    document.getElementById("hora").value = hora;
    document.getElementById("fecha").value = fecha;
    document.getElementById("overlay").style.display = "block"; // Mostrar el overlay
    document.getElementById("popupSem").style.display = "block"; // Mostrar el popup
}

// Inicializar el calendario al cargar la página
window.onload = function() {
    // Obtener las citas desde el backend
    fetch("/obtener-fechas-citas/")
        .then(response => response.json())
        .then(data => {
            generateWeekView(data.citas); // Pasar las citas a la función
        });

    // Añadir evento al botón "Hoy"
    document.getElementById("today").addEventListener("click", irAHoy);
};

function mostrarCitasDelDia(citasDia, fecha) {
    const citasContainer = document.getElementById("citasContainer");
    const citasSemOverlay = document.getElementById("citasSemOverlay");
    const citasPopupSem = document.getElementById("citasPopupSem");

    // Limpiar el contenido previo del popup
    citasContainer.innerHTML = "";

    if (citasDia.length > 0) {
        citasDia.forEach(cita => {
            const citaElement = document.createElement('div');
            citaElement.classList.add('cita-item');
            citaElement.innerHTML = `
                <h3>${cita.titulo}</h3>
                <p>Hora: ${cita.hora}</p>
                <p>Paciente: ${cita.paciente}</p>
                <p>Sala: ${cita.sala}</p>
                <p>Tipo: ${cita.tipo_cita}</p>
                <p>Detalle: ${cita.detalle}</p>
            `;
            citasContainer.appendChild(citaElement);
        });
    } else {
        citasContainer.innerHTML = "<p>No hay citas para este día.</p>";
    }

    // Mostrar el popup
    citasSemOverlay.style.display = "block";
    citasPopupSem.style.display = "block";
}

// Función para cerrar el popup de citas
function cerrarCitasPopupSem() {
    document.getElementById("citasSemOverlay").style.display = "none";
    document.getElementById("citasPopupSem").style.display = "none";
}

// Función para ir al día actual
function irAHoy() {
    // Obtener la fecha actual
    const hoy = new Date();
    // Establecer el inicio de la semana al lunes de esta semana
    hoy.setDate(hoy.getDate() - (hoy.getDay() + 6) % 7);
    currentWeekStartDate = hoy;

    // Obtener las citas desde el backend y regenerar la vista
    fetch("/obtener-fechas-citas/")
        .then(response => response.json())
        .then(data => {
            generateWeekView(data.citas); // Pasar las citas a la función
        });
}

// Función para cambiar entre semanas
function cambiarSemana(direccion) {
    // Cambio entre semanas
    currentWeekStartDate.setDate(currentWeekStartDate.getDate() + (direccion * 7));

    // Obtener las citas desde el backend y regenerar la vista
    fetch("/obtener-fechas-citas/")
        .then(response => response.json())
        .then(data => {
            generateWeekView(data.citas); // Pasar las citas a la función
        });
}

// Función para mostrar el popup
function mostrarPopupSem(dia, hora, fecha) {
    document.getElementById("hora").value = hora;
    document.getElementById("fecha").value = fecha;
    document.getElementById("overlay").style.display = "block"; // Mostrar el overlay
    document.getElementById("popupSem").style.display = "block"; // Mostrar el popup
}

// Función para cerrar el popup
function cerrarPopupSem() {
    document.getElementById("overlay").style.display = "none"; // Ocultar el overlay
    document.getElementById("popupSem").style.display = "none"; // Ocultar el popup
}

// Inicializar el calendario al cargar la página
window.onload = function() {
    // Obtener las citas desde el backend
    fetch("/obtener-fechas-citas/")
        .then(response => response.json())
        .then(data => {
            generateWeekView(data.citas); // Pasar las citas a la función
        });

    // Añadir evento al botón "Hoy"
    document.getElementById("today").addEventListener("click", irAHoy);
};