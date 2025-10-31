
# Aplikasi Handpose

Aplikasi deteksi gestur tangan (handpose) yang dibuat dengan Python, OpenCV, dan MediaPipe. Aplikasi ini mampu mengenali berbagai gestur tangan secara real-time melalui webcam.

## ✨ Developer

Aplikasi ini dikembangkan oleh **izhardevelop** dari tim **Daru Bot**.

[![Statistik GitHub izhardevelops](https://github-readme-stats.vercel.app/api?username=izhardevelop&show_icons=true&theme=radical)](https://github.com/izhardevelop)

Kunjungi profil GitHub: [https://github.com/izhardevelop](https://github.com/izhardevelop)

---

## Fitur

- Deteksi 1 & 2 tangan secara bersamaan.
- Pengenalan gestur:
  - **Satu Tangan:** 1-5 Jari, Pose Kepal, Pose OK.
  - **Dua Tangan:** Pose Hati (Love), Pose Lingkaran Besar.
- Estimasi jarak tangan dari kamera.
- Tampilan antarmuka minimalis dengan panel informasi.
- Kompatibilitas CPU/GPU otomatis yang ditangani oleh MediaPipe.
- Deteksi kamera otomatis untuk kompabilitas di berbagai perangkat.

## Instalasi

1.  Pastikan Anda memiliki **Python 3.7+**.
2.  Buka terminal atau Command Prompt.
3.  Install semua library yang dibutuhkan dengan perintah berikut:

    ```bash
    pip install opencv-python mediapipe numpy
    ```

## Cara Menjalankan

Setelah instalasi selesai, jalankan aplikasi dengan perintah:

```bash
python app_handpose.py
```

Aplikasi akan otomatis mencari webcam yang aktif. Arahkan tangan Anda ke kamera untuk memulai deteksi. Tekan tombol **'q'** untuk keluar.
