// Mostrar/ocultar opciones del filtro
const dropdownButton = document.getElementById('dropdownMenuButton');
const filterOptions = document.getElementById('filterOptions');
const arrow = document.getElementById('arrow');

dropdownButton.addEventListener('click', () => {
    filterOptions.style.display = filterOptions.style.display === 'none' ? 'block' : 'none';
    arrow.textContent = arrow.textContent === '▼' ? '▲' : '▼';
});

// Aplicar el filtro cuando se selecciona una opción
function applyFilter(orderBy) {
    const urlParams = new URLSearchParams(window.location.search);

    // Mantener el valor de búsqueda si está presente
    const searchQuery = urlParams.get('search');
    if (searchQuery) {
        urlParams.set('search', searchQuery);
    }
    
    urlParams.set('order_by', orderBy);
    window.location.search = urlParams.toString();
}

// Limpiar el filtro de orden
function clearOrderFilter() {
    const urlParams = new URLSearchParams(window.location.search);

    // Mantener el valor de búsqueda si está presente
    const searchQuery = urlParams.get('search');
    if (searchQuery) {
        urlParams.set('search', searchQuery);
    }

    urlParams.delete('order_by');
    window.location.search = urlParams.toString();
}