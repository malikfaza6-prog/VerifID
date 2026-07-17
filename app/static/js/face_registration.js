/* ========================================
   Face Registration JavaScript
   ======================================== */

let selectedEmpId = null;
let selectedEmpData = null;
let mediaStream = null;
let captureInterval = null;
let collectedFrames = 0;
const REQUIRED_FRAMES = 30;
let sessionKey = `reg_${Date.now()}_${Math.random().toString(36).slice(2)}`;
let isCapturing = false;
let countdownTimer = null;

const video = document.getElementById('videoFeed');
const canvas = document.getElementById('canvasOverlay');
const ctx = canvas ? canvas.getContext('2d') : null;
const cameraPanel = document.getElementById('cameraPanel');
const selectPrompt = document.getElementById('selectPrompt');
const btnStart = document.getElementById('btnStartScan');
const btnStop = document.getElementById('btnStopScan');
const btnDelete = document.getElementById('btnDeleteEncoding');
const progressSection = document.getElementById('progressSection');
const frameProgress = document.getElementById('frameProgress');
const frameCountText = document.getElementById('frameCountText');
const cameraStatus = document.getElementById('cameraStatus');
const cameraStatusText = document.getElementById('cameraStatusText');
const countdownEl = document.getElementById('countdown');
const registrationResult = document.getElementById('registrationResult');

// ---- Employee Search Filter ----
document.getElementById('empSearch').addEventListener('input', function() {
    const q = this.value.toLowerCase();
    document.querySelectorAll('.emp-list-item').forEach(item => {
        const name = item.dataset.nama.toLowerCase();
        const nik = item.dataset.nik.toLowerCase();
        item.style.display = (name.includes(q) || nik.includes(q)) ? '' : 'none';
    });
});

// ---- Select Employee ----
async function selectEmployee(el) {
    document.querySelectorAll('.emp-list-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');

    selectedEmpId = parseInt(el.dataset.id);
    const { ok, data } = await apiRequest(`/wajah/api/check/${selectedEmpId}`);

    if (!ok) {
        showToast('Gagal memuat data pegawai.', 'danger');
        return;
    }

    selectedEmpData = data.employee;
    selectPrompt.classList.add('d-none');
    cameraPanel.classList.remove('d-none');
    registrationResult.classList.add('d-none');

    // Update badge
    document.getElementById('selectedEmployeeInfo').classList.remove('d-none');
    document.getElementById('selectedEmpBadge').textContent = `${selectedEmpData.nama} (${selectedEmpData.nik})`;

    if (data.has_encoding) {
        btnDelete.classList.remove('d-none');
        setStatus(`⚠️ ${selectedEmpData.nama} sudah terdaftar. Daftarkan ulang atau hapus.`, 'warning');
    } else {
        btnDelete.classList.add('d-none');
        setStatus('Pilih "Mulai Scan Wajah" untuk mendaftarkan wajah.', 'info');
    }

    resetCapture();

    // Start camera preview
    await startCamera();
}

// ---- Start Camera ----
async function startCamera() {
    if (mediaStream) return;
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        video.srcObject = mediaStream;
        await video.play();
        syncCanvas();
    } catch (e) {
        setStatus('❌ Kamera tidak dapat diakses: ' + e.message, 'danger');
    }
}

function syncCanvas() {
    if (video && canvas) {
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
    }
}

// ---- Stop Camera ----
function stopCamera() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(t => t.stop());
        mediaStream = null;
    }
}

// ---- Start Capture ----
btnStart.addEventListener('click', async () => {
    if (!selectedEmpId) {
        showToast('Pilih pegawai terlebih dahulu.', 'warning');
        return;
    }
    sessionKey = `reg_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    collectedFrames = 0;
    frameProgress.style.width = '0%';
    frameCountText.textContent = '0 / 30';

    btnStart.classList.add('d-none');
    btnStop.classList.remove('d-none');
    progressSection.style.display = 'block';

    // Countdown 3,2,1
    await runCountdown();
    startFrameCapture();
});

// ---- Countdown ----
async function runCountdown() {
    return new Promise(resolve => {
        let count = 3;
        countdownEl.style.display = 'block';
        countdownEl.textContent = count;
        countdownTimer = setInterval(() => {
            count--;
            if (count <= 0) {
                countdownEl.style.display = 'none';
                clearInterval(countdownTimer);
                resolve();
            } else {
                countdownEl.textContent = count;
            }
        }, 1000);
    });
}

// ---- Frame Capture Loop ----
function startFrameCapture() {
    isCapturing = true;
    setStatus('📸 Mengambil frame wajah...', 'info');

    captureInterval = setInterval(async () => {
        if (!isCapturing || collectedFrames >= REQUIRED_FRAMES) {
            clearInterval(captureInterval);
            if (collectedFrames >= REQUIRED_FRAMES) {
                await finalizeRegistration();
            }
            return;
        }

        const frameB64 = captureFrame();
        if (!frameB64) return;

        try {
            const res = await fetch('/wajah/api/process-frame', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pegawai_id: selectedEmpId, frame_b64: frameB64, session_key: sessionKey }),
            });
            const data = await res.json();

            if (data.success && data.status === 'ok') {
                collectedFrames = data.collected;
                const pct = Math.round((collectedFrames / REQUIRED_FRAMES) * 100);
                frameProgress.style.width = pct + '%';
                frameCountText.textContent = `${collectedFrames} / ${REQUIRED_FRAMES}`;
                setStatus(`✅ Frame ${collectedFrames}/${REQUIRED_FRAMES} berhasil diambil.`, 'success');
                updateInstructions(true, true, true);
            } else {
                handleFrameError(data.status);
            }
        } catch (e) {
            setStatus('Kesalahan jaringan.', 'danger');
        }
    }, 300);
}

function handleFrameError(status) {
    const msgs = {
        'no_face': ['Tidak ada wajah.', false, null, null],
        'multiple_faces': ['Hanya boleh satu wajah!', null, null, false],
        'blur': ['Gambar buram, stabilkan kamera.', null, false, null],
        'poor_lighting': ['Pencahayaan kurang.', null, null, null],
        'encoding_failed': ['Gagal encode, coba lagi.', null, null, null],
    };
    const [msg, face, sharp, single] = msgs[status] || ['Gagal memproses.', null, null, null];
    setStatus('⚠️ ' + msg, 'warning');
    updateInstructions(face, sharp, single);
}

function updateInstructions(face, sharp, single) {
    const setInstr = (id, ok) => {
        const el = document.getElementById(id);
        if (!el || ok === null) return;
        el.className = 'instruction-item ' + (ok ? 'ok' : 'fail');
        el.querySelector('i').className = `bi bi-${ok ? 'check-circle-fill text-success' : 'x-circle-fill text-danger'}`;
    };
    setInstr('instrFace', face);
    setInstr('instrLight', sharp);
    setInstr('instrSingle', single);
}

// ---- Capture Frame ----
function captureFrame() {
    if (!video || !video.videoWidth) return null;
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    tempCanvas.getContext('2d').drawImage(video, 0, 0);
    return tempCanvas.toDataURL('image/jpeg', 0.8);
}

// ---- Finalize Registration ----
async function finalizeRegistration() {
    isCapturing = false;
    btnStop.classList.add('d-none');
    setStatus('⏳ Menyimpan encoding wajah...', 'info');

    try {
        const res = await fetch('/wajah/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pegawai_id: selectedEmpId, session_key: sessionKey }),
        });
        const data = await res.json();

        if (data.success) {
            stopCamera();
            cameraPanel.classList.add('d-none');
            registrationResult.classList.remove('d-none');
            document.getElementById('resultMsg').textContent = data.message;
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'danger');
            setStatus('❌ ' + data.message, 'danger');
            btnStart.classList.remove('d-none');
            progressSection.style.display = 'none';
        }
    } catch (e) {
        showToast('Kesalahan server.', 'danger');
        resetCapture();
    }
}

// ---- Stop Button ----
btnStop.addEventListener('click', () => {
    isCapturing = false;
    clearInterval(captureInterval);
    clearInterval(countdownTimer);
    resetCapture();
});

// ---- Delete Encoding ----
btnDelete.addEventListener('click', async () => {
    if (!confirm(`Hapus data wajah ${selectedEmpData?.nama}?`)) return;
    const { ok, data } = await apiRequest(`/wajah/api/delete/${selectedEmpId}`, { method: 'DELETE' });
    showToast(data.message, ok && data.success ? 'success' : 'danger');
    if (data.success) btnDelete.classList.add('d-none');
});

function setStatus(msg, type = 'info') {
    const colors = { info: '#06b6d4', success: '#10b981', warning: '#f59e0b', danger: '#ef4444' };
    if (cameraStatus) {
        cameraStatus.style.borderColor = colors[type] || colors.info;
        cameraStatusText.textContent = msg;
    }
}

function resetCapture() {
    isCapturing = false;
    clearInterval(captureInterval);
    clearInterval(countdownTimer);
    countdownEl.style.display = 'none';
    btnStart.classList.remove('d-none');
    btnStop.classList.add('d-none');
    progressSection.style.display = 'none';
    collectedFrames = 0;
    frameProgress.style.width = '0%';
    frameCountText.textContent = '0 / 30';
    updateInstructions(null, null, null);
}

function resetRegistration() {
    stopCamera();
    registrationResult.classList.add('d-none');
    cameraPanel.classList.add('d-none');
    selectPrompt.classList.remove('d-none');
    document.getElementById('selectedEmployeeInfo').classList.add('d-none');
    document.querySelectorAll('.emp-list-item').forEach(i => i.classList.remove('selected'));
    selectedEmpId = null;
    selectedEmpData = null;
    resetCapture();
}

// Auto-select if emp_id in query
const urlParams = new URLSearchParams(window.location.search);
const preSelectId = urlParams.get('emp_id');
if (preSelectId) {
    const el = document.querySelector(`.emp-list-item[data-id="${preSelectId}"]`);
    if (el) el.click();
}
