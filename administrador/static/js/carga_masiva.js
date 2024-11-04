
function openPopup() {
    document.getElementById("popup").style.display = "block";
    document.getElementById("overlay").style.display = "block";
}

document.getElementById("closePopup").onclick = function(event) {
    event.preventDefault();
    document.getElementById("popup").style.display = "none";
    document.getElementById("overlay").style.display = "none";
}


var dropzone = document.getElementById('dropzone');
dropzone.ondragover = function() {
    this.style.backgroundColor = '#ccc';
    return false;
};
dropzone.ondragleave = function() {
    this.style.backgroundColor = 'transparent';
    return false;
};
dropzone.ondrop = function(e) {
    e.preventDefault();
    document.getElementById('archivo_csv').files = e.dataTransfer.files;
    this.style.backgroundColor = 'transparent';
};


document.getElementById('archivo_csv').onchange = function() {
    if (this.value) {
        document.getElementById('dropzone-message').textContent = "Archivo cargado";
    } else {
        document.getElementById('dropzone-message').textContent = "Arrastra tu archivo o haz click para buscar en tu computador";
    }
};