/* ========================================
   User Management JavaScript
   ======================================== */

const modalUser = new bootstrap.Modal(document.getElementById('modalUser'));
const modalDeleteUser = new bootstrap.Modal(document.getElementById('modalDeleteUser'));
let deleteUserId = null;
let matkulOptionsCache = [];

// ---- Muat daftar mata kuliah utk dropdown role Dosen ----
async function loadMatkulOptionsForUserForm() {
    try {
        const res = await fetch('/matkul/api');
        const json = await res.json();
        if (json.success) {
            matkulOptionsCache = json.data;
            const select = document.getElementById('userMatkul');
            select.innerHTML = '<option value="">-- Pilih Mata Kuliah --</option>' +
                matkulOptionsCache.map(m => `<option value="${m.id}">${m.kode} - ${m.nama}</option>`).join('');
        }
    } catch (e) {
        console.error('Gagal memuat daftar matkul:', e);
    }
}
loadMatkulOptionsForUserForm();

// ---- Open Add Modal ----
document.querySelector('[data-bs-target="#modalUser"]').addEventListener('click', () => {
    resetUserForm();
    document.getElementById('userModalTitle').innerHTML = '<i class="bi bi-person-plus-fill me-2"></i>Tambah User';
    document.getElementById('pwdRequired').textContent = '*';
    document.getElementById('statusGroup').style.display = 'none'; // Hide status on create
    toggleKelasField();
});

// ---- Toggle Kelas/Matkul field berdasarkan role yang dipilih ----
function toggleKelasField() {
    const role = document.getElementById('userRole').value;
    const kelasGroup = document.getElementById('kelasGroup');
    const matkulGroup = document.getElementById('matkulGroup');
    kelasGroup.classList.toggle('d-none', role !== 'kelas');
    matkulGroup.classList.toggle('d-none', role !== 'dosen');
}
document.getElementById('userRole').addEventListener('change', toggleKelasField);

// ---- Edit User ----
async function editUser(id) {
    const { ok, data } = await apiRequest(`/users/api/${id}`);
    if (!ok || !data.success) {
        showToast(data.message || 'Gagal memuat data.', 'danger');
        return;
    }
    
    resetUserForm();
    const u = data.data;
    document.getElementById('userId').value = u.id;
    document.getElementById('userUsername').value = u.username;
    document.getElementById('userRole').value = u.role;
    document.getElementById('userIsActive').value = u.is_active;
    document.getElementById('userKelas').value = u.kelas || '';
    document.getElementById('userMatkul').value = u.matkul_id || '';
    toggleKelasField();
    
    document.getElementById('userModalTitle').innerHTML = '<i class="bi bi-pencil-fill me-2"></i>Edit User';
    document.getElementById('pwdRequired').textContent = '';
    document.getElementById('pwdHint').textContent = 'Kosongkan jika tidak ingin mengubah password';
    document.getElementById('statusGroup').style.display = 'block';
    
    modalUser.show();
}

// ---- Form Submit ----
document.getElementById('userForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const id = document.getElementById('userId').value;
    const pwd = document.getElementById('userPassword').value;
    
    if (!id && pwd.length < 6) {
        showToast('Password minimal 6 karakter', 'warning');
        return;
    }
    
    const payload = {
        username: document.getElementById('userUsername').value,
        role: document.getElementById('userRole').value,
        is_active: document.getElementById('userIsActive').value,
        kelas: document.getElementById('userKelas').value,
        matkul_id: document.getElementById('userMatkul').value,
    };
    if (pwd) payload.password = pwd;

    const url = id ? `/users/api/${id}` : '/users/api';
    const method = id ? 'PUT' : 'POST';

    const { ok, data } = await apiRequest(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (ok && data.success) {
        showToast(data.message, 'success');
        modalUser.hide();
        setTimeout(() => location.reload(), 1000);
    } else {
        showToast(data.message || 'Gagal menyimpan.', 'danger');
    }
});

// ---- Delete ----
function deleteUser(id, username) {
    deleteUserId = id;
    document.getElementById('deleteUserName').textContent = username;
    modalDeleteUser.show();
}

document.getElementById('confirmDeleteUser').addEventListener('click', async () => {
    if (!deleteUserId) return;
    const btn = document.getElementById('confirmDeleteUser');
    btn.disabled = true;

    const { ok, data } = await apiRequest(`/users/api/${deleteUserId}`, { method: 'DELETE' });

    btn.disabled = false;
    modalDeleteUser.hide();

    if (ok && data.success) {
        showToast(data.message, 'success');
        setTimeout(() => location.reload(), 800);
    } else {
        showToast(data.message || 'Gagal menghapus.', 'danger');
    }
    deleteUserId = null;
});

function resetUserForm() {
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('pwdHint').textContent = '';
}
