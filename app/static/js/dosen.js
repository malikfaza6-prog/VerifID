/* ========================================
   Dosen - Absensi Mata Kuliah Saya
   ======================================== */

const modalEditAbsen = new bootstrap.Modal(document.getElementById('modalEditAbsen'));
const modalTambahAbsen = new bootstrap.Modal(document.getElementById('modalTambahAbsen'));

let currentPage = 1;
let mahasiswaOptions = [];
let selectedMahasiswaId = null;

function statusBadge(status) {
    if (status === 'hadir') return '<span class="badge bg-success">Hadir</span>';
    if (status === 'terlambat') return '<span class="badge bg-warning text-dark">Terlambat</span>';
    if (status === 'pulang') return '<span class="badge bg-info">Pulang</span>';
    return '<span class="badge bg-secondary">-</span>';
}

// ---- Load & render tabel absensi ----
async function loadAttendance(page = 1) {
    currentPage = page;
    const params = new URLSearchParams({
        search: document.getElementById('filterSearch').value,
        tanggal_from: document.getElementById('filterFrom').value,
        tanggal_to: document.getElementById('filterTo').value,
        page: page,
        per_page: 15,
    });

    const tbody = document.getElementById('attTableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-5">Memuat data...</td></tr>';

    try {
        const res = await fetch(`/dosen/api?${params.toString()}`);
        const json = await res.json();

        if (!json.success || !json.data.length) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-5">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>Belum ada data absensi.</td></tr>`;
            document.getElementById('paginationInfo').textContent = '';
            document.getElementById('paginationControls').innerHTML = '';
            return;
        }

        tbody.innerHTML = json.data.map(r => `
            <tr>
                <td>
                    <div><strong>${r.nama}</strong></div>
                    <div class="text-muted small">${r.nik}</div>
                </td>
                <td>${r.departemen || '-'}</td>
                <td>${r.tanggal || '-'}</td>
                <td>${r.jam_masuk ? r.jam_masuk.substring(0, 5) : '-'}</td>
                <td>${statusBadge(r.status)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick='openEditAbsen(${JSON.stringify(r)})' title="Koreksi">
                        <i class="bi bi-pencil-fill"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        const meta = json.meta;
        document.getElementById('paginationInfo').textContent =
            `Menampilkan ${json.data.length} dari ${meta.total} data (hal ${meta.page}/${meta.total_pages})`;
        renderPagination(meta);
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger py-5">Gagal memuat data.</td></tr>';
    }
}

function renderPagination(meta) {
    const el = document.getElementById('paginationControls');
    let html = '<div class="btn-group btn-group-sm">';
    html += `<button class="btn btn-outline-secondary" ${!meta.has_prev ? 'disabled' : ''} onclick="loadAttendance(${meta.prev_page})"><i class="bi bi-chevron-left"></i></button>`;
    html += `<button class="btn btn-outline-secondary" ${!meta.has_next ? 'disabled' : ''} onclick="loadAttendance(${meta.next_page})"><i class="bi bi-chevron-right"></i></button>`;
    html += '</div>';
    el.innerHTML = html;
}

document.getElementById('btnFilter').addEventListener('click', () => loadAttendance(1));

// ---- Edit absensi (koreksi status/jam) ----
function openEditAbsen(r) {
    document.getElementById('editAttId').value = r.id;
    document.getElementById('editAttNama').textContent = r.nama;
    document.getElementById('editAttNik').textContent = r.nik;
    document.getElementById('editJamMasuk').value = r.jam_masuk || '';
    document.getElementById('editStatus').value = r.status || 'hadir';
    modalEditAbsen.show();
}

document.getElementById('editAbsenForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('editAttId').value;
    const payload = {
        jam_masuk: document.getElementById('editJamMasuk').value,
        status: document.getElementById('editStatus').value,
    };

    const { ok, data } = await apiRequest(`/dosen/api/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (ok && data.success) {
        showToast(data.message, 'success');
        modalEditAbsen.hide();
        loadAttendance(currentPage);
    } else {
        showToast(data.message || 'Gagal menyimpan.', 'danger');
    }
});

// ---- Tambah absensi manual ----
document.querySelector('[data-bs-target="#modalTambahAbsen"]').addEventListener('click', () => {
    document.getElementById('tambahAbsenForm').reset();
    document.getElementById('tambahTanggal').value = new Date().toISOString().slice(0, 10);
    selectedMahasiswaId = null;
    document.getElementById('pilihMahasiswa').innerHTML = '';
    loadMahasiswaOptions('');
});

async function loadMahasiswaOptions(search) {
    try {
        const res = await fetch(`/dosen/api/mahasiswa-list?search=${encodeURIComponent(search)}`);
        const json = await res.json();
        mahasiswaOptions = json.data || [];
        const select = document.getElementById('pilihMahasiswa');
        select.innerHTML = mahasiswaOptions.map(m =>
            `<option value="${m.id}">${m.nama} - ${m.nik} (${m.departemen || '-'})</option>`
        ).join('');
    } catch (e) {
        console.error(e);
    }
}

let searchDebounce;
document.getElementById('cariMahasiswa').addEventListener('input', (e) => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => loadMahasiswaOptions(e.target.value), 300);
});

document.getElementById('tambahAbsenForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const select = document.getElementById('pilihMahasiswa');
    const pegawaiId = select.value;

    if (!pegawaiId) {
        showToast('Pilih mahasiswa terlebih dahulu.', 'warning');
        return;
    }

    const payload = {
        pegawai_id: parseInt(pegawaiId),
        tanggal: document.getElementById('tambahTanggal').value,
        jam_masuk: document.getElementById('tambahJam').value,
        status: document.getElementById('tambahStatus').value,
    };

    const { ok, data } = await apiRequest('/dosen/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (ok && data.success) {
        showToast(data.message, 'success');
        modalTambahAbsen.hide();
        loadAttendance(1);
    } else {
        showToast(data.message || 'Gagal menyimpan.', 'danger');
    }
});

// Init
loadAttendance(1);
