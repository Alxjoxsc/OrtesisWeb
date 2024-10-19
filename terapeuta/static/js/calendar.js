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
    let citas = [];
    const modal = document.getElementById("nuevaCita");
    const btnCerrar = document.getElementById("cerrarModal");
    const btnCancelar = document.getElementById("cancelarNuevaCita");

    function updateCalendar() {
        calendar.innerHTML = ""; // Limpiar el calendario antes de actualizar
        if (currentView === 'month') {
            generateMonthView();
        } else {
            generateWeekView();
        }
        fetch('/obtener-fechas-citas/')
            .then(response => response.json())
            .then(data => {
                citas = data.citas || [];
                if (currentView === 'month') {
                    destacarDiasConCita(citas.map(cita => cita.fecha));
                } else {
                    destacarHorasConCita(citas);
                }
            })
            .catch(error => console.error('Error al obtener las citas:', error));
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
            calendarHTML += `<div class="day ${isToday ? 'today' : ''}" data-fecha="${day}/${month + 1}/${year}" onclick="abrirModal('${day}/${month + 1}/${year}')">${day}</div>`;
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
            calendarHTML += `<tr><td class="time-slot">${hour}:00</td>`;
            for (let day = 0; day < 7; day++) {
                const currentDay = new Date(startOfWeek);
                currentDay.setDate(currentDay.getDate() + day);
                const formattedDate = formatDate(currentDay);
                calendarHTML += `<td class="week-hour" data-hour="${hour}:00" data-day="${day}" onclick="abrirModal('${formattedDate}', '${hour}:00')"></td>`;
            }
            calendarHTML += '</tr>';
        }

        calendarHTML += '</tbody></table></div>';
        calendar.innerHTML = calendarHTML;

        // Reasignar eventos de click para la vista semanal
        document.querySelectorAll('.week-hour').forEach(hourBlock => {
            hourBlock.addEventListener('click', function() {
                const fecha = this.getAttribute('data-day');
                const hora = this.getAttribute('data-hour');
                abrirModal(fecha, hora);
            });
        });
    }

    function abrirModal(fecha, hora = null) {
        modal.style.display = "block";
        document.getElementById("fecha_inicio").value = fecha.split('/').reverse().join('-');
        if (hora) {
            document.getElementById("hora").value = hora;
        }
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
