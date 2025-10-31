import cv2
import mediapipe as mp
import serial
import time

# --- Konfigurasi Serial Arduino ---
# Ganti 'COM3' dengan port serial Arduino kamu (misal: '/dev/ttyACM0' di Linux/Mac)
# Pastikan baud rate (9600) sama dengan yang diatur di kode Arduino
try:
    arduino = serial.Serial('COM9', 9600, timeout=1)
    print("Koneksi serial ke Arduino berhasil!")
    time.sleep(2) # Beri waktu Arduino untuk reset setelah koneksi serial
except serial.SerialException:
    print("Gagal terhubung ke Arduino. Pastikan port serial benar dan Arduino terhubung.")
    arduino = None # Set arduino ke None jika koneksi gagal

# --- Inisialisasi MediaPipe Hands ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,         # Deteksi hanya satu tangan
    min_detection_confidence=0.7, # Tingkat kepercayaan deteksi tangan
    min_tracking_confidence=0.7  # Tingkat kepercayaan pelacakan tangan
)
mp_draw = mp.solutions.drawing_utils

# --- Inisialisasi Kamera ---
cap = cv2.VideoCapture(0) # 0 adalah ID kamera default, ganti jika punya lebih dari satu kamera

# Variabel untuk melacak status jari sebelumnya
prev_hand_state = None # 'open' atau 'closed'

def get_hand_state(hand_landmarks):
    # Mengidentifikasi apakah jari-jari terbuka atau tertutup
    # Kita akan memeriksa ujung jari (tip) dan sendi di bawahnya (PIP)
    # Indeks landmark jari tangan:
    # Jempol: 4 (tip), 3 (PIP)
    # Telunjuk: 8 (tip), 7 (PIP)
    # Tengah: 12 (tip), 11 (PIP)
    # Cincin: 16 (tip), 15 (PIP)
    # Kelingking: 20 (tip), 19 (PIP)

    # Logika sederhana: jika ujung jari (tip) lebih tinggi (y lebih kecil) dari sendi PIP-nya,
    # maka jari dianggap terbuka. Khusus jempol, periksa sumbu x relatif.

    # Ambang batas untuk jempol (perlu disesuaikan jika tidak bekerja dengan baik)
    thumb_threshold_x = 0.05 # Perbedaan koordinat x yang cukup besar untuk jempol

    # Memeriksa jari-jari selain jempol (jari 8, 12, 16, 20)
    # Jika ujung jari (tip) lebih tinggi dari sendi PIP-nya, jari dianggap terbuka
    fingers_open = 0
    # Jari telunjuk (8 vs 7)
    if hand_landmarks.landmark[8].y < hand_landmarks.landmark[7].y:
        fingers_open += 1
    # Jari tengah (12 vs 11)
    if hand_landmarks.landmark[12].y < hand_landmarks.landmark[11].y:
        fingers_open += 1
    # Jari manis (16 vs 15)
    if hand_landmarks.landmark[16].y < hand_landmarks.landmark[15].y:
        fingers_open += 1
    # Jari kelingking (20 vs 19)
    if hand_landmarks.landmark[20].y < hand_landmarks.landmark[19].y:
        fingers_open += 1

    # Memeriksa jempol (4 vs 3) - logikanya sedikit berbeda, berdasarkan sumbu X
    # Jika jempol terbuka, koordinat x ujung jempol (4) biasanya akan lebih jauh dari sendi jempol (3)
    # dalam arah yang berlawanan dengan telapak tangan
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x - thumb_threshold_x or \
       hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x + thumb_threshold_x:
        # Ini adalah logika yang sangat disederhanakan.
        # Untuk akurasi lebih tinggi, perlu mempertimbangkan orientasi tangan.
        # Untuk sekarang, kita asumsikan jempol terbuka jika x-nya jauh dari basisnya.
        fingers_open += 1


    # Jika semua 5 jari terbuka
    if fingers_open >= 4: # Menggunakan 4 atau 5 untuk toleransi
        return 'open'
    else:
        return 'closed'

print("Program Python dimulai. Tekan 'q' untuk keluar.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Gagal membaca frame dari kamera.")
        break

    # Balik gambar secara horizontal untuk tampilan seperti cermin
    image = cv2.flip(image, 1)

    # Ubah warna gambar dari BGR ke RGB (MediaPipe membutuhkan RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Proses gambar untuk deteksi tangan
    results = hands.process(image_rgb)

    # Gambar landmark jika tangan terdeteksi
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            current_hand_state = get_hand_state(hand_landmarks)

            if current_hand_state != prev_hand_state:
                if current_hand_state == 'open':
                    command = 'O'
                    status_text = "Tangan Terbuka (Servo 90)"
                else:
                    command = 'C'
                    status_text = "Tangan Tertutup (Servo 0)"

                print(f"Mengirim '{command}' ke Arduino. Status: {status_text}")
                if arduino:
                    try:
                        arduino.write(command.encode('utf-8'))
                    except serial.SerialException as e:
                        print(f"Error mengirim data serial: {e}")
                        arduino = None # Matikan koneksi jika ada error
                prev_hand_state = current_hand_state
            else:
                if prev_hand_state == 'open':
                    status_text = "Tangan Terbuka (Servo 90)"
                elif prev_hand_state == 'closed':
                    status_text = "Tangan Tertutup (Servo 0)"
                else:
                    status_text = "Menunggu deteksi tangan..."

    else:
        status_text = "Tidak ada tangan terdeteksi."
        # Reset state jika tangan tidak terdeteksi untuk menghindari pengiriman ulang perintah
        if prev_hand_state is not None:
            print("Tangan hilang, reset status.")
            prev_hand_state = None

    # Tampilkan status di jendela kamera
    cv2.putText(image, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


    # Tampilkan gambar
    cv2.imshow('Hand Pose Detection', image)

    # Keluar dari loop jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan sumber daya
if arduino:
    arduino.close()
    print("Koneksi serial ditutup.")
cap.release()
cv2.destroyAllWindows()
print("Program Python selesai.")