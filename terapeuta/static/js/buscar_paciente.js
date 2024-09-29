function detectEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchPacientes();
        
    }
}

function searchPacientes() {
    const input = document.getElementById('searchBar').value.toLowerCase();
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

function toggleClearButton() {
    const searchBar = document.getElementById('searchBar');
    const clearButton = document.getElementById('clearButton');

    // Mostrar el botón de "Limpiar filtro" solo si hay texto en el campo de búsqueda
    if (searchBar.value.trim() !== '') {
        clearButton.style.display = 'inline-block';
    } else {
        clearButton.style.display = 'none';
    }
}

function clearSearch() {
    // Limpiar el campo de búsqueda
    const searchBar = document.getElementById('searchBar');
    searchBar.value = '';
    
    // Ocultar el botón de "Limpiar filtro"
    const clearButton = document.getElementById('clearButton');
    clearButton.style.display = 'none';
    
    // Enviar el formulario para mostrar todos los pacientes de nuevo
    searchBar.form.submit();
}

