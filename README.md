# Kontrol Relay Arduino dengan Gestur Tangan

Proyek ini memungkinkan pengguna untuk mengontrol sebuah relay yang terhubung ke Arduino menggunakan gestur tangan yang dideteksi melalui kamera webcam. Aplikasi utama ditulis dalam Python dan menggunakan OpenCV dan MediaPipe untuk pemrosesan gambar, sementara Arduino menjalankan kode untuk menerima perintah melalui komunikasi serial.

## Cara Kerja

1.  **Aplikasi Python (`gui.py`)**: 
    -   Saat dijalankan, aplikasi akan menampilkan jendela untuk memilih port serial tempat Arduino terhubung.
    -   Setelah port dipilih, aplikasi akan mengaktifkan kamera webcam.
    -   Menggunakan pustaka `mediapipe`, aplikasi secara terus-menerus mendeteksi posisi tangan dalam frame video.
    -   Aplikasi ini secara spesifik mencari dua jenis gestur:
        -   **Gestur "V" (2 Jari)**: Ketika jari telunjuk dan jari tengah terangkat, aplikasi mengirimkan string `"ON"` melalui koneksi serial ke Arduino.
        -   **Gestur 3 Jari**: Ketika jari telunjuk, tengah, dan manis terangkat, aplikasi mengirimkan string `"OFF"` melalui koneksi serial.

2.  **Kode Arduino (`smart_coding.ino`)**:
    -   Kode ini diunggah ke papan Arduino.
    -   Arduino terus-menerus mendengarkan data yang masuk pada port serial.
    -   Ketika menerima string `"ON"`, Arduino akan mengaktifkan `RELAY_D7` (terhubung ke pin digital 7) dengan mengaturnya ke level `HIGH`.
    -   Ketika menerima string `"OFF"`, Arduino akan menonaktifkan `RELAY_D7` dengan mengaturnya ke level `LOW`.
    -   Kode ini juga berisi logika untuk mengontrol relay lain berdasarkan input dari sensor suhu (NTC), air, dan cahaya (CDS), tetapi kontrol utama dari Python ditujukan untuk `RELAY_D7`.

## File dalam Proyek

-   `gui.py`: Aplikasi utama berbasis Python dengan antarmuka grafis (GUI) untuk pemilihan port dan deteksi gestur.
-   `smart_coding.ino`: Sketch Arduino untuk menerima perintah serial dan mengontrol beberapa relay.
-   `handpose.py`: Versi awal dari skrip deteksi tangan, yang logikanya sekarang telah diintegrasikan dan disempurnakan di dalam `gui.py`.
-   `rev1.py`: File revisi atau cadangan, tidak digunakan dalam alur kerja utama.

## Prasyarat

### Perangkat Keras
-   Papan Arduino (misalnya, Arduino Uno).
-   Modul Relay.
-   Webcam.
-   Kabel jumper.

### Perangkat Lunak
-   Python 3.
-   Pustaka Python: `opencv-python`, `mediapipe`, `pyserial`, `tkinter`.
-   Arduino IDE.

## Cara Menjalankan

1.  **Setup Arduino**:
    -   Buka file `smart_coding.ino` di Arduino IDE.
    -   Hubungkan papan Arduino ke komputer Anda.
    -   Pilih Board dan Port yang benar dari menu Tools.
    -   Unggah (upload) sketch ke Arduino.

2.  **Jalankan Aplikasi Python**:
    -   Pastikan semua pustaka Python yang diperlukan telah terinstal.
    -   Jalankan file `gui.py`.
    -   Sebuah jendela akan muncul. Pilih port COM tempat Arduino Anda terhubung dari menu dropdown.
    -   Klik tombol "Confirm and Start".
    -   Jendela kamera akan terbuka. Arahkan tangan Anda ke kamera untuk melakukan gestur.

3.  **Kontrol Relay**:
    -   Tunjukkan **gestur 'V' (2 jari)** untuk menyalakan relay.
    -   Tunjukkan **gestur 3 jari** untuk mematikan relay.
    -   Untuk keluar dari program, tekan tombol 'q' pada jendela kamera.