// Navegación simulada
function navigate(route) {
    console.log("Navegando a", route);
}

// Función de cierre de sesión
function logout() {
    alert("Cerrar sesión");
    // Redirigir al login o cerrar sesión
    window.location.href = '/login';
}

// Lógica para crear un rol
document.getElementById("createRolForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const descripcion = document.getElementById("descripcion").value;
    
    const rolData = {
        descripcion: descripcion
    };
    
    try {
        const response = await fetch('/api/rols', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rolData)
        });

        if (response.ok) {
            document.getElementById("responseMessage").innerText = "Rol creado exitosamente";
        } else {
            const errorData = await response.json();
            document.getElementById("responseMessage").innerText = "Error al crear el rol: " + errorData.message;
        }
    } catch (error) {
        document.getElementById("responseMessage").innerText = "Error de conexión";
        console.error("Error al crear el rol:", error);
    }
});
