document.addEventListener("DOMContentLoaded", function() {
    const btnAnadir = document.querySelector(".btn-anadir");
    const popup = document.getElementById("popup");
    const closePopup = document.getElementById("close-popup");
    const btnCancelar = document.getElementById("btn-cancelar");

    // Evento para abrir el popup al hacer clic en "Añadir Observación"
    btnAnadir.addEventListener("click", function() {
        popup.style.display = "block";
    });

    // Cerrar popup de añadir
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

    // Delegación de eventos para edición y eliminación
    document.addEventListener('click', function(event) {
        // Abrir popup de edición
        if (event.target.classList.contains('editar-observacion')) {
            const observacionId = event.target.getAttribute('data-id');
            const observacionTexto = event.target.closest('.observacion-card').querySelector('p').innerText;

            document.getElementById('edit-contenido-observacion').value = observacionTexto;
            document.getElementById('edit-observacion-form').action = `/editar-observacion/${observacionId}/`;

            document.getElementById('edit-popup').style.display = 'block';
        }

        // Abrir popup de eliminación
        if (event.target.classList.contains('eliminar-observacion')) {
            popupEliminar.style.display = 'block';
            observacionIdEliminar = event.target.getAttribute('data-id');
        }
    });

    // Cerrar popup de edición
    document.getElementById('close-edit-popup').addEventListener('click', function() {
        document.getElementById('edit-popup').style.display = 'none';
    });

    document.getElementById('cancel-edit').addEventListener('click', function() {
        document.getElementById('edit-popup').style.display = 'none';
    });

    // Variables para gestionar la eliminación de observaciones
    const popupEliminar = document.getElementById('popup-eliminar');
    const closeEliminarBtn = document.getElementById('close-popup-eliminar');
    const cancelarEliminarBtn = document.getElementById('cancelar-eliminar');
    const confirmarEliminarBtn = document.getElementById('confirmar-eliminar');

    // Obtener el token CSRF
    const csrftoken = getCookie('csrftoken');

    // Cerrar popup de eliminación
    closeEliminarBtn.addEventListener('click', () => {
        popupEliminar.style.display = 'none';
    });

    cancelarEliminarBtn.addEventListener('click', () => {
        popupEliminar.style.display = 'none';
    });

    // Confirmar eliminación
    confirmarEliminarBtn.addEventListener('click', () => {
        if (observacionIdEliminar) {
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

    // Buscar observaciones por palabras clave
    document.querySelector('.busca-observaciones').addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const observacionCards = document.querySelectorAll('.observacion-card');

        observacionCards.forEach(function(card) {
            const observacionText = card.querySelector('p').innerText.toLowerCase();
            const fechaText = card.querySelector('h3').innerText.toLowerCase();

            if (observacionText.includes(searchTerm) || fechaText.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// Función para obtener el token CSRF
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
