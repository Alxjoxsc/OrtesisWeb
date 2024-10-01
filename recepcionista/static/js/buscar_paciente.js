document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearButton');

    // Verificar si el campo de búsqueda existe
    if (searchInput) {
        // Mostrar u ocultar el botón de limpiar dependiendo del contenido del campo de búsqueda
        toggleClearButton();

        // Asignar evento al botón de limpiar para que borre el texto y haga un submit del formulario
        clearButton.addEventListener('click', function() {
            clearSearch();
        });

        // Asignar evento para detectar cuando se presiona la tecla Enter y realizar la búsqueda
        searchInput.addEventListener('keydown', function(event) {
            detectEnter(event);
        });
    } else {
        console.error('El elemento con el ID searchInput no se encontró.');
    }
});

// Función para detectar la tecla Enter y realizar la búsqueda
function detectEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchPacientes();
    }
}

// Función para mostrar el botón de limpiar solo si hay texto en el campo de búsqueda
function toggleClearButton() {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearButton');

    if (searchInput.value.trim() !== '') {
        clearButton.style.display = 'inline-block';
    } else {
        clearButton.style.display = 'none';
    }
}

// Función para limpiar la búsqueda y enviar el formulario para volver a mostrar todos los pacientes
function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.value = '';  // Limpiar el campo de búsqueda
        toggleClearButton();  // Ocultar el botón de limpiar
        searchInput.form.submit();  // Enviar el formulario para recargar la lista completa de pacientes
    } else {
        console.error('El elemento con el ID searchInput no se encontró.');
    }
}

// Función para buscar pacientes dentro de la lista
function searchPacientes() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const pacientes = document.querySelectorAll('.paciente');
    let found = false;

    pacientes.forEach(paciente => {
        const nombre = paciente.querySelector('.nombre').textContent.toLowerCase();
        const rut = paciente.querySelector('.rut').textContent.toLowerCase();
        const tratamiento = paciente.querySelector('.tratamiento').textContent.toLowerCase();

        if (nombre.includes(input) || rut.includes(input) || tratamiento.includes(input)) {
            paciente.style.display = ''; // Mostrar el paciente
            found = true;
        } else {
            paciente.style.display = 'none'; // Ocultar el paciente
        }
    });

    if (!found) {
        console.log('No se encontraron pacientes.');
    }
}
