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
    const modal = document.getElementById("nuevaCita");
    const modal_editar = document.getElementById("editarCita");
    const btnCerrar = document.getElementById("cerrarModal");
    const btnCancelar = document.getElementById("cancelarNuevaCita");
    const btnCerrarEditar = document.getElementById("cerrarEditarModal");
    const btnCancelarEditar = document.getElementById("cancelarEditarCita");
    const eliminarCitaBtn = document.getElementById('eliminarCita');
    const confirmarEliminarModal = document.getElementById('confirmarEliminarCita');
    const cerrarConfirmarEliminarModal = document.getElementById('cerrarConfirmarEliminarModal');
    const cancelarEliminarCita = document.getElementById('cancelarEliminarCita');
    const confirmarEliminarCitaBtn = document.getElementById('confirmarEliminarCitaBtn');
    const citaIdInput = document.getElementById('cita_id'); // El input hidden que tiene el cita_id

    // Referencias a los elementos del modal de nueva cita
    const tipoCitaPresencial = document.getElementById('tipo_presencial');
    const tipoCitaOnline = document.getElementById('tipo_online');
    const horaInicioInput = document.getElementById('hora_inicio');
    const horaFinalInput = document.getElementById('hora_final');

    // Referencias a los elementos del modal de editar cita
    const tipoCitaPresencialEditar = document.getElementById('tipo_presencial_editar');
    const tipoCitaOnlineEditar = document.getElementById('tipo_online_editar');
    const horaInicioEditarInput = document.getElementById('hora_inicio_editar');
    const horaFinalEditarInput = document.getElementById('hora_final_editar');

    // Función para actualizar la hora final según el tipo de cita
    function actualizarHoraFinal(modalType) {
        if (modalType === 'nueva') {
            if (tipoCitaOnline.checked) {
                ajustarHoraFinal(horaInicioInput, horaFinalInput);
                horaFinalInput.readOnly = true;
            } else {
                horaFinalInput.readOnly = false;
            }
        } else if (modalType === 'editar') {
            if (tipoCitaOnlineEditar.checked) {
                ajustarHoraFinal(horaInicioEditarInput, horaFinalEditarInput);
                horaFinalEditarInput.readOnly = true;
            } else {
                horaFinalEditarInput.readOnly = false;
            }
        }
    }

    function ajustarHoraFinal(horaInicioElem, horaFinalElem) {
        const horaInicio = horaInicioElem.value;
        if (horaInicio) {
            const [hours, minutes] = horaInicio.split(':');
            const inicioDate = new Date(0, 0, 0, parseInt(hours), parseInt(minutes));
            const finDate = new Date(inicioDate.getTime() + 30 * 60000); // Añadir 30 minutos

            const finHours = String(finDate.getHours()).padStart(2, '0');
            const finMinutes = String(finDate.getMinutes()).padStart(2, '0');
            horaFinalElem.value = `${finHours}:${finMinutes}`;
        }
    }

    // Eventos para el modal de nueva cita
    tipoCitaPresencial.addEventListener('change', function() { actualizarHoraFinal('nueva'); });
    tipoCitaOnline.addEventListener('change', function() { actualizarHoraFinal('nueva'); });
    horaInicioInput.addEventListener('change', function() {
        if (tipoCitaOnline.checked) {
            actualizarHoraFinal('nueva');
        }
    });

    // Eventos para el modal de editar cita
    tipoCitaPresencialEditar.addEventListener('change', function() { actualizarHoraFinal('editar'); });
    tipoCitaOnlineEditar.addEventListener('change', function() { actualizarHoraFinal('editar'); });
    horaInicioEditarInput.addEventListener('change', function() {
        if (tipoCitaOnlineEditar.checked) {
            actualizarHoraFinal('editar');
        }
    });


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
            
            calendarHTML += `<div class="day ${isToday ? 'today' : ''}" data-fecha="${fechaFormateada}" data-day="${day}">${day}</div>`;
        }
    
        const totalCells = adjustedFirstDay + daysInMonth;
        for (let i = totalCells; i < 42; i++) {
            calendarHTML += `<div class="empty-day"></div>`;
        }
    
        calendarHTML += '</div>'; // Cerrar el div de calendar-grid
        calendar.innerHTML = calendarHTML;
    
        // Asignar eventos de clic a los días
        document.querySelectorAll('.day').forEach(dayElement => {
            dayElement.addEventListener('click', function() {
                const fechaSeleccionada = this.getAttribute('data-fecha');
                // Convertir fecha de 'DD/MM/YYYY' a Date object
                const [day, month, year] = fechaSeleccionada.split('/');
                currentDate = new Date(year, month - 1, day);
                currentView = 'week';
                updateCalendar();
            });
        });
    }
    

    function generateWeekView() {
        const startOfWeek = getStartOfWeek(currentDate);
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(endOfWeek.getDate() + 6);
        monthYearLabel.textContent = `${formatDate(startOfWeek)} - ${formatDate(endOfWeek)}`;
    
        // Obtener el día actual
        const today = new Date();
        const todayFormatted = formatDate(today); // 'DD/MM/YYYY'
    
        // Crear un array con los nombres de los días y las fechas correspondientes
        const daysOfWeek = [];
        let todayIndex = -1; // Inicializar con -1 indicando que el día actual no está en la semana mostrada
        for (let i = 0; i < 7; i++) {
            const currentDay = new Date(startOfWeek);
            currentDay.setDate(currentDay.getDate() + i);
            const dayName = getDayName(currentDay.getDay()); // Obtener el nombre del día basado en getDay()
            const formattedDate = formatDate(currentDay); // 'DD/MM/YYYY'
            daysOfWeek.push({ dayName, formattedDate, date: currentDay });
            
            // Verificar si currentDay es hoy
            if (formattedDate === todayFormatted) {
                todayIndex = i; // Guardar el índice del día actual
            }
        }
    
        let calendarHTML = `
            <div class="week-view-container">
                <table class="week-view">
                    <thead>
                        <tr>
                            <th>Hora</th>`;
    
        daysOfWeek.forEach((day, index) => {
            // Si el índice coincide con todayIndex, agregamos una clase especial
            const isToday = index === todayIndex;
            calendarHTML += `<th class="${isToday ? 'today-column' : ''}">${day.dayName} ${day.formattedDate}</th>`;
        });
    
        calendarHTML += `
                        </tr>
                    </thead>
                    <tbody>`;
    
        for (let hour = 8; hour < 20; hour++) {
            for (let minutes = 0; minutes < 60; minutes += 30) {
                const horaInicio = String(hour).padStart(2, '0') + ":" + String(minutes).padStart(2, '0');
                let nextHour = hour;
                let nextMinutes = minutes + 30;
                if (nextMinutes >= 60) {
                    nextHour += 1;
                    nextMinutes = 0;
                }
                const horaFin = String(nextHour).padStart(2, '0') + ":" + String(nextMinutes).padStart(2, '0');
                const horaStr = `${horaInicio} - ${horaFin}`;
    
                calendarHTML += `<tr><td class="time-slot">${horaStr}</td>`;
                for (let day = 0; day < 7; day++) {
                    const date = new Date(startOfWeek);
                    date.setDate(date.getDate() + day);
                    const formattedDate = formatDate(date);
                    const isToday = day === todayIndex;
                    calendarHTML += `<td class="week-hour ${isToday ? 'today-column' : ''}" data-date="${formattedDate}" data-hour-inicio="${horaInicio}" data-hour-fin="${horaFin}"></td>`;
                }
                calendarHTML += '</tr>';
            }
        }
    
        calendarHTML += '</tbody></table></div>';
        calendar.innerHTML = calendarHTML;
    
        // Reasignar eventos de click para la vista semanal
        document.querySelectorAll('.week-hour').forEach(hourBlock => {
            hourBlock.addEventListener('click', function() {
                const fecha = this.getAttribute('data-date'); // 'DD/MM/YYYY'
                const horaInicio = this.getAttribute('data-hour-inicio'); // 'HH:MM'
                const horaFin = this.getAttribute('data-hour-fin'); // 'HH:MM'
                abrirModal(fecha, horaInicio, horaFin);
            });
        });
    }
    
    
    // Modificar getDayName para usar getDay() correctamente
    function getDayName(dayIndex) {
        const dayNames = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
        return dayNames[dayIndex];
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

        // Convertir horas a minutos para calcular la duración
        function timeToMinutes(timeStr) {
            const [hours, minutes] = timeStr.split(':').map(Number);
            return hours * 60 + minutes;
        }

        const inicioMinutes = timeToMinutes(horaInicio);
        const finMinutes = timeToMinutes(horaFin);
        const duracion = finMinutes - inicioMinutes;

        // Calcular el número de bloques de 30 minutos
        const duracionEnBloques = Math.ceil(duracion / 30);

        // Iterar sobre cada bloque que ocupa la cita
        for (let i = 0; i < duracionEnBloques; i++) {
            const bloqueMinutes = inicioMinutes + i * 30;
            const bloqueHoraInicio = minutesToTime(bloqueMinutes);

            // Obtener la celda correspondiente
            const cell = document.querySelector(`.week-hour[data-date="${fechaFormateada}"][data-hour-inicio="${bloqueHoraInicio}"]`);

            if (cell) {
                // Asegurarse de que la celda esté vacía
                if (!cell.hasChildNodes()) {
                    const citaDiv = document.createElement('div');
                    citaDiv.classList.add('cita-semana');

                    if (cita.tipo_cita === 'online') {
                        citaDiv.classList.add('cita-online');
                    }

                    // Solo mostrar el título en la primera celda
                    
                                        citaDiv.innerHTML = `${cita.titulo}<br>${cita.paciente.nombre}`;
                  

                    citaDiv.title = `Título: ${cita.titulo}\nPaciente: ${cita.paciente.nombre}\nSala: ${cita.sala}\nDetalle: ${cita.detalle}`;
                    citaDiv.addEventListener('click', function(event) {
                        event.stopPropagation(); 
                        abrirEditar(
                            cita.id,
                            cita.fecha.split('-').reverse().join('/'),
                            cita.hora_inicio,
                            cita.hora_final,
                            cita.titulo,
                            cita.paciente.id,
                            cita.paciente.nombre,
                            cita.sala,
                            cita.detalle,
                            cita.tipo_cita 
                        );
                    });

                    cell.appendChild(citaDiv);
                }
            } else {
                console.warn(`No se encontró la celda para la cita: ${cita.titulo} en ${fechaFormateada} a las ${bloqueHoraInicio}`);
            }
        }
    });
}

// Función auxiliar para convertir minutos a hora en formato HH:MM
function minutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return String(hours).padStart(2, '0') + ':' + String(mins).padStart(2, '0');
}

    

    //     // Función para destacar horas con citas en vista semanal
    // function destacarHorasConCita(citas) {
    //     citas.forEach(cita => {
    //         // Obtener la fecha y hora de la cita
    //         const fecha = cita.fecha; // 'YYYY-MM-DD'
    //         const horaInicio = cita.hora_inicio; // 'HH:MM'
    //         const horaFin = cita.hora_final; // 'HH:MM'
            
    //         console.log(`Procesando cita: ${cita.titulo} en ${fecha} de ${horaInicio} a ${horaFin}`);
            
    //         // Convertir fecha a 'DD/MM/YYYY'
    //         const fechaParts = cita.fecha.split('-');
    //         const fechaFormateada = `${fechaParts[2]}/${fechaParts[1]}/${fechaParts[0]}`;
            
    //         // Convertir horas a formato de 24 horas
    //         const horaInicioParts = horaInicio.split(':');
    //         const horaFinParts = horaFin.split(':');
    //         const horaInicioDecimal = parseInt(horaInicioParts[0]) + parseInt(horaInicioParts[1]) / 60;
    //         const horaFinDecimal = parseInt(horaFinParts[0]) + parseInt(horaFinParts[1]) / 60;
    
    //         // Calcular la duración de la cita en bloques de 30 minutos
    //         const duracionEnHoras = horaFinDecimal - horaInicioDecimal;
    //         const duracionEnBloques = duracionEnHoras * 2; // Cada bloque representa 30 minutos
    
    //         // Obtener la celda correspondiente al inicio de la cita
    //         const cell = document.querySelector(`.week-hour[data-date="${fechaFormateada}"][data-hour="${horaInicio}"]`);
            
    //         if (cell) {
    //             console.log(`Cita encontrada en cell: ${cell}`);
    
    //             // Crear un elemento para la cita
    //             const citaDiv = document.createElement('div');
    //             citaDiv.classList.add('cita-semana');
    //             citaDiv.textContent = cita.titulo;
    //             citaDiv.title = `Título: ${cita.titulo}\nPaciente: ${cita.paciente.nombre}\nSala: ${cita.sala}\nDetalle: ${cita.descripcion}`;
    
    //             // Hacer que la cita ocupe varios bloques usando rowspan
    //             cell.setAttribute('rowspan', duracionEnBloques);
    
    //             // Agregar evento de clic para ver detalles
    //             citaDiv.addEventListener('click', function(event) {
    //                 event.stopPropagation(); // Evitar que se abra el modal de crear cita
    //                 abrirEditar(cita.id, cita.fecha.split('-').reverse().join('/'), cita.hora_inicio, cita.hora_final, cita.titulo,  cita.paciente.id , cita.paciente.nombre, cita.sala, cita.detalle);
    //             });
    
    //             cell.appendChild(citaDiv);
    
    //             // Remover las celdas que se superponen
    //             for (let i = 1; i < duracionEnBloques; i++) {
    //                 const nextHour = horaInicioDecimal + i * 0.5;
    //                 const nextHourStr = String(Math.floor(nextHour)).padStart(2, '0') + ':' + String((nextHour % 1) * 60).padStart(2, '0');
    //                 const nextCell = document.querySelector(`.week-hour[data-date="${fechaFormateada}"][data-hour="${nextHourStr}"]`);
    //                 if (nextCell) {
    //                     nextCell.style.display = 'none';
    //                 }
    //             }
    //         } else {
    //             console.warn(`No se encontró la celda para la cita: ${cita.titulo} en ${fechaFormateada} a las ${horaInicio}`);
    //         }
    //     });
    // }
    

    function abrirModal(fecha, hora_inicio = null, hora_final = null) {
        console.log(`Abrir modal para fecha: ${fecha}, hora_inicio: ${hora_inicio}, hora_final: ${hora_final}`);
        modal.style.display = "block";
    
        // Convertir 'DD/MM/YYYY' a 'YYYY-MM-DD'
        const fechaISO = fecha.split('/').reverse().join('-');
        console.log(`Fecha ISO: ${fechaISO}`);
        document.getElementById("fecha").value = fechaISO;
        tipoCitaPresencial.checked = true;
        tipoCitaOnline.checked = false;
        horaFinalInput.readOnly = false;
    
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

        actualizarHoraFinal('nueva');
    }

    // Reasignación de IDs en abrirEditar
    function abrirEditar(cita_id, fecha, hora_inicio = null, hora_final = null, titulo = null, paciente_id = null, paciente_nombre = null, sala = null, detalle = null, tipo_cita = null) {
        modal_editar.style.display = "block";

        const fechaISO = fecha.split('/').reverse().join('-');
        document.getElementById("cita_id").value = cita_id;
        document.getElementById("fecha_editar").value = fechaISO;
        document.getElementById("hora_inicio_editar").value = hora_inicio || '';
        document.getElementById("hora_final_editar").value = hora_final || '';
        document.getElementById("titulo_editar").value = titulo || '';
        const pacienteSelect = document.getElementById("paciente_editar");

        if (tipo_cita === 'online') {
            tipoCitaOnlineEditar.checked = true;
            tipoCitaPresencialEditar.checked = false;
            horaFinalEditarInput.readOnly = true;
        } else {
            tipoCitaPresencialEditar.checked = true;
            tipoCitaOnlineEditar.checked = false;
            horaFinalEditarInput.readOnly = false;
        }

        // Verificar si el paciente con la ID existe en las opciones del select
        let optionExists = false;
        for (let i = 0; i < pacienteSelect.options.length; i++) {
            if (pacienteSelect.options[i].value === String(paciente_id)) {
                optionExists = true;
                break;
            }
        }

        if (optionExists) {
            // Si el paciente existe en el select, seleccionarlo
            pacienteSelect.value = paciente_id;
        } else {
            // Si no existe, agregar una opción temporal con el nombre y la ID del paciente
            let newOption = new Option(paciente_nombre, paciente_id, true, true);
            pacienteSelect.add(newOption);
        }

        document.getElementById("sala_editar").value = sala || '';
        document.getElementById("detalle_editar").value = detalle || '';

        actualizarHoraFinal('editar');
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

    // Para el modal de crear nueva cita
    btnCerrar.onclick = btnCancelar.onclick = function() {
        modal.style.display = "none";
    };

    // Para el modal de editar cita
    btnCerrarEditar.onclick = btnCancelarEditar.onclick = function() {
        modal_editar.style.display = "none";
    };

    // Función para abrir el modal de confirmación
    eliminarCitaBtn.addEventListener('click', function () {
        confirmarEliminarModal.style.display = 'block';
    });

    // Función para cerrar el modal de confirmación
    cerrarConfirmarEliminarModal.addEventListener('click', function () {
        confirmarEliminarModal.style.display = 'none';
    });

    // Cerrar modal de confirmación al cancelar
    cancelarEliminarCita.addEventListener('click', function () {
        confirmarEliminarModal.style.display = 'none';
    });

    // Función para confirmar la eliminación de la cita
    confirmarEliminarCitaBtn.addEventListener('click', function () {
        // Obtener el valor de cita_id
        const citaId = citaIdInput.value;

        // Redirigir a la URL de eliminación de la cita con el cita_id en la ruta
        const eliminarUrl = `/eliminar_cita/${citaId}/`;

        // Redirigir a la URL
        window.location.href = eliminarUrl;
    });

    // Cerrar el modal si se hace clic fuera de la ventana del modal
    window.addEventListener('click', function (event) {
        if (event.target == confirmarEliminarModal) {
            confirmarEliminarModal.style.display = 'none';
        }
    });
    

    updateCalendar();
});
