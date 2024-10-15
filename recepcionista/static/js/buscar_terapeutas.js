function toggleClearButton() {
    const searchBar = document.getElementById('searchBar');
    const clearButton = document.getElementById('clearButton');
    clearButton.style.display = searchBar.value ? 'inline-block' : 'none';
}

function clearSearch() {
    document.getElementById('searchBar').value = '';
    document.getElementById('searchBar').parentNode.submit();
}

function toggleDropdown() {
    document.getElementById("dropdownMenu").classList.toggle("show");
}

