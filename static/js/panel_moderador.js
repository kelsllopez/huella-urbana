// ========================================
// INICIALIZAR FILTROS DESDE LA URL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    // Leer parámetros de la URL
    const urlParams = new URLSearchParams(window.location.search);
    
    // Restaurar estado de filtros
    currentFilters.status = urlParams.get('estado') || 'pendiente';
    currentFilters.severity = urlParams.get('gravedad') || 'all';
    currentFilters.animal = urlParams.get('animal') || 'all';
    currentFilters.anonymous = urlParams.get('anonimo') || 'all';
    
    // Actualizar UI de los filtros
    updateFilterUI();
});

// Cerrar dropdowns al hacer clic fuera
document.addEventListener('click', (e) => {
    if (!e.target.closest('.filter-dropdown')) {
        document.querySelectorAll('.filter-dropdown').forEach(d => d.classList.remove('open'));
    }
});

// Toggle dropdown
function toggleFilter(id) {
    const dropdown = document.getElementById(id);
    const wasOpen = dropdown.classList.contains('open');
    
    document.querySelectorAll('.filter-dropdown').forEach(d => d.classList.remove('open'));
    
    if (!wasOpen) dropdown.classList.add('open');
}

// Filtros activos
let currentFilters = {
    status: 'pendiente',
    severity: 'all',
    animal: 'all',
    anonymous: 'all'
};

// Mapeo de valores para los labels
const filterLabels = {
    status: {
        'pendiente': { label: 'Pendientes', icon: 'fa-clock' },
        'aprobado': { label: 'Aprobados', icon: 'fa-check-circle' },
        'rechazado': { label: 'Rechazados', icon: 'fa-times-circle' },
        'all': { label: 'Todos los estados', icon: 'fa-list' }
    },
    severity: {
        'grave': { label: 'Graves', icon: 'fa-exclamation-triangle' },
        'moderado': { label: 'Moderados', icon: 'fa-exclamation-circle' },
        'leve': { label: 'Leves', icon: 'fa-info-circle' },
        'all': { label: 'Todas las gravedades', icon: 'fa-list' }
    },
    animal: {
        'perro': { label: 'Perros', icon: 'fa-dog' },
        'gato': { label: 'Gatos', icon: 'fa-cat' },
        'otro': { label: 'Otros', icon: 'fa-paw' },
        'all': { label: 'Todos los animales', icon: 'fa-list' }
    },
    anonymous: {
        'true': { label: 'Sí (Anónimo)', icon: 'fa-user-secret' },
        'false': { label: 'No (Con datos)', icon: 'fa-user' },
        'all': { label: 'Todos', icon: 'fa-list' }
    }
};

// Actualizar la UI de los filtros según el estado actual
function updateFilterUI() {
    // Actualizar cada dropdown
    updateDropdownUI('statusFilter', 'status', currentFilters.status);
    updateDropdownUI('severityFilter', 'severity', currentFilters.severity);
    updateDropdownUI('animalFilter', 'animal', currentFilters.animal);
    updateDropdownUI('anonymousFilter', 'anonymous', currentFilters.anonymous);
}

// Actualizar un dropdown específico
function updateDropdownUI(dropdownId, filterType, value) {
    const dropdown = document.getElementById(dropdownId);
    const button = dropdown.querySelector('.filter-btn');
    const config = filterLabels[filterType][value];
    
    if (config) {
        button.querySelector('.filter-btn-content').innerHTML = `
            <i class="fas ${config.icon}"></i>
            ${config.label}
        `;
        
        // Marcar como activo si no es 'all'
        if (value !== 'all') {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    }
    
    // Actualizar opciones seleccionadas
    dropdown.querySelectorAll('.filter-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    
    const dataAttr = `data-${filterType}`;
    const selectedOption = dropdown.querySelector(`[${dataAttr}="${value}"]`);
    if (selectedOption) {
        selectedOption.classList.add('selected');
    }
}

// Seleccionar filtro
function selectFilter(type, value, label, icon) {
    currentFilters[type] = value;
    
    const dropdown = document.getElementById(type + 'Filter');
    const button = dropdown.querySelector('.filter-btn');
    
    button.querySelector('.filter-btn-content').innerHTML = `
        <i class="fas ${icon}"></i>
        ${label}
    `;
    
    // Agregar/quitar clase active
    if (value !== 'all') {
        button.classList.add('active');
    } else {
        button.classList.remove('active');
    }
    
    dropdown.querySelectorAll('.filter-option').forEach(opt => opt.classList.remove('selected'));
    dropdown.querySelector(`[data-${type}="${value}"]`).classList.add('selected');
    
    dropdown.classList.remove('open');
    
    applyFilters();
}

// Aplicar filtros (recarga la página con los parámetros correctos)
function applyFilters() {
    const params = new URLSearchParams();
    
    // Agregar filtros activos (solo los que no son 'all')
    if (currentFilters.status !== 'all') {
        params.set('estado', currentFilters.status);
    }
    
    if (currentFilters.severity !== 'all') {
        params.set('gravedad', currentFilters.severity);
    }
    
    if (currentFilters.animal !== 'all') {
        params.set('animal', currentFilters.animal);
    }
    
    if (currentFilters.anonymous !== 'all') {
        params.set('anonimo', currentFilters.anonymous);
    }
    
    // Redirigir con los nuevos parámetros
    window.location.search = params.toString();
}

// Cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Aprobar
function aprobar(id) {
    Swal.fire({
        title: "¿Aprobar este reporte?",
        text: "El reporte será publicado en el mapa público.",
        icon: "question",
        showCancelButton: true,
        confirmButtonColor: "#10B981",
        cancelButtonColor: "#6B7280",
        confirmButtonText: '<i class="fas fa-check"></i> Sí, aprobar',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/aprobar/${id}/`)
                .then(res => res.json())
                .then(data => Swal.fire({
                    title: "¡Aprobado!",
                    text: data.mensaje,
                    icon: "success",
                    confirmButtonColor: "#8B5CF6"
                }).then(() => location.reload()));
        }
    });
}

// Rechazar
function rechazar(id) {
    Swal.fire({
        title: "¿Rechazar este reporte?",
        input: "textarea",
        inputLabel: "Motivo del rechazo (obligatorio)",
        inputPlaceholder: "Escribe el motivo...",
        showCancelButton: true,
        confirmButtonColor: "#EF4444",
        cancelButtonColor: "#6B7280",
        confirmButtonText: '<i class="fas fa-times"></i> Rechazar',
        cancelButtonText: 'Cancelar',
        inputValidator: v => !v && "Debes ingresar un motivo"
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/rechazar/${id}/`, {
                method: "POST",
                headers: {"X-CSRFToken": getCookie("csrftoken")},
                body: new URLSearchParams({motivo: result.value})
            })
                .then(res => res.json())
                .then(data => Swal.fire({
                    title: "Rechazado",
                    text: data.mensaje,
                    icon: "info",
                    confirmButtonColor: "#8B5CF6"
                }).then(() => location.reload()));
        }
    });
}

// Función global para cambiar de pestaña
function switchTab(event, tabId) {
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}

// Ver detalles del reporte
function verDetalles(id) {
    fetch(`/detalles/${id}/`)
        .then(res => res.json())
        .then(data => {
            const template = document.getElementById('modalDetallesTemplate');
            const modalHTML = template.innerHTML;
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = modalHTML;

            // TÍTULO Y FECHA
            tempDiv.querySelector('#modal-titulo').textContent = data.titulo || 'Sin título';
            tempDiv.querySelector('#modal-fecha').textContent = `${data.fecha} ${data.hora ? '- ' + data.hora : ''}`;

            // INFORMACIÓN DEL INCIDENTE
            tempDiv.querySelector('#modal-tipo-animal').textContent = data.tipo_animal || "No especificado";
            tempDiv.querySelector('#modal-cantidad-perros').textContent = data.cantidad_perros || "Sin dato";
            tempDiv.querySelector('#modal-gravedad').textContent = data.gravedad || "Sin dato";
            tempDiv.querySelector('#modal-direccion').textContent = data.direccion || "No indicada";

            // DATOS DEL REPORTANTE
            tempDiv.querySelector('#modal-nombre').textContent = 
                data.nombre_reportante && data.nombre_reportante.trim() !== "" ? data.nombre_reportante : "Anónimo";
            tempDiv.querySelector('#modal-email').textContent = 
                data.email_reportante && data.email_reportante.trim() !== "" ? data.email_reportante : "No proporcionado";
            tempDiv.querySelector('#modal-telefono').textContent = 
                data.telefono_reportante && data.telefono_reportante.trim() !== "" ? data.telefono_reportante : "No proporcionado";
            tempDiv.querySelector('#modal-anonimo').textContent = data.anonimo ? "Sí" : "No";
            tempDiv.querySelector('#modal-usuario').textContent = data.usuario ? data.usuario : "No asociado";

            // UBICACIÓN
            tempDiv.querySelector('#modal-sector').textContent = data.sector || "No especificado";
            tempDiv.querySelector('#modal-direccion-ubicacion').textContent = data.direccion || "No indicada";
            tempDiv.querySelector('#modal-coordenadas').textContent = 
                data.latitud && data.longitud ? `${data.latitud}, ${data.longitud}` : "Sin coordenadas";
            tempDiv.querySelector('#modal-map-link').href = 
                data.latitud && data.longitud ? `https://www.google.com/maps?q=${data.latitud},${data.longitud}` : "#";

            // DESCRIPCIÓN
            tempDiv.querySelector('#modal-descripcion').textContent = 
                data.descripcion && data.descripcion.trim() !== "" ? data.descripcion : "Sin descripción proporcionada";

            // MOSTRAR MODAL
            Swal.fire({
                html: tempDiv.innerHTML,
                showConfirmButton: true,
                confirmButtonText: '<i class="fas fa-times"></i> Cerrar',
                confirmButtonColor: "#8B5CF6",
                showCloseButton: true,
                width: "90%",
                padding: "0",
                customClass: {
                    popup: "swal-detalles"
                }
            });
        });
}

// Ver foto ampliada
function showImageModal(src) {
    Swal.fire({
        imageUrl: src,
        imageAlt: 'Evidencia fotográfica',
        showConfirmButton: false,
        showCloseButton: true,
        width: "900px",
        background: '#000',
        backdrop: 'rgba(0,0,0,0.9)'
    });
}