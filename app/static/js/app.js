/* ========================================
   VerifID - Main Application JS
   ======================================== */

// ---- Live Clock ----
function updateClock() {
    const el = document.getElementById('liveTime');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleString('id-ID', {
        weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    });
}
setInterval(updateClock, 1000);
updateClock();

// ---- Sidebar Toggle ----
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    // Close sidebar when clicking outside (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 992 && !sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// ---- Alert Auto-dismiss ----
setTimeout(() => {
    document.querySelectorAll('.flash-container .alert').forEach(a => {
        const bs = bootstrap.Alert.getOrCreateInstance(a);
        bs.close();
    });
}, 5000);

// ---- Toast Helper ----
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer') || (() => {
        const c = document.createElement('div');
        c.id = 'toastContainer';
        c.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;';
        document.body.appendChild(c);
        return c;
    })();

    const icons = { success: 'check-circle-fill', danger: 'x-circle-fill', warning: 'exclamation-triangle-fill', info: 'info-circle-fill' };
    const colors = { success: '#10b981', danger: '#ef4444', warning: '#f59e0b', info: '#06b6d4' };

    const toast = document.createElement('div');
    toast.style.cssText = `background:#fff;border-radius:10px;padding:12px 16px;box-shadow:0 8px 30px rgba(0,0,0,0.15);
        display:flex;align-items:center;gap:10px;min-width:280px;max-width:380px;
        border-left:4px solid ${colors[type]};font-size:13px;animation:slideIn 0.3s ease;`;
    toast.innerHTML = `<i class="bi bi-${icons[type]}" style="color:${colors[type]};font-size:18px;flex-shrink:0;"></i>
        <span style="flex:1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;opacity:0.5;font-size:16px;">✕</button>`;

    toastContainer.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, duration);
}

// ---- API Helper ----
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return { ok: response.ok, data };
    } catch (e) {
        return { ok: false, data: { success: false, message: 'Koneksi gagal.' } };
    }
}

// ---- Confirm Dialog ----
function confirmAction(message) {
    return new Promise(resolve => {
        const result = window.confirm(message);
        resolve(result);
    });
}

// Slide-in animation style
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from { transform: translateX(100px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}`;
document.head.appendChild(style);

// Search with debounce
function debounce(fn, delay = 400) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

// Global search keyboard shortcut
const globalSearch = document.getElementById('searchInput');
if (globalSearch) {
    const debouncedSearch = debounce(() => {
        const form = globalSearch.closest('form') || { submit: () => {
            const url = new URL(window.location);
            url.searchParams.set('search', globalSearch.value);
            url.searchParams.set('page', 1);
            window.location = url;
        }};
        form.submit();
    }, 600);
    globalSearch.addEventListener('input', debouncedSearch);
}
