document.addEventListener("DOMContentLoaded", function () {
    // Elementos para la funcionalidad de desvinculación
    const desvincularBtn = document.querySelector(".desvincular-btn");
    const modal = document.getElementById("desvincularModal");
    const cancelarBtn = document.getElementById("cancelarDesvinculacion");
    const confirmarBtn = document.getElementById("confirmarDesvinculacion");
    const motivoTextarea = document.getElementById("motivo");

    // Elementos para la funcionalidad de añadir rutina
    const nuevaRutinaModal = document.getElementById('nuevaRutinaModal');
    const btnNuevaRutina = document.querySelector('.btn-añadir-rutina');
    const cerrarNuevaRutina = document.getElementById('cerrarNuevaRutina');
    const cancelarNuevaRutina = document.getElementById('cancelarNuevaRutina');
    const nuevaRutinaForm = document.getElementById('nuevaRutinaForm');

    // Mostrar popup cuando se presiona "Desvincular paciente"
    if (desvincularBtn) {
        desvincularBtn.addEventListener("click", function () {
            modal.style.display = "flex";
        });
    }

    // Ocultar popup cuando se presiona "Cancelar" en desvinculación
    if (cancelarBtn) {
        cancelarBtn.addEventListener("click", function () {
            modal.style.display = "none";
        });
    }

    // Ocultar popup cuando se hace clic fuera del modal de desvinculación
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

     // Manejar el envío del formulario de nueva rutina
    if (nuevaRutinaForm) {
        nuevaRutinaForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevenir el envío por defecto del formulario

            const pacienteId = document.getElementById('pacienteId').value;

            // Obtener los datos del formulario
            const formData = new FormData(nuevaRutinaForm);

            // Enviar los datos al backend usando fetch
            fetch(`/paciente/${pacienteId}/crear_rutina/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken, // Asegúrate de que csrftoken está definido
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Rutina creada exitosamente.');
                    // Puedes actualizar la página o la lista de rutinas aquí
                    window.location.reload();
                } else {
                    alert('Error al crear la rutina: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error al crear la rutina:', error);
                alert('Ocurrió un error al crear la rutina.');
            });

            // Ocultar el modal después de enviar los datos
            nuevaRutinaModal.style.display = 'none';
        });
    }

    // Confirmar y enviar motivo de inactivación
    if (confirmarBtn) {
        confirmarBtn.addEventListener("click", function () {
            const pacienteId = document.getElementById("pacienteId").value;
            const motivo = motivoTextarea.value;

            if (motivo.trim() === "") {
                alert("Debe ingresar un motivo para inactivar al paciente.");
                return;
            }

            // Enviar los datos al backend con fetch
            fetch(`/paciente/cambiar-estado/${pacienteId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ motivo: motivo })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    window.location.href = '/pacientes_terapeuta/';
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error al desvincular paciente:', error);
            });

            // Ocultar modal después de enviar los datos
            modal.style.display = "none";
        });
    }
    
    if (btnNuevaRutina) {
        btnNuevaRutina.onclick = function () {
            nuevaRutinaModal.style.display = 'block';
        };
    }

    if (cerrarNuevaRutina) {
        cerrarNuevaRutina.onclick = function () {
            nuevaRutinaModal.style.display = 'none';
        };
    }

    if (cancelarNuevaRutina) {
        cancelarNuevaRutina.onclick = function () {
            nuevaRutinaModal.style.display = 'none';
        };
    }
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
        if (event.target === nuevaRutinaModal) {
            nuevaRutinaModal.style.display = 'none';
        }
    };

});