function detectEnter(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchRecepcionistas();
        
    }
}

function searchRecepcionistas() {
    const input = document.getElementById('searchBar').value.toLowerCase();
    const recepcionistas = document.querySelectorAll('.recepcionista');
    let found = false;

    recepcionistas.forEach(recepcionista => {
        const nombre = recepcionista.querySelector('.centro-tabla:nth-child(2)').textContent.toLowerCase();
        const rut = recepcionista.querySelector('.centro-tabla:nth-child(3)').textContent.toLowerCase();

        if (nombre.includes(input) || rut.includes(input)) {
            recepcionista.style.display = ''; // Mostrar el recepcionista
            found = true;
        } else {
            recepcionista.style.display = 'none'; // Ocultar el recepcionista
        }
    });

    if (!found) {
        console.log('No se encontraron recepcionistas.');
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
    
    // Enviar el formulario para mostrar todos los recepcionistas de nuevo
    searchBar.form.submit();
}

