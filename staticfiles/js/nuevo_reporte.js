/* ========================= CONFIG DEBUG ========================= */
const DEBUG = true;
const log = (m, d = null) => {
    if (DEBUG) console.log(`🐕 [REPORTE] ${m}`, d ?? '');
};

let currentStep = 1;
const totalSteps = 3;
let map, marker;
let previewFiles = [];

/* ========================= INICIO ========================= */
document.addEventListener('DOMContentLoaded', () => {
    log('Página cargada');

    const gravedadField = document.getElementById('id_gravedad');
    const fileInput = document.getElementById('fileInput');
    const fechaField = document.getElementById('id_fecha');

    log('Form IDs:', {
        gravedad: !!gravedadField,
        lat: !!document.getElementById('id_latitud'),
        lng: !!document.getElementById('id_longitud'),
        anonimo: !!document.getElementById('id_anonimo'),
        fileInput: !!fileInput,
        fecha: !!fechaField
    });

    if (gravedadField && gravedadField.value) paintSeverity(gravedadField.value);

    updateCharCounter();

    if (fechaField) {
        const today = new Date().toISOString().split('T')[0];
        fechaField.setAttribute('max', today);
        fechaField.addEventListener('change', validateDate);
    }
});

/* ========================= VALIDACIÓN DE FECHA ========================= */
function validateDate() {
    const fechaField = document.getElementById('id_fecha');
    const dateWarning = document.getElementById('dateWarning');
    if (!fechaField || !dateWarning) return;

    const selectedDate = new Date(fechaField.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate > today) {
        dateWarning.style.display = 'flex';
        fechaField.style.borderColor = 'var(--color-danger)';
        fechaField.value = '';
    } else {
        dateWarning.style.display = 'none';
        fechaField.style.borderColor = 'var(--color-border)';
    }
}

/* ========================= NAVEGACIÓN ========================= */
document.addEventListener("DOMContentLoaded", () => {
    const btnNext = document.getElementById('btnNext');
    const btnPrev = document.getElementById('btnPrev');

    if (btnNext) {
        btnNext.addEventListener('click', () => {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateSteps();
                }
            }
        });
    }

    if (btnPrev) {
        btnPrev.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                updateSteps();
            }
        });
    }
});

function updateSteps() {
    document.querySelectorAll('.step').forEach((step, idx) => {
        const n = idx + 1;
        step.classList.remove('active', 'completed');
        if (n < currentStep) step.classList.add('completed');
        else if (n === currentStep) step.classList.add('active');
    });

    document.querySelectorAll('.step-content').forEach(c => c.classList.remove('active'));
    document.querySelector(`.step-content[data-step="${currentStep}"]`)
        .classList.add('active');

    document.getElementById('btnPrev').style.display = currentStep === 1 ? 'none' : 'block';
    document.getElementById('btnNext').style.display = currentStep === totalSteps ? 'none' : 'block';
    document.getElementById('btnSubmit').style.display = currentStep === totalSteps ? 'block' : 'none';

    if (currentStep === 2 && !map) setTimeout(initMap, 100);

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ========================= VALIDACIONES POR PASO ========================= */
function validateStep(step) {
    if (step === 1) {
        const titulo = document.getElementById('id_titulo')?.value.trim() || '';
        const fecha = document.getElementById('id_fecha')?.value || '';
        const tipo = document.getElementById('id_tipo_animal')?.value || '';
        const gravedad = document.getElementById('id_gravedad')?.value || '';
        const desc = document.getElementById('id_descripcion')?.value.trim() || '';

        if (fecha) {
            const selectedDate = new Date(fecha);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (selectedDate > today) {
                Swal.fire({
                    icon: 'error',
                    title: 'Fecha inválida',
                    text: 'No puedes seleccionar una fecha futura.',
                    confirmButtonColor: '#EF4444'
                });
                return false;
            }
        }

        if (!titulo || !fecha || !tipo || !gravedad || desc.length < 50) {
            Swal.fire({
                icon: 'warning',
                title: 'Completa los campos obligatorios',
                confirmButtonColor: '#8B5CF6'
            });
            return false;
        }
    }

    if (step === 2) {
        const lat = document.getElementById('id_latitud')?.value;
        const lng = document.getElementById('id_longitud')?.value;

        if (!lat || !lng) {
            Swal.fire({
                icon: 'info',
                title: 'Selecciona la ubicación',
                text: 'Haz clic en el mapa para marcar el lugar del incidente.',
                confirmButtonColor: '#8B5CF6'
            });
            return false;
        }
    }

    return true;
}

/* ========================= MAPA ========================= */
function initMap() {
    const latField = document.getElementById('id_latitud');
    const lngField = document.getElementById('id_longitud');

    const lat = parseFloat(latField?.value) || -39.8142;
    const lng = parseFloat(lngField?.value) || -73.2459;

    map = L.map('map').setView([lat, lng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    if (latField?.value && lngField?.value) {
        marker = L.marker([lat, lng]).addTo(map);
        document.getElementById('locationInfo').style.display = 'block';
        document.getElementById('lat').textContent = lat.toFixed(6);
        document.getElementById('lng').textContent = lng.toFixed(6);
    }

    map.on('click', (e) => {
        if (marker) map.removeLayer(marker);
        marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);

        latField.value = e.latlng.lat.toFixed(6);
        lngField.value = e.latlng.lng.toFixed(6);

        document.getElementById('lat').textContent = e.latlng.lat.toFixed(6);
        document.getElementById('lng').textContent = e.latlng.lng.toFixed(6);
        document.getElementById('locationInfo').style.display = 'block';
    });
}

/* ========================= GRAVEDAD ========================= */
document.addEventListener("DOMContentLoaded", () => {
    const gravedadField = document.getElementById('id_gravedad');
    const options = document.querySelectorAll('.severity-option');

    options.forEach(option => {
        option.addEventListener('click', () => {
            const value = option.dataset.value;
            gravedadField.value = value;
            paintSeverity(value);
        });
    });
});

function paintSeverity(value) {
    document.querySelectorAll('.severity-option')
        .forEach(opt => opt.classList.remove('selected'));

    const chosen = document.querySelector(`.severity-option[data-value="${value}"]`);
    if (chosen) chosen.classList.add('selected');
}

/* ========================= ANÓNIMO ========================= */
document.addEventListener("DOMContentLoaded", () => {
    const checkbox = document.getElementById('id_anonimo');
    const contactFields = document.getElementById('contactFields');

    if (!checkbox || !contactFields) return;

    checkbox.addEventListener('change', () => {
        const isAnon = checkbox.checked;

        contactFields.style.opacity = isAnon ? '0.5' : '1';
        contactFields.style.pointerEvents = isAnon ? 'none' : 'auto';
    });
});

/* ========================= IMÁGENES ========================= */
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const fileCount = document.getElementById('fileCount');

function updateFileCount() {
    if (fileCount) fileCount.textContent = previewFiles.length;
}

function displayImage(file, index) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const div = document.createElement('div');
        div.className = 'image-preview';
        div.dataset.index = index;
        div.innerHTML = `
            <img src="${e.target.result}" alt="Preview">
            <button type="button" class="remove-image" data-remove="${index}">
                <i class="fas fa-times"></i>
            </button>`;
        imagePreview.appendChild(div);
    };
    reader.readAsDataURL(file);
}

function rerenderPreview() {
    imagePreview.innerHTML = '';
    previewFiles.forEach((file, idx) => displayImage(file, idx));
    updateFileCount();
}

function addFiles(fileList) {
    const maxFiles = 5;

    for (const file of fileList) {
        if (previewFiles.length >= maxFiles) break;
        if (!file.type.startsWith('image/')) continue;
        if (file.size > 5 * 1024 * 1024) continue;

        previewFiles.push(file);
    }

    const dt = new DataTransfer();
    previewFiles.forEach(f => dt.items.add(f));
    fileInput.files = dt.files;

    rerenderPreview();
}

if (uploadArea) uploadArea.addEventListener('click', () => fileInput.click());
if (fileInput) fileInput.addEventListener('change', (e) => addFiles(e.target.files));

uploadArea?.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea?.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));

uploadArea?.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    addFiles(e.dataTransfer.files);
});

imagePreview?.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-remove]');
    if (!btn) return;

    const idx = Number(btn.dataset.remove);
    previewFiles.splice(idx, 1);

    const dt = new DataTransfer();
    previewFiles.forEach(f => dt.items.add(f));
    fileInput.files = dt.files;

    rerenderPreview();
});

/* ========================= CONTADOR DESCRIPCIÓN ========================= */
const descripcionField = document.getElementById('id_descripcion');
const descProgress = document.getElementById('descProgress');
const charCount = document.getElementById('charCount');

function updateCharCounter() {
    if (!descripcionField) return;

    const min = 50;
    const cur = descripcionField.value.length;
    const percent = Math.min((cur / min) * 100, 100);

    descProgress.style.width = `${percent}%`;

    if (cur < min) {
        charCount.textContent = `Mínimo 50 caracteres (${cur}/50)`;
        charCount.className = 'char-counter invalid';
        descProgress.style.background = 'var(--color-danger)';
    } else {
        charCount.textContent = `${cur} caracteres`;
        charCount.className = 'char-counter valid';
        descProgress.style.background = 'var(--color-secondary)';
    }
}

if (descripcionField) descripcionField.addEventListener('input', updateCharCounter);

/* ========================= LOG ENVÍO ========================= */
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('reportForm');
    if (!form) return;

    form.addEventListener('submit', () => {
        const fd = new FormData(form);
        console.log('📤 ENVIANDO FORMULARIO');
        for (let [k, v] of fd.entries()) {
            if (v instanceof File) console.log(`${k}: ${v.name}`);
            else console.log(`${k}: ${v}`);
        }
    });
});
