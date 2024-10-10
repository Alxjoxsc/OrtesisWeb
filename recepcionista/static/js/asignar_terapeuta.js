let redirectUrl; // Variable para almacenar la URL de redirección

// Función para mostrar el popup con los datos del paciente y terapeuta
window.mostrarPopUpAsignarTerapeuta = function(pacienteId, nombrePaciente, apellidoPaciente, terapeutaId, nombreTerapeuta, apellidoTerapeuta, url) {
    const mensaje = `¿Confirma la asignación del terapeuta ${nombreTerapeuta} ${apellidoTerapeuta} al paciente ${nombrePaciente} ${apellidoPaciente}?`;

    document.getElementById('popup-mensaje').textContent = mensaje;
    document.getElementById('popupModal').style.display = 'block';

    // Almacena la URL con los parámetros en la variable redirectUrl
    redirectUrl = url.replace('paciente_id', pacienteId).replace('terapeuta_id', terapeutaId);
};

// Función para cerrar el popup
window.cerrarPopUp = function() {
    document.getElementById('popupModal').style.display = 'none';
};

// Función para manejar la confirmación
document.getElementById('confirmButton').onclick = function() {
    // Redirige a la URL almacenada con los IDs correspondientes
    if (redirectUrl) {
        window.location.href = redirectUrl;
    } else {
        console.error('No se ha definido una URL de redirección.');
    }
};
