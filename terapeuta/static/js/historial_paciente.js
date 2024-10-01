document.addEventListener("DOMContentLoaded", function () {
    const desvincularBtn = document.querySelector(".desvincular-btn");
    const modal = document.getElementById("desvincularModal");
    const cancelarBtn = document.getElementById("cancelarDesvinculacion");
    const confirmarBtn = document.getElementById("confirmarDesvinculacion");
    const motivoTextarea = document.getElementById("motivo");

    // Mostrar popup cuando se presiona "Desvincular paciente"
    desvincularBtn.addEventListener("click", function () {
        modal.style.display = "flex";
    });

    // Ocultar popup cuando se presiona "Cancelar"
    cancelarBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Ocultar popup cuando se hace clic fuera
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Confirmar y enviar motivo de inactivación 
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
});
