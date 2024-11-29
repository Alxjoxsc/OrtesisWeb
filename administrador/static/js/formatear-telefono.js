document.addEventListener('input', (e) => {
    const telefono = document.getElementById('id_telefono');
    const telefonoEmergencia = document.getElementById('id_telefono_emergencia');

    if (e.target === telefono || e.target === telefonoEmergencia) {
        const inputField = e.target;
        let cleaned = inputField.value.replace(/\D/g, ''); // Elimina todo lo que no sea número

        // Validar si es un número válido
        if (cleaned.startsWith('9') && cleaned.length <= 9) {
            // Aplicar formato solo si tiene exactamente 9 dígitos
            if (cleaned.length === 9) {
                inputField.value = cleaned.replace(/(\d{1})(\d{4})(\d{4})/, '$1 $2 $3');
            } else {
                inputField.value = cleaned; // Mostrar el número sin formatear mientras se escribe
            }
        } else if (cleaned.length > 9) {
            inputField.value = cleaned.slice(0, 9); // Limitar a 9 dígitos
        } else {
            inputField.value = cleaned; // Permitir que se siga escribiendo
        }
    }
});
