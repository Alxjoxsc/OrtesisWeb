function openPopup() {
    document.getElementById("overlay").style.display = "block";
}

// Función para cerrar el popup y limpiar el archivo cargado
document.getElementById("closePopup").onclick = function(event) {
    event.preventDefault();
    document.getElementById("overlay").style.display = "none";

    // Limpiar el archivo cargado
    document.getElementById('archivo_csv').value = ""; // Limpia el archivo del input
    document.getElementById('dropzone-message').textContent = "Arrastra tu archivo o haz click para buscar en tu computador";
    
    // Remover clase de estilo temporal
    dropzone.classList.remove("file-loaded");
};

var dropzone = document.getElementById('dropzone');
dropzone.ondragover = function() {
    this.classList.add("drag-hover");  // Agregar una clase temporal para el estilo de arrastre
    return false;
};

dropzone.ondragleave = function() {
    this.classList.remove("drag-hover");  // Quitar la clase de arrastre al salir
    return false;
};

dropzone.ondrop = function(e) {
    e.preventDefault();
    document.getElementById('archivo_csv').files = e.dataTransfer.files;

    // Cambiar el mensaje y aplicar clase si hay un archivo cargado
    if (e.dataTransfer.files.length > 0) {
        var fileName = e.dataTransfer.files[0].name;
        document.getElementById('dropzone-message').textContent = "Archivo cargado: " + fileName;
        this.classList.add("file-loaded");  // Agregar clase indicando que hay un archivo cargado
        this.classList.remove("drag-hover");  // Remover el estilo de arrastre
    }
};

document.getElementById('archivo_csv').onchange = function() {
    if (this.files.length > 0) {
        var fileName = this.files[0].name;
        document.getElementById('dropzone-message').textContent = "Archivo cargado: " + fileName;
        dropzone.classList.add("file-loaded");  // Agregar clase indicando que hay un archivo cargado
    } else {
        document.getElementById('dropzone-message').textContent = "Arrastra tu archivo o haz click para buscar en tu computador";
        dropzone.classList.remove("file-loaded");  // Remover la clase si se borra el archivo
    }
};
