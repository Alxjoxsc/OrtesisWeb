document.addEventListener("DOMContentLoaded", function() {
    const btnAnadir = document.querySelector(".btn-anadir");
    const popup = document.getElementById("popup");
    const closePopup = document.getElementById("close-popup");
    const btnCancelar = document.getElementById("btn-cancelar");

    // Evento para abrir el popup al hacer clic en "Añadir Observación"
    btnAnadir.addEventListener("click", function() {
        popup.style.display = "block"; // Muestra el popup
    });

    //Cerrar popup
    closePopup.addEventListener("click", function() {
        popup.style.display = "none";
    });

    btnCancelar.addEventListener("click", function() {
        popup.style.display = "none"; 
    });

    window.addEventListener("click", function(event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    });
});

// Funcionalidad para abrir el popup de edición y cargar datos de la observación
document.querySelectorAll('.editar-observacion').forEach(function(editBtn) {
    editBtn.addEventListener('click', function() {
        var observacionId = this.dataset.id; // Obtener el ID de la observación
        var observacionTexto = this.closest('.observacion-card').querySelector('p').innerText;

        // Precargar el textarea con el contenido de la observación
        document.getElementById('edit-contenido-observacion').value = observacionTexto;

        // Establecer la acción del formulario para que envíe la solicitud al servidor
        document.getElementById('edit-observacion-form').action = '/editar-observacion/' + observacionId + '/';

        // Mostrar el popup de edición
        document.getElementById('edit-popup').style.display = 'block';
    });
});

// Cerrar el popup de edición
document.getElementById('close-edit-popup').addEventListener('click', function() {
    document.getElementById('edit-popup').style.display = 'none'; // Oculta el popup de edición
});

document.getElementById('cancel-edit').addEventListener('click', function() {
    document.getElementById('edit-popup').style.display = 'none'; // Oculta el popup de edición
});

// Variables para gestionar la eliminación de observaciones
const iconosEliminar = document.querySelectorAll('.eliminar-observacion');
const popupEliminar = document.getElementById('popup-eliminar');
const closeEliminarBtn = document.getElementById('close-popup-eliminar');
const cancelarEliminarBtn = document.getElementById('cancelar-eliminar');
const confirmarEliminarBtn = document.getElementById('confirmar-eliminar');

// Almacenar el ID de la observación a eliminar
let observacionIdEliminar = null;

// Función para obtener el CSRF token del documento
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken'); // Obtener el token CSRF

// Abrir el popup de eliminación al hacer clic en el ícono de eliminar
iconosEliminar.forEach((icono) => {
    icono.addEventListener('click', function() {
        popupEliminar.style.display = 'block';
        observacionIdEliminar = this.getAttribute('data-id');
    });
});

// Cerrar el popup de eliminación
closeEliminarBtn.addEventListener('click', () => {
    popupEliminar.style.display = 'none';
});

cancelarEliminarBtn.addEventListener('click', () => {
    popupEliminar.style.display = 'none';
});

// Confirmar eliminación y realizar la solicitud al servidor
confirmarEliminarBtn.addEventListener('click', () => {
    if (observacionIdEliminar) {
        // Realiza la petición para eliminar la observación usando fetch
        fetch(`/eliminar_observacion/${observacionIdEliminar}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error('Error al eliminar la observación');
            }
        });
    }
});

// Evento para buscar observaciones por palabras clave
document.querySelector('.busca-observaciones').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase(); // Obtener el texto de búsqueda y convertirlo a minúsculas
    const observacionCards = document.querySelectorAll('.observacion-card'); // Obtener todas las tarjetas de observación

    observacionCards.forEach(function(card) {
        const observacionText = card.querySelector('p').innerText.toLowerCase(); // Obtener el texto de la observación en minúsculas
        const fechaText = card.querySelector('h3').innerText.toLowerCase(); // Obtener el texto de la fecha en minúsculas

        // Comprobar si el texto de búsqueda está presente en el texto de la observación o en la fecha
        if (observacionText.includes(searchTerm) || fechaText.includes(searchTerm)) {
            card.style.display = ''; // Mostrar la tarjeta si hay una coincidencia
        } else {
            card.style.display = 'none'; // Ocultar la tarjeta si no hay coincidencia
        }
    });
});