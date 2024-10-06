document.addEventListener("DOMContentLoaded", function() {
    const pesoInput = document.getElementById("id_peso");
    const alturaInput = document.getElementById("id_altura");

    const validateDecimal = (event) => {
        const input = event.target;
        const value = input.value;
        
        // Expresión regular para validar dos decimales
        const regex = /^\d+(\.\d{0,2})?$/;

        // Si el valor no coincide con la expresión regular, eliminar el último carácter
        if (!regex.test(value) && value !== "") {
            input.value = value.slice(0, -1);
        }

        // Validar límites para peso y altura
        if (input === pesoInput) {
            // Convertir a número y verificar límite
            const pesoValue = parseFloat(value);
            if (pesoValue > 700) {
                input.value = 700; // Limitar a 700
            }
        }

        if (input === alturaInput) {
            // Convertir a número y verificar límite
            const alturaValue = parseFloat(value);
            if (alturaValue > 3) {
                input.value = 3; // Limitar a 3
            }
        }
    };

    // Agregar evento de entrada a los campos de peso y altura
    if (pesoInput) {
        pesoInput.addEventListener("input", validateDecimal);
    }

    if (alturaInput) {
        alturaInput.addEventListener("input", validateDecimal);
    }
});