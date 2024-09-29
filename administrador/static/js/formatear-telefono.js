document.addEventListener('input', (e) => {
    const telefono = document.getElementById('id_telefono');
    if (e.target === telefono) {
        let telefonoFormateado = formatPhoneNumber(telefono.value);
        telefono.value = telefonoFormateado;
    }
});

function formatPhoneNumber(phoneNumber) {
    // Sacar todos los caracteres que no sean números
    let cleaned = phoneNumber.toString().replace(/\D/g, '');
    
    // Eliminar el prefijo '56' si existe
    if (cleaned.startsWith('56')) {
        cleaned = cleaned.slice(2);
    }

    // Si empieza con '9' y tiene exactamente 9 dígitos, aplicar el formato '9 1234 5678'
    if (cleaned.startsWith('9') && cleaned.length === 9) {
        const formatted = cleaned.replace(/(\d{1})(\d{4})(\d{4})/, '$1 $2 $3');
        return formatted;
    } else if (cleaned.length > 9) {
        return ''; // Si el número tiene más de 9 dígitos, limpiar el campo
    }

    return cleaned; // Retornar los números sin formatear si no cumple con las condiciones
}
