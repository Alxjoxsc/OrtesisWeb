document.addEventListener('DOMContentLoaded', function () {
    const prevButton = document.getElementById('prev');
    const nextButton = document.getElementById('next');
    const todayButton = document.getElementById('today');
    const monthYearLabel = document.getElementById('month-year');
    const calendar = document.getElementById('calendar');
    const weekViewButton = document.getElementById('week-view');
    const monthViewButton = document.getElementById('month-view');
    let currentDate = new Date();
    let currentView = 'month'; // 'month' o 'week'
    // let citas = []; // Eliminar esta línea
    const modal = document.getElementById("nuevaCita");
    const modal_editar = document.getElementById("editarCita");
    const btnCerrar = document.getElementById("cerrarModal");
    const btnCancelar = document.getElementById("cancelarNuevaCita");

    // Verificar que 'citas' está definida
    if (typeof citas === 'undefined') {
        console.error('La variable "citas" no está definida.');
        citas = [];
    } else {
        console.log('Citas cargadas:', citas);
    }

    function updateCalendar() {
        calendar.innerHTML = ""; // Limpiar el calendario antes de actualizar
        if (currentView === 'month') {
            generateMonthView();
        } else {
            generateWeekView();
        }
        if (currentView === 'month') {
            destacarDiasConCita(citas);
        } else {
            destacarHorasConCita(citas);
        }
    }

    function generateMonthView() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        monthYearLabel.textContent = `${getMonthName(month)} ${year}`;
        
        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const adjustedFirstDay = (firstDayOfMonth === 0) ? 6 : firstDayOfMonth - 1;

        let calendarHTML = '<div class="calendar-grid">';
        ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].forEach(day => {
            calendarHTML += `<div class="day-name">${day}</div>`;
        });

        for (let i = 0; i < adjustedFirstDay; i++) {
            calendarHTML += `<div class="empty-day"></div>`;
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = (day === new Date().getDate() && year === new Date().getFullYear() && month === new Date().getMonth());
            // Formatear la fecha como 'DD/MM/YYYY'
            const dayStr = String(day).padStart(2, '0');
            const monthStr = String(month + 1).padStart(2, '0');
            const fechaFormateada = `${dayStr}/${monthStr}/${year}`;
            
            calendarHTML += `<div class="day ${isToday ? 'today' : ''}" data-fecha="${fechaFormateada}" onclick="abrirModal('${fechaFormateada}')">${day}</div>`;
        }

        const totalCells = adjustedFirstDay + daysInMonth;
        for (let i = totalCells; i < 42; i++) {
            calendarHTML += `<div class="empty-day"></div>`;
        }

        calendar.innerHTML = calendarHTML;
    }

    function generateWeekView() {
        const startOfWeek = getStartOfWeek(currentDate);
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(endOfWeek.getDate() + 6);
        monthYearLabel.textContent = `${formatDate(startOfWeek)} - ${formatDate(endOfWeek)}`;

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

        for (let hour = 8; hour <= 20; hour++) {
            const horaStr = String(hour).padStart(2, '0') + ":00";
            calendarHTML += `<tr><td class="time-slot">${horaStr}</td>`;
            for (let day = 0; day < 7; day++) {
                const currentDay = new Date(startOfWeek);
                currentDay.setDate(currentDay.getDate() + day);
                const formattedDate = formatDate(currentDay);
                // Eliminar onclick del HTML
                calendarHTML += `<td class="week-hour" data-date="${formattedDate}" data-hour="${horaStr}"></td>`;
            }
            calendarHTML += '</tr>';
        }

        calendarHTML += '</tbody></table></div>';
        calendar.innerHTML = calendarHTML;

        // Reasignar eventos de click para la vista semanal
        document.querySelectorAll('.week-hour').forEach(hourBlock => {
            hourBlock.addEventListener('click', function() {
                const fecha = this.getAttribute('data-date'); // 'DD/MM/YYYY'
                const hora = this.getAttribute('data-hour'); // 'HH:MM'
                abrirModal(fecha, hora);
            });
        });
    }

    // Función para destacar días con citas en vista mensual
    function destacarDiasConCita(citas) {
        // Crear un diccionario para contar citas por día
        const contadorCitas = {};
        
        citas.forEach(cita => {
            // Convertir fecha de 'YYYY-MM-DD' a 'DD/MM/YYYY'
            const fechaParts = cita.fecha.split('-');
            const fechaFormateada = `${fechaParts[2]}/${fechaParts[1]}/${fechaParts[0]}`;
            
            if (contadorCitas[fechaFormateada]) {
                contadorCitas[fechaFormateada]++;
            } else {
                contadorCitas[fechaFormateada] = 1;
            }
        });
        
        // Iterar sobre los días del calendario
        const dias = document.querySelectorAll('.day');
        dias.forEach(dia => {
            const fecha = dia.getAttribute('data-fecha'); // 'DD/MM/YYYY'
            if (contadorCitas[fecha]) {
                // Crear un elemento para mostrar el número de citas
                const badge = document.createElement('span');
                badge.classList.add('cita-badge');
                badge.textContent = contadorCitas[fecha];
                dia.appendChild(badge);
            }
        });
    }

    // Función para destacar horas con citas en vista semanal
    function destacarHorasConCita(citas) {
        citas.forEach(cita => {
            // Obtener la fecha y hora de la cita
            const fecha = cita.fecha; // 'YYYY-MM-DD'
            const horaInicio = cita.hora_inicio; // 'HH:MM'
            const horaFin = cita.hora_final; // 'HH:MM'
            
            console.log(`Procesando cita: ${cita.titulo} en ${fecha} de ${horaInicio} a ${horaFin}`);
            
            // Convertir fecha a 'DD/MM/YYYY'
            const fechaParts = cita.fecha.split('-');
            const fechaFormateada = `${fechaParts[2]}/${fechaParts[1]}/${fechaParts[0]}`;
            
            // Convertir horas a formato de 24 horas
            const horaInicioParts = horaInicio.split(':');
            const horaFinParts = horaFin.split(':');
            const horaInicioDecimal = parseInt(horaInicioParts[0]) + parseInt(horaInicioParts[1]) / 60;
            const horaFinDecimal = parseInt(horaFinParts[0]) + parseInt(horaFinParts[1]) / 60;
    
            // Calcular la duración de la cita en bloques de 30 minutos
            const duracionEnHoras = horaFinDecimal - horaInicioDecimal;
            const duracionEnBloques = duracionEnHoras * 2; // Cada bloque representa 30 minutos
    
            // Obtener la celda correspondiente al inicio de la cita
            const cell = document.querySelector(`.week-hour[data-date="${fechaFormateada}"][data-hour="${horaInicio}"]`);
            
            if (cell) {
                console.log(`Cita encontrada en cell: ${cell}`);
    
                // Crear un elemento para la cita
                const citaDiv = document.createElement('div');
                citaDiv.classList.add('cita-semana');
                citaDiv.textContent = cita.titulo;
                citaDiv.title = `Título: ${cita.titulo}\nPaciente: ${cita.paciente.nombre}\nSala: ${cita.sala}\nDetalle: ${cita.descripcion}`;
    
                // Hacer que la cita ocupe varios bloques usando rowspan
                cell.setAttribute('rowspan', duracionEnBloques);
    
                // Agregar evento de clic para ver detalles
                citaDiv.addEventListener('click', function(event) {
                    event.stopPropagation(); // Evitar que se abra el modal de crear cita
                    abrirEditar(cita.fecha.split('-').reverse().join('/'), cita.hora_inicio, cita.hora_final, cita.titulo,  `${cita.paciente.nombre}`, cita.sala, cita.detalle);
                });
    
                cell.appendChild(citaDiv);
    
                // Remover las celdas que se superponen
                for (let i = 1; i < duracionEnBloques; i++) {
                    const nextCell = document.querySelector(`.week-hour[data-date="${fechaFormateada}"][data-hour="${horaInicioDecimal + i * 0.5}:00"]`);
                    if (nextCell) {
                        nextCell.remove();
                    }
                }
            } else {
                console.warn(`No se encontró la celda para la cita: ${cita.titulo} en ${fechaFormateada} a las ${horaInicio}`);
            }
        });
    }
    

    function abrirModal(fecha, hora_inicio = null, hora_final = null) {
        console.log(`Abrir modal para fecha: ${fecha}, hora_inicio: ${hora_inicio}, hora_final: ${hora_final}`);
        modal.style.display = "block";
    
        // Convertir 'DD/MM/YYYY' a 'YYYY-MM-DD'
        const fechaISO = fecha.split('/').reverse().join('-');
        console.log(`Fecha ISO: ${fechaISO}`);
        document.getElementById("fecha").value = fechaISO;
    
        // Asignar hora de inicio si existe
        if (hora_inicio) {
            document.getElementById("hora_inicio").value = hora_inicio;
    
            // Si no se ha proporcionado hora_final, asignar hora_inicio + 1 hora
            if (!hora_final) {
                const [hours, minutes] = hora_inicio.split(':');
                let nuevaHoraFinal = parseInt(hours) + 1; // Sumar una hora
                if (nuevaHoraFinal < 10) {
                    nuevaHoraFinal = `0${nuevaHoraFinal}`; // Formatear con un cero delante si es menor a 10
                }
                hora_final = `${nuevaHoraFinal}:${minutes}`; // Mantener los mismos minutos
            }
        }
    
        // Asignar hora de finalización si existe
        if (hora_final) {
            document.getElementById("hora_final").value = hora_final;
        } else {
            document.getElementById("hora_final").value = '';
        }
    
        // Limpiar otros campos para una nueva cita
        document.getElementById("titulo").value = '';
        document.getElementById("paciente").value = '';
        document.getElementById("sala").value = '';
        document.getElementById("detalle").value = '';
    }

    function abrirEditar(fecha, hora_inicio = null, hora_final = null, titulo = null, paciente=null, sala=null, detalle=null) {
        console.log(`Abrir modal para fecha: ${fecha}, hora_inicio: ${hora_inicio}, hora_final: ${hora_final}`);
        modal.style.display = "block";
    
        // Convertir 'DD/MM/YYYY' a 'YYYY-MM-DD'
        const fechaISO = fecha.split('/').reverse().join('-');
        console.log(`Fecha ISO: ${fechaISO}`);
        document.getElementById("fecha").value = fechaISO;
        console.log(titulo);
        console.log(paciente);
        console.log(sala);
        console.log(detalle);
    
        // Asignar hora de inicio si existe
        if (hora_inicio) {
            document.getElementById("hora_inicio").value = hora_inicio;
    
            // Si no se ha proporcionado hora_final, asignar hora_inicio + 1 hora
            if (!hora_final) {
                const [hours, minutes] = hora_inicio.split(':');
                let nuevaHoraFinal = parseInt(hours) + 1; // Sumar una hora
                if (nuevaHoraFinal < 10) {
                    nuevaHoraFinal = `0${nuevaHoraFinal}`; // Formatear con un cero delante si es menor a 10
                }
                hora_final = `${nuevaHoraFinal}:${minutes}`; // Mantener los mismos minutos
            }
        }
    
        // Asignar hora de finalización si existe
        if (hora_final) {
            document.getElementById("hora_final").value = hora_final;
        } else {
            document.getElementById("hora_final").value = '';
        }

        // Asignar otros campos para una nueva cita
        document.getElementById("titulo").value = titulo;
        document.getElementById("paciente").value = paciente;
        document.getElementById("sala").value = sala;
        document.getElementById("detalle").value = detalle;
    }
    
    function getStartOfWeek(date) {
        const dayOfWeek = date.getDay() === 0 ? 6 : date.getDay() - 1;
        const startOfWeek = new Date(date);
        startOfWeek.setDate(date.getDate() - dayOfWeek);
        return startOfWeek;
    }

    function formatDate(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        return `${day}/${month}/${date.getFullYear()}`;
    }

    function getMonthName(monthIndex) {
        return ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][monthIndex];
    }

    // Manejo de botones de navegación y vistas
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

    btnCerrar.onclick = btnCancelar.onclick = function() {
        modal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    updateCalendar();
});
