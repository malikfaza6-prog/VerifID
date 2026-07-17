/* ========================================
   Matkul (Mata Kuliah) Management JavaScript
   ======================================== */

const modalMatkul = new bootstrap.Modal(document.getElementById('modalMatkul'));
const modalDeleteMatkul = new bootstrap.Modal(document.getElementById('modalDeleteMatkul'));
let deleteMatkulId = null;

// ---- Open Add Modal ----
document.querySelector('[data-bs-target="#modalMatkul"]').addEventListener('click', () => {
    resetMatkulForm();
    document.getElementById('matkulModalTitle').innerHTML = '<i class="bi bi-plus-lg me-2"></i>Tambah Mata Kuliah';
});

// ---- Edit ----
async function editMatkul(id) {
    const { ok, data } = await apiRequest(`/matkul/api/${id}`);
    if (!ok || !data.success) {
        showToast(data.message || 'Gagal memuat data.', 'danger');
        return;
    }

    resetMatkulForm();
    const m = data.data;
    document.getElementById('matkulId').value = m.id;
    document.getElementById('matkulKode').value = m.kode;
    document.getElementById('matkulNama').value = m.nama;

    document.getElementById('matkulModalTitle').innerHTML = '<i class="bi bi-pencil-fill me-2"></i>Edit Mata Kuliah';
    modalMatkul.show();
}

// ---- Form Submit ----
document.getElementById('matkulForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const id = document.getElementById('matkulId').value;
    const payload = {
        kode: document.getElementById('matkulKode').value,
        nama: document.getElementById('matkulNama').value,
    };

    const url = id ? `/matkul/api/${id}` : '/matkul/api';
    const method = id ? 'PUT' : 'POST';

    const { ok, data } = await apiRequest(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (ok && data.success) {
        showToast(data.message, 'success');
        modalMatkul.hide();
        setTimeout(() => location.reload(), 800);
    } else {
        showToast(data.message || 'Gagal menyimpan.', 'danger');
    }
});

// ---- Delete ----
function deleteMatkul(id, nama) {
    deleteMatkulId = id;
    document.getElementById('deleteMatkulName').textContent = nama;
    modalDeleteMatkul.show();
}

document.getElementById('confirmDeleteMatkul').addEventListener('click', async () => {
    if (!deleteMatkulId) return;
    const btn = document.getElementById('confirmDeleteMatkul');
    btn.disabled = true;

    const { ok, data } = await apiRequest(`/matkul/api/${deleteMatkulId}`, { method: 'DELETE' });

    btn.disabled = false;
    modalDeleteMatkul.hide();

    if (ok && data.success) {
        showToast(data.message, 'success');
        setTimeout(() => location.reload(), 800);
    } else {
        showToast(data.message || 'Gagal menghapus.', 'danger');
    }
    deleteMatkulId = null;
});

function resetMatkulForm() {
    document.getElementById('matkulForm').reset();
    document.getElementById('matkulId').value = '';
}
