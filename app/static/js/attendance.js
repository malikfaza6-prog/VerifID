/* ========================================
   Attendance Scanning JavaScript
   Alur: deteksi wajah -> pilih mata kuliah -> konfirmasi
   ======================================== */

let mediaStream = null;
let scanInterval = null;
let isScanning = false;
let matkulOptions = [];
let pendingRecognition = null; // { pegawai_id, nama, nik, departemen, foto, confidence }

const video = document.getElementById('videoFeed');
const btnStart = document.getElementById('btnStartCam');
const btnStop = document.getElementById('btnStopCam');
const statusText = document.getElementById('statusText');
const cameraIndicator = document.getElementById('cameraIndicator');
const scanLine = document.getElementById('scanLine');
const resultPanel = document.getElementById('resultPanel');
const emptyResult = document.getElementById('emptyResult');
const matkulResult = document.getElementById('matkulResult');
const successResult = document.getElementById('successResult');
const errorResult = document.getElementById('errorResult');
const todayLog = document.getElementById('todayLog');

// ---- Load daftar mata kuliah sekali di awal ----
async function loadMatkulOptions() {
    try {
        const res = await fetch('/absensi/api/matkul-list');
        const json = await res.json();
        if (json.success) {
            matkulOptions = json.data;
            const select = document.getElementById('matkulSelect');
            if (select) {
                select.innerHTML = '<option value="">-- Pilih Mata Kuliah --</option>' +
                    matkulOptions.map(m => `<option value="${m.id}">${m.kode} - ${m.nama}</option>`).join('');
            }
        }
    } catch (e) {
        console.error('Gagal memuat daftar matkul:', e);
    }
}
loadMatkulOptions();

// ---- Camera Control ----
if (btnStart) {
    btnStart.addEventListener('click', async () => {
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
            video.srcObject = mediaStream;
            await video.play();

            btnStart.classList.add('d-none');
            btnStop.classList.remove('d-none');
            cameraIndicator?.classList.remove('bg-danger');
            cameraIndicator?.classList.add('bg-success');
            if (cameraIndicator) cameraIndicator.innerHTML = '<i class="bi bi-record-circle-fill me-1"></i>SCANNING';
            if (scanLine) scanLine.style.display = 'block';
            setStatus('Sedang mendeteksi wajah...', 'info');

            startScanning();
        } catch (e) {
            setStatus('Kamera tidak dapat diakses.', 'danger');
            showToast('Kamera tidak dapat diakses: ' + e.message, 'danger');
        }
    });
}

if (btnStop) {
    btnStop.addEventListener('click', () => {
        stopCamera();
        btnStop.classList.add('d-none');
        btnStart.classList.remove('d-none');
        cameraIndicator?.classList.remove('bg-success');
        cameraIndicator?.classList.add('bg-danger');
        if (cameraIndicator) cameraIndicator.innerHTML = '<i class="bi bi-record-circle-fill me-1"></i>LIVE';
        if (scanLine) scanLine.style.display = 'none';
        setStatus('Penindaian dihentikan.', 'warning');
        hideResults();
    });
}

function stopCamera() {
    isScanning = false;
    clearInterval(scanInterval);
    if (mediaStream) {
        mediaStream.getTracks().forEach(t => t.stop());
        mediaStream = null;
    }
}

// ---- Scan Loop ----
function startScanning() {
    isScanning = true;
    scanInterval = setInterval(async () => {
        if (!isScanning) return;

        const frameB64 = captureFrame();
        if (!frameB64) return;

        try {
            const res = await fetch('/absensi/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ frame_b64: frameB64 }),
            });
            const data = await res.json();

            if (data.success && data.status === 'recognized') {
                // Pause scanning, tampilkan pemilihan mata kuliah
                isScanning = false;
                showMatkulSelection(data.employee);
            } else if (data.status === 'cooldown') {
                showError(data);
                isScanning = false;
                setTimeout(() => { if (mediaStream) isScanning = true; }, 3000);
            } else if (data.status === 'unknown') {
                showError(data);
                // Don't wait on unknown, keep scanning immediately for better response
            }
        } catch (e) {
            console.error('Scan error:', e);
        }
    }, 800); // Scan every 0.8s for better responsiveness
}

function captureFrame() {
    if (!video || !video.videoWidth) return null;
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    tempCanvas.getContext('2d').drawImage(video, 0, 0);
    return tempCanvas.toDataURL('image/jpeg', 0.8);
}

// ---- UI Updates ----
function setStatus(msg, type = 'info') {
    if (statusText) statusText.textContent = msg;
}

function hideResults() {
    emptyResult?.classList.remove('d-none');
    matkulResult?.classList.add('d-none');
    successResult?.classList.add('d-none');
    errorResult?.classList.add('d-none');
}

// ---- Step 1: Wajah dikenali -> tampilkan pilihan matkul ----
function showMatkulSelection(emp) {
    pendingRecognition = emp;

    emptyResult?.classList.add('d-none');
    successResult?.classList.add('d-none');
    errorResult?.classList.add('d-none');
    matkulResult?.classList.remove('d-none');

    const namaEl = document.getElementById('matkulNama');
    const nikEl = document.getElementById('matkulNik');
    const avatarEl = document.getElementById('matkulAvatar');
    if (namaEl) namaEl.textContent = emp.nama;
    if (nikEl) nikEl.textContent = emp.nik;
    if (avatarEl) {
        avatarEl.innerHTML = emp.foto
            ? `<img src="/static/uploads/${emp.foto}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`
            : `<i class="bi bi-person-fill"></i>`;
    }

    const select = document.getElementById('matkulSelect');
    if (select) select.value = '';

    playBeep(600, 100);
}

document.getElementById('btnBatalMatkul')?.addEventListener('click', () => {
    pendingRecognition = null;
    hideResults();
    isScanning = true;
});

document.getElementById('btnKonfirmasiMatkul')?.addEventListener('click', async () => {
    const select = document.getElementById('matkulSelect');
    const matkulId = select ? select.value : '';

    if (!matkulId) {
        showToast('Silakan pilih mata kuliah terlebih dahulu.', 'warning');
        return;
    }
    if (!pendingRecognition) {
        hideResults();
        isScanning = true;
        return;
    }

    const btn = document.getElementById('btnKonfirmasiMatkul');
    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Menyimpan...'; }

    try {
        const res = await fetch('/absensi/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pegawai_id: pendingRecognition.pegawai_id,
                matkul_id: matkulId,
                confidence: pendingRecognition.confidence,
            }),
        });
        const data = await res.json();

        if (data.success) {
            showSuccess(data, pendingRecognition);
        } else {
            showError({ status: 'gagal', message: data.message, employee: pendingRecognition });
        }
    } catch (e) {
        console.error('Submit error:', e);
        showError({ status: 'gagal', message: 'Gagal terhubung ke server.', employee: pendingRecognition });
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-check-lg me-1"></i>Konfirmasi Absen'; }
        pendingRecognition = null;
        setTimeout(() => { if (mediaStream) isScanning = true; }, 3000);
    }
});

// ---- Step 2: Hasil akhir (sukses / gagal) ----
function showSuccess(data, emp) {
    emptyResult?.classList.add('d-none');
    matkulResult?.classList.add('d-none');
    errorResult?.classList.add('d-none');
    successResult?.classList.remove('d-none');

    const nama = emp.nama;
    document.getElementById('resultNama').textContent = nama;
    document.getElementById('resultNik').textContent = emp.nik;
    document.getElementById('resultDept').textContent = emp.departemen || '-';

    const now = new Date();
    document.getElementById('resultJam').textContent = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const confEl = document.getElementById('resultConfidence');
    if (confEl) confEl.textContent = `${emp.confidence}%`;

    const statusEl = document.getElementById('resultStatus');
    if (statusEl) {
        statusEl.innerHTML = data.message.includes('T' + 'E' + 'R' + 'L' + 'A' + 'M' + 'B' + 'A' + 'T')
            ? '<span class="text-warning">Terlambat</span>'
            : '<span class="text-success">Hadir</span>';
    }
    document.getElementById('resultMessage').textContent = data.message;

    const avatarEl = document.getElementById('resultAvatar');
    if (avatarEl) {
        avatarEl.innerHTML = emp.foto
            ? `<img src="/static/uploads/${emp.foto}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`
            : `<i class="bi bi-person-fill"></i>`;
    }

    addLogItem(nama, data.message, emp.foto);
    showToast(`${nama}: ${data.message}`, 'success');
    playBeep(800, 150);
}

function showError(data) {
    emptyResult?.classList.add('d-none');
    matkulResult?.classList.add('d-none');
    successResult?.classList.add('d-none');
    errorResult?.classList.remove('d-none');

    const titleEl = document.getElementById('errorTitle');
    const msgEl = document.getElementById('errorMessage');

    if (data.status === 'cooldown') {
        if (titleEl) titleEl.textContent = 'Harap Tunggu';
        if (msgEl) msgEl.textContent = data.message;
        if (data.employee && data.employee.nama && msgEl) {
             msgEl.textContent = `Absensi ${data.employee.nama} telah tercatat. Tunggu beberapa saat.`;
        }
    } else if (data.status === 'unknown') {
        if (titleEl) titleEl.textContent = 'Wajah Tidak Dikenali';
        if (msgEl) msgEl.textContent = data.message || 'Wajah tidak cocok dengan database.';
    } else {
        if (titleEl) titleEl.textContent = 'Absensi Gagal';
        if (msgEl) msgEl.textContent = data.message || 'Terjadi kesalahan saat menyimpan absensi.';
    }

    playBeep(300, 300);
}

let logCount = 0;
function addLogItem(nama, msg, foto) {
    if (!todayLog) return;
    document.getElementById('emptyLog')?.remove();

    const div = document.createElement('div');
    div.className = 'activity-item';
    div.innerHTML = `
        <div class="activity-avatar">
            ${foto ? `<img src="/static/uploads/${foto}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">` : nama[0].toUpperCase()}
        </div>
        <div class="activity-content">
            <div class="activity-user">${nama}</div>
            <div class="activity-text">${msg}</div>
        </div>
        <div class="activity-time">
            <i class="bi bi-clock me-1"></i>Baru saja
        </div>
    `;

    todayLog.prepend(div);
    logCount++;
    if (logCount > 5 && todayLog.lastElementChild) { // Keep last 5
        todayLog.lastElementChild.remove();
    }
}

// Simple beep for feedback
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playBeep(freq, dur) {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    osc.frequency.value = freq;
    osc.type = "sine";
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    osc.start();
    setTimeout(() => osc.stop(), dur);
}
