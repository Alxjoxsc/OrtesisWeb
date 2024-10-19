  document.addEventListener("DOMContentLoaded", function() {
    const btnDesplegable = document.getElementById('btnDesplegableRutina');
    const contenidoDesplegable = document.getElementById('contenidoDesplegableRutina');

    btnDesplegable.addEventListener('click', function() {
      contenidoDesplegable.classList.toggle('mostrar');
      this.querySelector('i').classList.toggle('fa-chevron-up');
      this.querySelector('i').classList.toggle('fa-chevron-down');
    });

    // Cerrar el desplegable si el usuario hace clic fuera de él
    window.onclick = function(event) {
      if (!event.target.matches('#btnDesplegableRutina')) {
        if (contenidoDesplegable.classList.contains('mostrar')) {
          contenidoDesplegable.classList.remove('mostrar');
          btnDesplegable.querySelector('i').classList.remove('fa-chevron-up');
          btnDesplegable.querySelector('i').classList.add('fa-chevron-down');
        }
      }
    }
  });

