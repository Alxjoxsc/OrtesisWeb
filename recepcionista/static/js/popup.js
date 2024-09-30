let redirectUrl; // Variable para almacenar la URL

window.mostrarPopUpAsignarTerapeuta = function(pacienteId, nombre, rut, terapeuta, url) {
    const titulo = `Asignar Terapeuta a ${nombre}`;
    const mensaje = `¿Confirma la asignación del terapeuta ${terapeuta} al paciente ${nombre} (${rut})?`;

    document.getElementById('popup-titulo').textContent = titulo;
    document.getElementById('popup-mensaje').textContent = mensaje;
    document.getElementById('popupModal').style.display = 'block';

    // Almacena la URL en la variable
    redirectUrl = url;

    document.getElementById('confirmButton').setAttribute('data-estado', 'inactivo');
    document.getElementById('confirmButton').setAttribute('data-ids', JSON.stringify([pacienteId]));
};

// Función para manejar la confirmación
document.getElementById('confirmButton').onclick = function() {
    // Redirige a la URL almacenada
    window.location.href = redirectUrl;
};
