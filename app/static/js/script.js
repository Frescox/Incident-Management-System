document.addEventListener("DOMContentLoaded", function() {
    const incidentList = document.getElementById("incident-list");
    const incidentForm = document.getElementById("incident-form");

    // Simula una base de datos de incidencias
    let incidents = [
        { id: 1, titulo: "Incidencia 1", descripcion: "Descripción de la incidencia 1" },
        { id: 2, titulo: "Incidencia 2", descripcion: "Descripción de la incidencia 2" },
    ];

    // Función para mostrar las incidencias
    function displayIncidents() {
        incidentList.innerHTML = ""; // Limpiar la lista antes de actualizar
        incidents.forEach(incident => {
            const li = document.createElement("li");
            li.innerHTML = `<strong>${incident.titulo}</strong>: ${incident.descripcion}`;
            incidentList.appendChild(li);
        });
    }

    // Mostrar las incidencias cuando se carga la página
    displayIncidents();

    // Manejo del formulario para añadir una nueva incidencia
    incidentForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevenir el envío del formulario

        const titulo = document.getElementById("titulo").value;
        const descripcion = document.getElementById("descripcion").value;

        if (titulo && descripcion) {
            const newIncident = {
                id: incidents.length + 1,
                titulo: titulo,
                descripcion: descripcion
            };

            incidents.push(newIncident); // Añadir nueva incidencia
            displayIncidents(); // Actualizar la lista

            // Limpiar el formulario
            document.getElementById("titulo").value = "";
            document.getElementById("descripcion").value = "";
        }
    });
});
