document.addEventListener('DOMContentLoaded', function () {
    const prevButton = document.getElementById('prev');
    const nextButton = document.getElementById('next');
    const todayButton = document.getElementById('today');
    const monthYearLabel = document.getElementById('month-year');
    const calendar = document.getElementById('calendar');
    const weekViewButton = document.getElementById('week-view');
    const monthViewButton = document.getElementById('month-view');
    const popup = document.getElementById('popup');
    const btnAgendar = document.getElementById('add');
    let currentDate = new Date();
    let currentView = 'month';  // 'month' o 'week'
    let citas = []; // Variable global para almacenar las citas

    // Función para actualizar la vista del calendario
    function updateCalendar() {
        if (currentView === 'month') {
            generateMonthView();
        } else {
            generateWeekView();
        }
        fetch('/obtener-fechas-citas/')
            .then(response => response.json())
            .then(data => {
                citas = data.citas;
                console.log(citas);  // Verifica las fechas y horas recibidas
                const fechasCitas = citas.map(cita => cita.fecha);  // Obtener solo las fechas de las citas
                // Llamar a la función que destaca los días con citas
                if (currentView === 'month') {
                    destacarDiasConCita(fechasCitas);  // Destacar los días en la vista mensual
                }
                else {
                    destacarHorasConCita(citas);  // Destacar las horas en la vista semanal
                }
            })
            .catch(error => console.error('Error al obtener las fechas de citas:', error));
    }

    // -------------------------- VISTA MENSUAL --------------------------
    function generateMonthView() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        // Actualizar el encabezado
        monthYearLabel.textContent = `${getMonthName(month)} ${year}`;

        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        const adjustedFirstDay = (firstDayOfMonth === 0) ? 6 : firstDayOfMonth - 1;
        let calendarHTML = '<div class="calendar-grid">';

        const dayNames = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
        dayNames.forEach((day, index) => {
            const className = index >= 5 ? 'day-name weekend' : 'day-name';
            calendarHTML += `<div class="${className}">${day}</div>`;
        });

        // Días vacíos antes del inicio del mes
        for (let i = 0; i < adjustedFirstDay; i++) {
            calendarHTML += `<div class="empty-day"></div>`;
        }

        // Días del mes
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = (day === new Date().getDate() && year === new Date().getFullYear() && month === new Date().getMonth());
            const className = isToday ? 'day today' : 'day';
            calendarHTML += `<div class="${className}" data-fecha="${day}/${month + 1}/${year}">${day}</div>`;
        }

        const totalCells = adjustedFirstDay + daysInMonth;
        const extraDays = 42 - totalCells;

        for (let i = 0; i < extraDays; i++) {
            calendarHTML += `<div class="empty-day"></div>`;
        }

        calendarHTML += '</div>';
        calendar.innerHTML = calendarHTML;

        // Añadir el evento de clic a cada día
        btnAgendar.addEventListener('click', function() {
            popup.style.display = "block";
        });
        document.querySelectorAll(".day").forEach(day => {
            day.addEventListener("click", function () {
                const selectedDate = this.getAttribute("data-fecha");
                document.getElementById("fechaSeleccionada").textContent = selectedDate;
                document.getElementById("fecha").value = selectedDate; // Asigna la fecha al campo de fecha del formulario
                // Obtener las citas del día seleccionado
                const citasDelDia = obtenerCitasPorFecha(selectedDate);
                if (citasDelDia.length > 0) {
                    mostrarPopupCitas(citasDelDia);  // Muestra el popup si hay citas
                } else {
                    popup.style.display = "block"; // Muestra el popup
                }
            });
        });
        // Evento para editar cita
        document.getElementById("popup-content").addEventListener("click", function (event) {
            if (event.target.classList.contains("cita-item")) {  
                const citaId = event.target.getAttribute("data-cita-id");
                const cita = citas.find(cita => cita.id === parseInt(citaId));
                if (cita) {
                    // Mostrar el popup para editar la cita
                    document.getElementById("popupEditarCita").classList.add("mostrar");
                    console.log("Popup para editar la cita mostrado");
                    // Rellenar los campos del formulario con los datos de la cita
                    document.getElementById("cita_id").value = cita.id;
                    document.getElementById("titulo").value = cita.titulo;
                    document.getElementById("paciente").value = cita.paciente.id;
                    document.getElementById("fecha").value = cita.fecha;
                    document.getElementById("hora").value = cita.hora;
                    document.getElementById("sala").value = cita.sala;
                    document.getElementById("detalle").value = cita.descripcion;
                }
            }
        });
        // Cerrar popup de edición
        document.getElementById("closePopupEditarCita").addEventListener("click", function () {
            document.getElementById("popupEditarCita").style.display = "none";
        });
    }

    //------------------------------------VISTA SEMANAL------------------------------------
    function generateWeekView() {
        const startOfWeek = getStartOfWeek(currentDate);
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(endOfWeek.getDate() + 6);

        const weekRange = `${formatDate(startOfWeek)} - ${formatDate(endOfWeek)}`;
        monthYearLabel.textContent = weekRange;

        let calendarHTML = `
            <div class="week-view-container">
                <table class="week-view">
                    <thead>
                        <tr>
                            <th>Hora</th>
                            <th>Lunes</th>
                            <th>Martes</th>
                            <th>Miércoles</th>
                            <th>Jueves</th>
                            <th>Viernes</th>
                            <th>Sábado</th>
                            <th>Domingo</th>
                        </tr>
                    </thead>
                    <tbody>`;

        // Genera las horas de 8:00 AM a 8:00 PM
        for (let hour = 8; hour <= 20; hour++) {
            calendarHTML += `<tr><td class="time-slot">${hour}:00</td>`;
            for (let day = 0; day < 7; day++) {
                calendarHTML += `<td class="week-hour" data-hour="${hour}:00" data-day="${day}"></td>`;
            }
            calendarHTML += '</tr>';
        }

        calendarHTML += '</tbody></table></div>';
        calendar.innerHTML = calendarHTML;

    }

    //------------------------------------FUNCIONES AUXILIARES------------------------------------
    function getStartOfWeek(date) {
        const dayOfWeek = date.getDay() === 0 ? 6 : date.getDay() - 1;
        const startOfWeek = new Date(date);
        startOfWeek.setDate(date.getDate() - dayOfWeek);
        return startOfWeek;
    }

    function formatDate(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    function getMonthName(monthIndex) {
        const monthNames = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        return monthNames[monthIndex];
    }

    //------------------------------------FUNCION DESTACAR CITAS------------------------------------
    function destacarDiasConCita(fechasCitas) {
        const diasDelCalendario = document.querySelectorAll('.day');
        diasDelCalendario.forEach(dia => {
            const fechaDia = dia.getAttribute('data-fecha');  // La fecha del día en formato "dd/mm/yyyy"
            // Convertir la fecha del calendario al formato "YYYY-MM-DD" para comparar con las fechas de las citas
            const [diaNum, mesNum, anio] = fechaDia.split('/');
            const fechaFormateada = `${anio}-${mesNum.padStart(2, '0')}-${diaNum.padStart(2, '0')}`;
            // Comparar la fecha formateada con las fechas de las citas
            if (fechasCitas.includes(fechaFormateada)) {
                dia.classList.add('dia-con-cita');  // Destacar el día con una clase CSS especial
            }
        });
    }
    //------------------------------------EVENTOS DE LOS BOTONES------------------------------------
    prevButton.addEventListener('click', function () {
        if (currentView === 'month') {
            currentDate.setMonth(currentDate.getMonth() - 1);
        } else {
            currentDate.setDate(currentDate.getDate() - 7);
        }
        updateCalendar();
    });

    nextButton.addEventListener('click', function () {
        if (currentView === 'month') {
            currentDate.setMonth(currentDate.getMonth() + 1);
        } else {
            currentDate.setDate(currentDate.getDate() + 7);
        }
        updateCalendar();
    });

    todayButton.addEventListener('click', function () {
        currentDate = new Date();
        updateCalendar();
    });

    weekViewButton.addEventListener('click', function () {
        currentView = 'week';
        updateCalendar();
    });

    monthViewButton.addEventListener('click', function () {
        currentView = 'month';
        updateCalendar();
    });

    
    //------------------------------------CERRAR POPUP CITAS------------------------------------
    window.addEventListener("click", function (event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    });

    updateCalendar();
    // Función para mostrar el popup con las citas
    function mostrarPopupCitas(citasDelDia) {
        const popupCitas = document.getElementById("popupCitas");
        const popupCitasContent = document.getElementById("popup-content");
        // Limpiar el contenido previo
        popupCitasContent.innerHTML = '';
        // Agregar las citas al popup
        citasDelDia.forEach(cita => {
            const citaElement = document.createElement('div');
            citaElement.classList.add('cita-item');
            citaElement.setAttribute('data-cita-id', cita.id);  // Agregar el dataset con el ID de la cita
            citaElement.innerHTML = `
                <p> ${cita.titulo}</p>
                <p> ${cita.hora}</p>
                <p><strong>Descripción:</strong> ${cita.descripcion}</p>
            `;
            popupCitasContent.appendChild(citaElement);

            // Agregar el evento de clic a todo el contenedor #popup-content
            document.getElementById("popup-content").addEventListener("click", function (event) {
                if (event.target.classList.contains("cita-item") || event.target.parentNode.classList.contains("cita-item")) {
                    const citaId = event.target.getAttribute("data-cita-id") || event.target.parentNode.getAttribute("data-cita-id");
                    const cita = citas.find(c => c.id === parseInt(citaId));
                    if (cita) {
                        // Mostrar el popup para editar la cita
                        document.getElementById("popupEditarCita").classList.add("mostrar");
                        console.log("Popup para editar la cita mostrado");
            
                        // Rellenar los campos del formulario con los datos de la cita
                        document.getElementById("cita_id").value = cita.id;
                        document.getElementById("titulo").value = cita.titulo;
                        document.getElementById("paciente").value = cita.paciente.id;
                        document.getElementById("fecha").value = cita.fecha;
                        document.getElementById("hora").value = cita.hora;
                        document.getElementById("sala").value = cita.sala;
                        document.getElementById("detalle").value = cita.descripcion;
                    }
                }
            });
        });

        // Mostrar el popup con las citas
        popupCitas.style.display = 'block';
    }
    // Función para obtener las citas del día seleccionado
    function obtenerCitasPorFecha(fechaDia) {
        const [dia, mes, anio] = fechaDia.split('/');
        const fechaFormateada = `${anio}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;

        // Filtrar citas que coinciden con esta fecha
        return citas.filter(cita => cita.fecha === fechaFormateada);
    }
    // Evento para mostrar el popup de citas
    document.querySelectorAll(".day").forEach(day => {
        day.addEventListener("click", function () {
            const selectedDate = this.getAttribute("data-fecha");
            const citasDelDia = obtenerCitasPorFecha(selectedDate);
            if (citasDelDia.length > 0) {
                mostrarPopupCitas(citasDelDia);  // Muestra el popup si hay citas
            } else {
                alert("No hay citas agendadas para este día.");
            }
        });
    });
});
