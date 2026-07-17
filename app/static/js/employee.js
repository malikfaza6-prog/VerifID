/* ========================================
   Employee Management JavaScript
   ======================================== */

const modalEmployee = new bootstrap.Modal(document.getElementById('modalEmployee'));
const modalDelete = new bootstrap.Modal(document.getElementById('modalDelete'));
let deleteEmpId = null;

// ---- Photo Preview ----
document.getElementById('empFoto').addEventListener('change', function() {
    const preview = document.getElementById('photoPreview');
    if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = e => {
            preview.innerHTML = `<img src="${e.target.result}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #e2e8f0;">`;
        };
        reader.readAsDataURL(this.files[0]);
    }
});

// ---- Open Add Modal ----
document.querySelector('[data-bs-target="#modalEmployee"]').addEventListener('click', () => {
    resetForm();
    document.getElementById('modalTitle').innerHTML = '<i class="bi bi-person-plus-fill me-2"></i>Tambah Pegawai';
});

// ---- Edit Employee ----
async function editEmployee(id) {
    const { ok, data } = await apiRequest(`/pegawai/api/${id}`);
    if (!ok || !data.success) {
        showToast(data.message || 'Gagal memuat data.', 'danger');
        return;
    }
    const emp = data.data;
    document.getElementById('empId').value = emp.id;
    document.getElementById('empNik').value = emp.nik;
    document.getElementById('empNama').value = emp.nama;
    document.getElementById('empDepartemen').value = emp.departemen || '';
    document.getElementById('empJabatan').value = emp.jabatan || '';
    document.getElementById('empStatus').value = emp.status;

    if (emp.foto) {
        document.getElementById('photoPreview').innerHTML = `<img src="/static/uploads/${emp.foto}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #e2e8f0;">`;
    }

    document.getElementById('modalTitle').innerHTML = '<i class="bi bi-pencil-fill me-2"></i>Edit Pegawai';
    modalEmployee.show();
}

// ---- Form Submit ----
document.getElementById('employeeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Menyimpan...';

    const id = document.getElementById('empId').value;
    const formData = new FormData(this);

    const url = id ? `/pegawai/api/${id}` : '/pegawai/api';
    const method = id ? 'PUT' : 'POST';

    const { ok, data } = await apiRequest(url, { method, body: formData });

    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="bi bi-save me-1"></i>Simpan';

    if (ok && data.success) {
        showToast(data.message, 'success');
        modalEmployee.hide();
        setTimeout(() => location.reload(), 1000);
    } else {
        showToast(data.message || 'Gagal menyimpan.', 'danger');
    }
});

// ---- Delete ----
function deleteEmployee(id, nama) {
    deleteEmpId = id;
    document.getElementById('deleteEmpName').textContent = nama;
    modalDelete.show();
}

document.getElementById('confirmDelete').addEventListener('click', async () => {
    if (!deleteEmpId) return;
    const btn = document.getElementById('confirmDelete');
    btn.disabled = true;

    const { ok, data } = await apiRequest(`/pegawai/api/${deleteEmpId}`, { method: 'DELETE' });

    btn.disabled = false;
    modalDelete.hide();

    if (ok && data.success) {
        showToast(data.message, 'success');
        setTimeout(() => location.reload(), 800);
    } else {
        showToast(data.message || 'Gagal menghapus.', 'danger');
    }
    deleteEmpId = null;
});

// ---- Reset Form ----
function resetForm() {
    document.getElementById('empId').value = '';
    document.getElementById('employeeForm').reset();
    document.getElementById('photoPreview').innerHTML = '';
}
