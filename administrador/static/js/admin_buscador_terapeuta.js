function detectEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchTerapeutas();
        
    }
}

function searchTerapeutas() {
    const input = document.getElementById('searchBar').value.toLowerCase();
    const terapeutas = document.querySelectorAll('.terapeuta');
    let found = false;

    terapeutas.forEach(terapeuta => {
        const nombre = terapeuta.querySelector('.centro-tabla:nth-child(2)').textContent.toLowerCase();
        const rut = terapeuta.querySelector('.centro-tabla:nth-child(3)').textContent.toLowerCase();
        const especialidad = terapeuta.querySelector('.centro-tabla:nth-child(5)').textContent.toLowerCase(); // Nombre del especialidad

        if (nombre.includes(input) || rut.includes(input) || especialidad.includes(input)) {
            terapeuta.style.display = ''; // Mostrar el terapeuta
            found = true;
        } else {
            terapeuta.style.display = 'none'; // Ocultar el terapeuta
        }
    });

    if (!found) {
        console.log('No se encontraron terapeutas.');
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
    
    // Enviar el formulario para mostrar todos los terapeutas de nuevo
    searchBar.form.submit();
}

