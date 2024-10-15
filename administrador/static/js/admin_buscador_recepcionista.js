document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearButton');
    const filasPacientes = document.querySelectorAll('tbody tr:not(#no-coincidencias):not(.table-empty)');
    const mensajeError = document.getElementById('no-coincidencias');

    toggleClearButton();

    searchInput.addEventListener('input', function () {
        toggleClearButton();
    });

    clearButton.addEventListener('click', function () {
        searchInput.value = '';
        toggleClearButton();
        mostrarTodasLasFilas();
    });

    searchInput.addEventListener('keypress', verificarEnter);

    function toggleClearButton() {
        if (searchInput.value.trim() !== '') {
            clearButton.style.display = 'inline-block';
        } else {
            clearButton.style.display = 'none';
        }
    }

    function mostrarTodasLasFilas() {
        filasPacientes.forEach((fila) => {
            fila.style.display = ''; // Mostrar todas las filas
        });
        mensajeError.style.display = 'none'; // Ocultar mensaje de no coincidencias
    }

    function filtrarPacientes(event) {
        event.preventDefault();

        const searchValue = searchInput.value.toLowerCase();
        let bandera = false; // Bandera para saber si hay coincidencias

        filasPacientes.forEach((fila) => {
            const nombre_paciente = fila.cells[0].textContent.toLowerCase();
            const rut_paciente = fila.cells[1].textContent.toLowerCase();

            // Verificar si el nombre o el rut contiene el texto de búsqueda
            if (nombre_paciente.includes(searchValue) || rut_paciente.includes(searchValue)) {
                fila.style.display = ''; // Mostrar la fila que coincida
                bandera = true; // Si encontramos un resultado, actualizamos la bandera
            } else {
                fila.style.display = 'none'; // Ocultar la fila que no coincida
            }
        });

        if (!bandera && searchValue !== '') {
            mensajeError.style.display = 'table-row';
        } else {
            mensajeError.style.display = 'none';
        }
    }

    function verificarEnter(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            filtrarPacientes(event);
        }
    }
});
