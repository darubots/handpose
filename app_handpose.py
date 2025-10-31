

import cv2
import mediapipe as mp
import numpy as np
import math
import customtkinter as ctk
from PIL import Image, ImageTk

# --- 1. INISIALISASI MEDIAPIPE ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# --- 2. KELAS UTAMA APLIKASI GUI ---
class HandposeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- A. PENGATURAN JENDELA UTAMA ---
        self.title("Aplikasi Handpose")
        self.geometry("1280x720")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- B. FRAME KIRI (PANEL UI) ---
        self.ui_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.ui_frame.grid(row=0, column=0, sticky="nswe")
        self.ui_frame.grid_propagate(False)
        self.ui_frame.grid_rowconfigure(4, weight=1)

        # Judul Panel UI
        title_label = ctk.CTkLabel(self.ui_frame, text="PANEL KONTROL", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Dropdown Pemilihan Kamera
        cam_label = ctk.CTkLabel(self.ui_frame, text="Pilih Kamera:", anchor="w")
        cam_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.available_cameras = self.get_available_cameras()
        self.camera_names = [f"Kamera {i}" for i in self.available_cameras]
        self.camera_dropdown = ctk.CTkOptionMenu(self.ui_frame, values=self.camera_names, command=self.switch_camera)
        self.camera_dropdown.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Label untuk menampilkan gestur
        self.gesture_label = ctk.CTkLabel(self.ui_frame, text="Gestur: -", font=ctk.CTkFont(size=18))
        self.gesture_label.grid(row=3, column=0, padx=20, pady=20)

        # Label untuk menampilkan jarak
        self.distance_label = ctk.CTkLabel(self.ui_frame, text="Jarak: -", font=ctk.CTkFont(size=18))
        self.distance_label.grid(row=4, column=0, padx=20, pady=20, sticky="n")

        # --- C. FRAME KANAN (VIDEO FEED) ---
        self.video_frame = ctk.CTkFrame(self, corner_radius=0)
        self.video_frame.grid(row=0, column=1, sticky="nswe")
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(fill="both", expand=True)

        # --- D. INISIALISASI KAMERA & LOOP UTAMA ---
        self.cap = None
        if self.available_cameras:
            self.switch_camera(self.camera_names[0])
        else:
            self.video_label.configure(text="Tidak ada kamera ditemukan.")

        self.update_frame()

    def get_available_cameras(self):
        """Mendeteksi dan mengembalikan daftar indeks kamera yang tersedia."""
        available_cameras = []
        for i in range(5):
            cap_test = cv2.VideoCapture(i)
            if cap_test.isOpened():
                available_cameras.append(i)
                cap_test.release()
        return available_cameras

    def switch_camera(self, selected_camera_name):
        """Beralih ke kamera yang dipilih dari dropdown."""
        print(f"Beralih ke {selected_camera_name}")
        if self.cap is not None:
            self.cap.release()
        
        cam_index = int(selected_camera_name.split()[-1])
        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened():
            print(f"Error: Gagal membuka kamera indeks {cam_index}")
            self.video_label.configure(text=f"Gagal membuka {selected_camera_name}")

    def update_frame(self):
        """Loop utama untuk membaca frame, memproses, dan menampilkannya."""
        if self.cap is None or not self.cap.isOpened():
            self.after(1000, self.update_frame) # Coba lagi setelah 1 detik jika kamera tidak ada
            return

        success, frame = self.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return

        frame = cv2.flip(frame, 1)
        
        # Proses deteksi gestur
        processed_frame, gesture_text, distance_text = self.process_gestures(frame.copy())

        # Update label UI
        self.gesture_label.configure(text=f"Gestur: {gesture_text}")
        self.distance_label.configure(text=f"Jarak: {distance_text}")

        # Konversi frame OpenCV ke format yang bisa ditampilkan di CustomTkinter
        img = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        
        self.video_label.configure(image=img_tk)
        self.video_label.image = img_tk # Jaga referensi agar tidak di-garbage collect

        # Panggil fungsi ini lagi setelah 10ms
        self.after(10, self.update_frame)

    def process_gestures(self, frame):
        """Fungsi yang berisi semua logika deteksi gestur MediaPipe."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        gesture_text = "-"
        distance_text = "-"

        if results.multi_hand_landmarks:
            all_landmarks = results.multi_hand_landmarks
            num_hands = len(all_landmarks)

            if num_hands == 2:
                # Logika 2 tangan (disingkat untuk kejelasan)
                gesture_text = self.detect_two_hands(all_landmarks)
                for hand_lms in all_landmarks:
                    mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            elif num_hands == 1:
                # Logika 1 tangan
                gesture_text, distance_text = self.detect_one_hand(all_landmarks[0])
                mp_draw.draw_landmarks(frame, all_landmarks[0], mp_hands.HAND_CONNECTIONS)
        
        return frame, gesture_text, distance_text

    def detect_one_hand(self, hand_landmarks):
        landmarks = hand_landmarks.landmark
        
        # Estimasi Jarak
        wrist_p = landmarks[mp_hands.HandLandmark.WRIST]
        middle_mcp_p = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        pixel_width = math.sqrt((wrist_p.x - middle_mcp_p.x)**2 + (wrist_p.y - middle_mcp_p.y)**2)
        distance_cm = (0.3 * 30) / pixel_width if pixel_width > 0 else 0
        distance_text = f"{distance_cm:.2f} cm"

        # Deteksi Jari
        tip_ids = [4, 8, 12, 16, 20]
        fingers_up = []
        if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        for i in range(1, 5):
            if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        total_fingers = sum(fingers_up)

        # Pengenalan Gestur
        dist_thumb_index = math.sqrt((landmarks[tip_ids[0]].x - landmarks[tip_ids[1]].x)**2 + (landmarks[tip_ids[0]].y - landmarks[tip_ids[1]].y)**2)
        if dist_thumb_index < 0.05 and total_fingers >= 3:
            return "Pose OK", distance_text
        elif total_fingers == 0:
            return "Pose Kepal", distance_text
        elif total_fingers == 1 and fingers_up[1]:
            return "1 Jari", distance_text
        elif total_fingers == 2 and fingers_up[1] and fingers_up[2]:
            return "Pose V (2 Jari)", distance_text
        elif total_fingers == 3 and fingers_up[1] and fingers_up[2] and fingers_up[3]:
            return "3 Jari", distance_text
        elif total_fingers == 4 and fingers_up[1] and fingers_up[2] and fingers_up[3] and fingers_up[4]:
            return "4 Jari", distance_text
        elif total_fingers == 5:
            return "5 Jari (Terbuka)", distance_text
        return "Tidak Dikenali", distance_text

    def detect_two_hands(self, all_landmarks):
        h1_lms = all_landmarks[0].landmark
        h2_lms = all_landmarks[1].landmark
        h1_index_tip = h1_lms[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        h2_index_tip = h2_lms[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        h1_thumb_tip = h1_lms[mp_hands.HandLandmark.THUMB_TIP]
        h2_thumb_tip = h2_lms[mp_hands.HandLandmark.THUMB_TIP]

        if (math.sqrt((h1_index_tip.x - h2_index_tip.x)**2 + (h1_index_tip.y - h2_index_tip.y)**2) < 0.1 and
            math.sqrt((h1_thumb_tip.x - h2_thumb_tip.x)**2 + (h1_thumb_tip.y - h2_thumb_tip.y)**2) < 0.1 and
            h1_index_tip.y < h1_thumb_tip.y and h2_index_tip.y < h2_thumb_tip.y):
            return "Pose Hati (Love)"
        
        h1_dist = math.sqrt((h1_index_tip.x - h1_thumb_tip.x)**2 + (h1_index_tip.y - h1_thumb_tip.y)**2)
        h2_dist = math.sqrt((h2_index_tip.x - h2_thumb_tip.x)**2 + (h2_index_tip.y - h2_thumb_tip.y)**2)
        if h1_dist < 0.1 and h2_dist < 0.1:
            return "Pose Lingkaran Besar"
        return "Dua Tangan"

    def on_closing(self):
        """Fungsi yang dipanggil saat jendela ditutup."""
        print("Menutup aplikasi...")
        if self.cap is not None:
            self.cap.release()
        self.destroy()

# --- 3. JALANKAN APLIKASI ---
if __name__ == "__main__":
    app = HandposeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # Pastikan kamera dilepaskan saat ditutup
    app.mainloop()
