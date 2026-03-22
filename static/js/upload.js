let currentFileId = null;
let selectedFile = null;

function handleDragOver(event) {
    event.preventDefault();
    const zone = document.getElementById('drop-zone');
    zone.style.borderColor = '#333';
    zone.style.background = '#f8f9fa';
}

function handleDragLeave(event) {
    const zone = document.getElementById('drop-zone');
    zone.style.borderColor = '#ddd';
    zone.style.background = '';
}

function handleDrop(event) {
    event.preventDefault();
    handleDragLeave(event);
    const file = event.dataTransfer.files[0];
    if (file) showFileInfo(file);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) showFileInfo(file);
}

function showFileInfo(file) {
    selectedFile = file;
    document.getElementById('file-info').classList.remove('d-none');
    document.getElementById('file-info').style.display = 'flex';
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = (file.size / 1024).toFixed(1) + ' KB';
    document.getElementById('upload-btn').disabled = false;
    document.getElementById('drop-zone').style.borderColor = '#28a745';
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').classList.add('d-none');
    document.getElementById('upload-btn').disabled = true;
    document.getElementById('drop-zone').style.borderColor = '#ddd';
    document.getElementById('drop-zone').style.background = '';
    document.getElementById('preview-section').classList.add('d-none');
}

async function uploadFile() {
    if (!selectedFile) return;

    const btn = document.getElementById('upload-btn');
    const errorDiv = document.getElementById('error-msg');
    const successDiv = document.getElementById('success-msg');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';
    errorDiv.classList.add('d-none');
    successDiv.classList.add('d-none');

    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        btn.disabled = false;
        btn.innerHTML = 'Upload file';
        errorDiv.textContent = data.detail || 'Upload failed';
        errorDiv.classList.remove('d-none');
        return;
    }

    currentFileId = data.file_id;
    successDiv.textContent = data.message;
    successDiv.classList.remove('d-none');
    btn.innerHTML = 'Uploaded';

    await previewFile();
}

async function previewFile() {
    const response = await fetch(`/api/preview/${currentFileId}`);
    const data = await response.json();
    if (!response.ok) return;

    const tbody = document.getElementById('preview-table-body');
    const rowCount = document.getElementById('row-count');
    const previewSection = document.getElementById('preview-section');

    tbody.innerHTML = '';
    rowCount.textContent = data.rows.length + ' transactions found';

    data.rows.slice(0, 10).forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td style="font-size: 13px;">${row.description}</td>
                <td style="font-size: 13px;">₹${Number(row.amount).toLocaleString()}</td>
                <td style="font-size: 13px;">${row.account_number}</td>
            </tr>
        `;
    });

    previewSection.classList.remove('d-none');
}

async function runAnalysis() {
    const btn = document.getElementById('analyse-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analysing your transactions...';

    const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({file_id: currentFileId})
    });

    const data = await response.json();

    if (!response.ok) {
        btn.disabled = false;
        btn.innerHTML = 'Run analysis';
        const errorDiv = document.getElementById('error-msg');
        errorDiv.textContent = data.detail || 'Analysis failed';
        errorDiv.classList.remove('d-none');
        return;
    }

    sessionStorage.setItem('predictionResult', JSON.stringify(data));
    window.location.href = '/dashboard';
}