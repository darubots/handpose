# Aplikasi Handpose (GUI Version)

Aplikasi deteksi gestur tangan (handpose) dengan antarmuka pengguna (GUI) modern yang dibuat menggunakan Python, OpenCV, MediaPipe, dan **CustomTkinter**.

---
*Catatan: Ini adalah dokumentasi untuk versi GUI. Versi sebelumnya yang hanya menggunakan OpenCV telah digantikan oleh versi ini.*
---

## ✨ Developer

Aplikasi ini dikembangkan oleh **izhardevelop** dari tim **Daru Bot**.

[![Statistik GitHub izhardevelop](https://github-readme-stats.vercel.app/api?username=izhardevelop&show_icons=true&theme=radical)](https://github.com/izhardevelop)

Kunjungi profil GitHub: [https://github.com/izhardevelop](https://github.com/izhardevelop)

---

## Fitur Unggulan

- **Antarmuka Modern:** Dibangun dengan **CustomTkinter** untuk tampilan yang bersih dan profesional dengan tema gelap.
- **Pemilihan Kamera Real-time:** Ganti sumber kamera kapan saja menggunakan **menu dropdown** di panel kontrol tanpa perlu me-restart aplikasi.
- **Panel Kontrol Interaktif:** Semua informasi dan kontrol (pemilihan kamera, info gestur, info jarak) ditampilkan secara rapi di panel sebelah kiri.
- **Deteksi Gestur Komprehensif:**
  - **Satu Tangan:** 1-5 Jari, Pose Kepal, Pose OK.
  - **Dua Tangan:** Pose Hati (Love), Pose Lingkaran Besar.
- **Informasi Real-time:** Menampilkan gestur yang terdeteksi dan estimasi jarak tangan dari kamera secara langsung.

## Instalasi

1.  Pastikan Anda memiliki **Python 3.7+**.
2.  Buka terminal atau Command Prompt.
3.  Install semua library yang dibutuhkan (termasuk untuk GUI) dengan satu perintah:

    ```bash
    pip install opencv-python mediapipe numpy customtkinter Pillow
    ```

## Cara Menjalankan

Setelah instalasi selesai, jalankan aplikasi dengan perintah:

```bash
python app_handpose.py
```

Aplikasi akan terbuka, dan Anda dapat langsung memilih kamera dari dropdown di panel kontrol sebelah kiri. Jika tidak ada kamera yang dipilih, feed video tidak akan muncul.
