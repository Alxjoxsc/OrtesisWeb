// Función para detectar la tecla Enter y activar la búsqueda
function detectEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchPacientes();
    }
}

// Función para buscar pacientes según el nombre, RUT o terapeuta
function searchPacientes() {
    const input = document.getElementById('searchBar').value.trim().toLowerCase();
    const pacientes = document.querySelectorAll('.paciente');
    let found = false;

    pacientes.forEach(paciente => {
        const nombre = paciente.querySelector('.nombre').textContent.toLowerCase();
        const rut = paciente.querySelector('.rut').textContent.toLowerCase();
        const terapeuta = paciente.querySelector('.centro-tabla:nth-child(5)').textContent.toLowerCase(); // Nombre del terapeuta

        const matches = [nombre, rut, terapeuta].some(field => field.includes(input));

        paciente.style.display = matches ? '' : 'none'; // Mostrar u ocultar paciente
        if (matches) found = true;
    });

    if (!found && input !== '') {
        console.log('No se encontraron pacientes.');
    }
}

// Función para mostrar el botón de limpiar si hay texto en el campo de búsqueda
function toggleClearButton() {
    const searchBar = document.getElementById('searchBar');
    const clearButton = document.getElementById('clearButton');

    clearButton.style.display = searchBar.value.trim() ? 'inline-block' : 'none';
}

// Función para limpiar el campo de búsqueda y mostrar todos los pacientes
function clearSearch() {
    const searchBar = document.getElementById('searchBar');
    searchBar.value = '';

    const clearButton = document.getElementById('clearButton');
    clearButton.style.display = 'none';

    searchPacientes(); // Mostrar todos los pacientes al limpiar el filtro
}
