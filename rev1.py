import cv2
import numpy as np

def find_available_cameras():
    """
    Mencari dan mengembalikan daftar indeks kamera yang tersedia.
    """
    available_cameras = []
    # Coba hingga 10 indeks kamera (kamu bisa sesuaikan jika perlu)
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

def get_camera_name(index):
    """
    Mencoba mendapatkan nama kamera (tidak selalu berhasil untuk semua kamera/driver).
    Ini lebih merupakan tebakan dan mungkin tidak berfungsi pada semua OS/hardware.
    """
    try:
        # CAP_DSHOW adalah backend khusus Windows, bisa coba tanpa ini jika di OS lain
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            # Beberapa properti bisa memberikan info, tapi tidak standar
            backend_name = cap.getBackendName()
            if backend_name:
                return f"Camera {index} (Backend: {backend_name})"
            else:
                return f"Camera {index} (Generic)"
        else:
            return f"Camera {index} (Not Accessible)"
    except Exception as e:
        return f"Camera {index} (Error: {e})"
    finally:
        # Pastikan objek cap ditutup jika sudah dibuat dan terbuka
        if 'cap' in locals() and cap.isOpened():
            cap.release()

def select_camera_with_preview_on_top(camera_indices):
    """
    Menampilkan pratinjau dari setiap kamera dan memungkinkan pengguna memilihnya
    dengan pratinjau muncul di bagian atas.
    """
    if not camera_indices:
        print("Tidak ada kamera yang terdeteksi.")
        return None

    selected_camera_index = None
    active_caps = {} # Menyimpan objek VideoCapture yang aktif untuk pratinjau

    print("\nPilih kamera yang ingin digunakan:")
    print("Tekan angka indeks kamera yang kamu inginkan, lalu Enter.")
    print("Tekan 'q' (di salah satu jendela pratinjau) untuk keluar.")

    # Loop untuk menampilkan pratinjau semua kamera
    # Loop ini akan terus berjalan sampai pengguna memilih kamera atau keluar
    while selected_camera_index is None:
        for idx in camera_indices:
            # Buka kamera jika belum terbuka untuk pratinjau
            if idx not in active_caps:
                active_caps[idx] = cv2.VideoCapture(idx)
                if not active_caps[idx].isOpened():
                    print(f"Gagal membuka kamera {idx}. Melewati...")
                    # Hapus dari daftar jika gagal dibuka
                    if idx in active_caps:
                        active_caps[idx].release()
                        del active_caps[idx]
                    continue # Lanjut ke kamera berikutnya

            ret, frame = active_caps[idx].read()
            if ret:
                # Tambahkan nama/indeks kamera ke frame pratinjau
                camera_name = get_camera_name(idx)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, f"{camera_name} (Tekan '{idx}')", (10, 30), font, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow(f"Pratinjau Kamera {idx}", frame)
            else:
                print(f"Gagal membaca frame dari Kamera {idx}.")

        # Tangani input keyboard. Perhatikan, waitKey bekerja di jendela OpenCV
        key = cv2.waitKey(1) & 0xFF # Ambil input dari jendela OpenCV
        if key == ord('q'):
            print("Memilih keluar dari pemilihan kamera.")
            break # Keluar dari loop pemilihan

        # Ambil input dari konsol untuk pilihan kamera
        # Kita perlu sedikit trik di sini karena cv2.waitKey tidak bagus untuk input angka multiline
        # Pilihan paling mudah adalah meminta input setelah semua pratinjau ditampilkan
        # Atau kita bisa terus memproses cv2.waitKey untuk menekan angka
        
        # Untuk kesederhanaan, kita akan terus menampilkan pratinjau, dan pilihan ada di konsol setelahnya
        # Jika kamu ingin pilihan langsung dari `waitKey`, itu akan lebih kompleks
        # Mari kita coba cara yang lebih mudah untuk input angka dari konsol
        
        # Karena kita ingin pratinjau di atas, kita akan biarkan loop ini berjalan
        # dan meminta input setelah loop pratinjau sedikit berjalan atau secara terpisah
        
        # Opsi 1: Minta input setelah beberapa detik pratinjau ditampilkan
        # (ini kurang interaktif)

        # Opsi 2: Tetap minta input 'q' dari waitKey, dan untuk pilihan angka,
        # kita biarkan pratinjau berjalan, lalu minta input dari terminal
        
        # Untuk demonstrasi, kita akan biarkan pratinjau berjalan, lalu di blok utama kita minta input.
        # Ini berarti pengguna akan melihat pratinjau, lalu kembali ke terminal untuk mengetik angka.
        # Jika kamu mau input angka langsung di jendela OpenCV, itu akan jadi PR selanjutnya!

    # Tutup semua jendela pratinjau dan rilis kamera sebelum meminta input di konsol
    for idx, cap in active_caps.items():
        cap.release()
        cv2.destroyWindow(f"Pratinjau Kamera {idx}")

    # Sekarang, minta input dari konsol setelah pratinjau ditampilkan
    if selected_camera_index is None and camera_indices: # Hanya jika belum dipilih dan ada kamera
        try:
            choice = input("Masukkan indeks kamera yang ingin digunakan (atau 'q' untuk keluar): ").strip()
            if choice.isdigit() and int(choice) in camera_indices:
                selected_camera_index = int(choice)
            elif choice.lower() == 'q':
                print("Memilih keluar.")
                selected_camera_index = None
            else:
                print("Pilihan tidak valid.")
                selected_camera_index = None # Reset atau tandai sebagai tidak valid
        except ValueError:
            print("Input tidak valid.")
            selected_camera_index = None
            
    return selected_camera_index

def run_camera_feed(camera_index):
    """
    Menjalankan feed dari kamera yang dipilih dan memungkinkan penggantian kamera.
    """
    if camera_index is None:
        print("Tidak ada kamera yang dipilih. Keluar.")
        return

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Gagal membuka kamera {camera_index}. Keluar.")
        return

    current_camera_name = get_camera_name(camera_index)
    print(f"\nMenampilkan feed dari: {current_camera_name}")
    print("Tekan 'n' untuk mengganti kamera, 'q' untuk keluar dari feed.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Gagal membaca frame dari {current_camera_name}. Mencoba lagi...")
            break

        # Tampilkan nama kamera di frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, current_camera_name, (10, 30), font, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow("Camera Feed", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):
            cap.release() # Lepaskan kamera saat ini
            cv2.destroyWindow("Camera Feed") # Tutup jendela feed saat ini
            return True # Beri sinyal untuk memilih kamera baru

    cap.release()
    cv2.destroyAllWindows()
    return False # Beri sinyal untuk keluar

if __name__ == "__main__":
    available_cams = find_available_cameras()
    print(f"Kamera yang terdeteksi: {available_cams}")

    while True:
        chosen_cam_idx = select_camera_with_preview_on_top(available_cams)
        
        if chosen_cam_idx is not None:
            if run_camera_feed(chosen_cam_idx):
                # Jika run_camera_feed mengembalikan True, berarti user ingin ganti kamera
                continue
            else:
                # Jika run_camera_feed mengembalikan False, berarti user ingin keluar
                break
        else:
            print("Tidak ada kamera yang dipilih atau terjadi kesalahan/pembatalan. Keluar.")
            break

    print("Aplikasi kamera selesai.")