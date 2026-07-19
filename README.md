# VerifID - Sistem Absensi Wajah Berbasis Web

Sistem informasi absensi cerdas menggunakan teknologi Facial Recognition (Pengenalan Wajah). Memanfaatkan OpenCV dan `face_recognition` library dalam framework Python (Flask) untuk mengenali wajah secara Real-Time melalui Webcam.

## 🔥 Fitur Utama
* **Dashboard Analitik**: Pantau tren kehadiran, keterlambatan, dan aktivitas harian dengan chart interaktif.
* **Manajemen Pegawai**: CRUD data pegawai terpusat, mendukung upload foto.
* **Pendaftaran Wajah Cerdas**: Algoritma mendeteksi & memandu user untuk mengambil frame wajah yang baik (cek pencahayaan, tingkat blur, wajah berlipat). Sistem mencuplik 30 frame dan melakukan rendering encoding numpy.
* **Absensi Cepat**: Cukup hadapkan wajah ke kamera untuk melakukan absen masuk atau absen pulang.
* **Export Laporan**: Filter riwayat absensi dan unduh dalam format Excel & PDF.
* **Role Management**: Pemisahan akses antara Admin dan Operator.

## 🛠️ Stack Teknologi
* **Backend**: Python 3, Flask, Blueprint routing
* **Database**: MySQL, SQLAlchemy (Pattern), Connection Pooling
* **Computer Vision**: OpenCV (Haar Cascades detect), dlib (`face_recognition` encoder)
* **Frontend**: HTML5, CSS3, ES6 JavaScript, Bootstrap 5 UI, Vanilla CSS Customizer (Dark Mode Admin)
* **Arsitektur**: MVC (Model View Controller), Repository Pattern, Service Layer.

## 🚀 Cara Instalasi

### 1. Persiapan Environment
```bash
# Buat Virtual Environment 
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate
# (Mac/Linux)
# source venv/bin/activate
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```
> **Catatan Windows**: Jika Anda mengalami error saat instalasi `face_recognition` / `dlib`, pastikan Anda sudah menginstal **CMake** dan **Visual Studio Build Tools** (C++).

### 3. Konfigurasi Database & Lingkungan
Buat database MySQL baru, contoh: `attendance_system`. 
Ubah file `.env` dan masukkan detail database Anda.
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=attendance_system
```

### 4. Menjalankan Aplikasi
Aplikasi ini sudah dilengkapi auto-migration. Saat aplikasi berjalan pertama kali, tabel database akan secara otomatis dibuat dan akun `admin` bawaan akan di-generate.
```bash
flask run --debug
# atau
python run.py
```
Akses di browser melalui: `http://localhost:5000`

### 🔑 Akun Default
- **Username**: `admin`
- **Password**: `admin123`

## 📂 Struktur Aplikasi
Aplikasi ini dipecah berdasarkan Service & Repository Pattern:
* `app/controllers` -> Digantikan dengan `routes/` (Flask Blueprints)
* `app/services/` -> Menangani Business Logic (Pendaftaran, Pengenalan)
* `app/repositories/` -> Menangani Data Access Logic (Query MySQL)
* `app/models/` -> Class struktur data (Entity).
* `app/camera/` -> Modul khusus memisahkan OpenCV dan Face Recognition dari Logic web.

---
Dikembangkan mematuhi prinsip Clean Code dan S.O.L.I.D.
