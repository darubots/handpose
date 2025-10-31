# =================================================================================
# APLIKASI DETEKSI GESTUR TANGAN (HANDPOSE)
# Dibuat oleh: Tim Daru Bot
# Developer: izhardevelops (https://github.com/izhardevelops)
#
# Deskripsi:
# Aplikasi ini menggunakan webcam untuk mendeteksi dan mengenali berbagai gestur 
# tangan secara real-time. Tampilan dibagi menjadi dua: panel informasi di kiri 
# dan feed webcam di kanan.
#
# Fitur:
# - Deteksi 1 & 2 tangan.
# - Pengenalan gestur: 1-5 jari, kepal, OK, hati (2 tangan), lingkaran (2 tangan).
# - Estimasi jarak tangan dari kamera.
# - UI minimalis dan modern.
# - Kompatibilitas CPU/GPU otomatis oleh MediaPipe.
# - Deteksi kamera yang lebih robust untuk berbagai perangkat.
#
# Library yang dibutuhkan:
# - opencv-python : Untuk akses kamera dan pemrosesan gambar.
# - mediapipe     : Untuk model machine learning deteksi tangan.
# - numpy         : Untuk manipulasi array dan gambar.
#
# Cara Menjalankan:
# 1. Pastikan Python dan pip sudah terinstal.
# 2. Buka terminal/CMD, lalu install library: pip install opencv-python mediapipe numpy
# 3. Jalankan script ini: python app_handpose.py
# =================================================================================

import cv2
import mediapipe as mp
import numpy as np
import math

# --- 1. INISIALISASI ---

# Inisialisasi MediaPipe Hands.
# - max_num_hands: Maksimal tangan yang dideteksi (kita set 2).
# - min_detection_confidence: Ambang batas kepercayaan minimum untuk deteksi awal.
# - min_tracking_confidence: Ambang batas kepercayaan minimum untuk tracking setelah deteksi awal.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils # Utilitas untuk menggambar landmark tangan.

# --- 2. FUNGSI BANTU ---

def calculate_distance(p1, p2):
    """Menghitung jarak Euclidean antara dua titik landmark."""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def find_available_camera(max_cameras_to_check=3):
    """
    Mencari dan mengembalikan indeks kamera yang tersedia.
    Ini membuat aplikasi lebih kompatibel di berbagai laptop.
    """
    for i in range(max_cameras_to_check - 1, -1, -1):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Kamera ditemukan di indeks {i}.")
            return cap
    print("Error: Tidak ada kamera yang ditemukan.")
    return None

# --- 3. SETUP KAMERA ---

# Cari kamera yang tersedia secara otomatis.
cap = find_available_camera()
if cap is None:
    exit()

# --- 4. LOOP UTAMA APLIKASI ---

while True:
    # Baca frame dari kamera.
    success, frame = cap.read()
    if not success:
        print("Error: Tidak bisa membaca frame dari kamera.")
        break

    # Balik frame secara horizontal (efek cermin) agar lebih intuitif.
    frame = cv2.flip(frame, 1)
    
    # Konversi warna frame dari BGR (OpenCV) ke RGB (MediaPipe).
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Proses frame untuk mendeteksi tangan.
    results = hands.process(frame_rgb)

    # Dapatkan tinggi dan lebar frame untuk membuat UI.
    frame_height, frame_width, _ = frame.shape
    
    # Buat panel UI hitam di sebelah kiri. Ukurannya adaptif dengan tinggi frame.
    ui_panel = np.zeros((frame_height, 400, 3), dtype=np.uint8)
    
    # Teks default jika tidak ada tangan yang terdeteksi.
    gesture_text = "Tidak ada tangan"
    distance_text = "Jarak: -"

    # --- 5. LOGIKA DETEKSI GESTUR ---

    if results.multi_hand_landmarks:
        all_landmarks = results.multi_hand_landmarks
        num_hands = len(all_landmarks)

        # --- A. Logika untuk Gestur DUA TANGAN ---
        if num_hands == 2:
            # Ambil landmark untuk tangan pertama dan kedua.
            hand1_lms = all_landmarks[0].landmark
            hand2_lms = all_landmarks[1].landmark

            # Deteksi Hati (Love): Ujung jari telunjuk kedua tangan bertemu di atas, 
            # dan ibu jari bertemu di bawah membentuk 'V'.
            h1_index_tip = hand1_lms[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h2_index_tip = hand2_lms[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h1_thumb_tip = hand1_lms[mp_hands.HandLandmark.THUMB_TIP]
            h2_thumb_tip = hand2_lms[mp_hands.HandLandmark.THUMB_TIP]

            if (calculate_distance(h1_index_tip, h2_index_tip) < 0.1 and
                calculate_distance(h1_thumb_tip, h2_thumb_tip) < 0.1 and
                h1_index_tip.y < h1_thumb_tip.y and h2_index_tip.y < h2_thumb_tip.y):
                gesture_text = "Pose Hati (Love)"

            # Deteksi Lingkaran Besar: Kedua tangan membentuk gestur 'OK' dan saling berdekatan.
            else:
                h1_dist = calculate_distance(h1_index_tip, h1_thumb_tip)
                h2_dist = calculate_distance(h2_index_tip, h2_thumb_tip)
                if h1_dist < 0.1 and h2_dist < 0.1:
                     gesture_text = "Pose Lingkaran Besar"
            
            # Gambar landmark untuk kedua tangan.
            for hand_lms in all_landmarks:
                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

        # --- B. Logika untuk Gestur SATU TANGAN ---
        elif num_hands == 1:
            hand_landmarks = all_landmarks[0]
            
            # Gambar landmark pada frame.
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            
            # Hitung estimasi jarak berdasarkan lebar tangan pada frame.
            # Ini adalah estimasi kasar dan mungkin perlu kalibrasi.
            wrist_p = landmarks[mp_hands.HandLandmark.WRIST]
            middle_mcp_p = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            pixel_width = calculate_distance(wrist_p, middle_mcp_p)
            
            if pixel_width > 0:
                # Formula sederhana: (Lebar_Piksel_Referensi * Jarak_Referensi) / Lebar_Piksel_Saat_Ini
                distance_cm = (0.3 * 30) / pixel_width 
                distance_text = f"Jarak: {distance_cm:.2f} cm"

            # Logika deteksi jari terangkat.
            tip_ids = [4, 8, 12, 16, 20] # ID untuk ujung jari: Ibu jari, Telunjuk, Tengah, Manis, Kelingking.
            fingers_up = []

            # Ibu Jari: Cek posisi horizontal (berbeda dari jari lain).
            # Asumsi tangan kanan: ibu jari di kiri jika terbuka.
            if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
                fingers_up.append(1)
            else:
                fingers_up.append(0)

            # Jari Lainnya: Cek posisi vertikal. Jari dianggap 'up' jika ujungnya lebih tinggi dari sendi di bawahnya.
            for i in range(1, 5):
                if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y:
                    fingers_up.append(1)
                else:
                    fingers_up.append(0)
            
            total_fingers = sum(fingers_up)

            # Kenali gestur berdasarkan jumlah dan posisi jari.
            dist_thumb_index = calculate_distance(landmarks[tip_ids[0]], landmarks[tip_ids[1]])
            
            if dist_thumb_index < 0.05 and total_fingers >= 3 and fingers_up[2] and fingers_up[3] and fingers_up[4]:
                 gesture_text = "Pose OK"
            elif total_fingers == 0:
                gesture_text = "Pose Kepal"
            elif total_fingers == 1 and fingers_up[1]:
                gesture_text = "1 Jari"
            elif total_fingers == 2 and fingers_up[1] and fingers_up[2]:
                gesture_text = "Pose V (2 Jari)"
            elif total_fingers == 3 and fingers_up[1] and fingers_up[2] and fingers_up[3]:
                gesture_text = "3 Jari"
            elif total_fingers == 4 and fingers_up[1] and fingers_up[2] and fingers_up[3] and fingers_up[4]:
                gesture_text = "4 Jari"
            elif total_fingers == 5:
                gesture_text = "5 Jari (Terbuka)"
            else:
                gesture_text = "Tidak Dikenali"

    # --- 6. TAMPILKAN UI & HASIL ---

    # Tampilkan semua teks informasi di panel UI sebelah kiri.
    cv2.putText(ui_panel, "DETEKSI GESTUR", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(ui_panel, gesture_text, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.putText(ui_panel, distance_text, (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(ui_panel, "Tekan 'q' untuk keluar", (30, frame_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    # Gabungkan panel UI dengan frame kamera secara horizontal.
    combined_frame = np.hstack((ui_panel, frame))

    # Tampilkan jendela aplikasi.
    cv2.imshow("Aplikasi Handpose", combined_frame)

    # Hentikan loop jika tombol 'q' ditekan.
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# --- 7. BERSIHKAN ---

# Lepaskan resource kamera dan tutup semua jendela OpenCV.
print("Menutup aplikasi...")
cap.release()
cv2.destroyAllWindows()