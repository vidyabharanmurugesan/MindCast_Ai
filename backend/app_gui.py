"""
Desktop User Interface (GUI) for AI Mental Health Assistant Backend.
Built in Python using Tkinter and TTK with modern dark theme aesthetics.
"""
import sys
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService
from app.services.fusion_service import FusionEngineService
from app.services.assessment_service import AssessmentService
from app.services.report_generator_service import ReportGeneratorService
from app.services.dataset_service import DatasetService
from app.services.auth_service import AuthService


class MentalHealthAIGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI Mental Health Assistant - Clinical Dashboard")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0F172A")

        # Initialize Services
        self.auth_service = AuthService()
        self.face_service = FaceEmotionService()
        self.voice_service = VoiceEmotionService()
        self.fusion_service = FusionEngineService()
        self.assessment_service = AssessmentService()
        self.report_service = ReportGeneratorService()
        self.dataset_service = DatasetService()

        self.current_user = None
        self.current_session_id = None
        self.last_face_pred = None
        self.last_voice_pred = None

        self._setup_styles()
        self._show_loading_screen()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors
        self.bg_dark = "#0F172A"
        self.card_bg = "#1E293B"
        self.accent_blue = "#3B82F6"
        self.accent_green = "#10B981"
        self.text_light = "#F8FAFC"
        self.text_muted = "#94A3B8"

        style.configure("TFrame", background=self.bg_dark)
        style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        style.configure("Header.TLabel", background=self.bg_dark, foreground=self.text_light, font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background=self.card_bg, foreground=self.accent_blue, font=("Segoe UI", 13, "bold"))
        style.configure("CardText.TLabel", background=self.card_bg, foreground=self.text_light, font=("Segoe UI", 10))
        style.configure("MutedText.TLabel", background=self.card_bg, foreground=self.text_muted, font=("Segoe UI", 9))
        
        style.configure("Primary.TButton", background=self.accent_blue, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Primary.TButton", background=[("active", "#2563EB")])

        style.configure("Success.TButton", background=self.accent_green, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Success.TButton", background=[("active", "#059669")])

    def _show_loading_screen(self):
        # Clear root window
        for widget in self.root.winfo_children():
            widget.destroy()

        load_frame = ttk.Frame(self.root, style="Card.TFrame", padding=40)
        load_frame.place(relx=0.5, rely=0.5, anchor="center", width=450)

        ttk.Label(load_frame, text="🧠 AI Mental Health Assistant", style="Header.TLabel").pack(pady=(0, 10))
        ttk.Label(load_frame, text="Initializing Clinical Suite Modules...", style="SubHeader.TLabel").pack(pady=(0, 15))

        progress = ttk.Progressbar(load_frame, mode="indeterminate", length=350)
        progress.pack(fill="x", pady=15)
        progress.start(10)

        ttk.Label(load_frame, text="Loading Neural Models & Database...", style="MutedText.TLabel").pack(pady=(10, 0))

        # Schedule transition to login screen after 1.5 seconds (1500 ms)
        self.root.after(1500, self._build_auth_screen)

    def _build_auth_screen(self):
        # Clear root window
        for widget in self.root.winfo_children():
            widget.destroy()

        self.auth_frame = ttk.Frame(self.root, style="Card.TFrame", padding=30)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center", width=420)

        # Login View Title
        ttk.Label(self.auth_frame, text="🧠 Clinical Suite Login", style="Header.TLabel").pack(pady=(0, 5))
        ttk.Label(self.auth_frame, text="Enter clinician credentials to continue", style="MutedText.TLabel").pack(pady=(0, 20))

        ttk.Label(self.auth_frame, text="Email Address:", style="CardText.TLabel").pack(anchor="w", pady=(5, 2))
        self.ent_login_email = ttk.Entry(self.auth_frame, font=("Segoe UI", 10))
        self.ent_login_email.insert(0, "doctor@hospital.com")
        self.ent_login_email.pack(fill="x", pady=(0, 10))

        ttk.Label(self.auth_frame, text="Password:", style="CardText.TLabel").pack(anchor="w", pady=(5, 2))
        self.ent_login_pass = ttk.Entry(self.auth_frame, show="•", font=("Segoe UI", 10))
        self.ent_login_pass.insert(0, "doctor123")
        self.ent_login_pass.pack(fill="x", pady=(0, 15))

        btn_login = ttk.Button(self.auth_frame, text="🔐 Log In", style="Primary.TButton", command=self._handle_login)
        btn_login.pack(fill="x", pady=(5, 10))

        btn_goto_signup = ttk.Button(self.auth_frame, text="📝 Create New Account (Sign Up)", style="Success.TButton", command=self._switch_to_signup)
        btn_goto_signup.pack(fill="x")

    def _switch_to_signup(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.auth_frame = ttk.Frame(self.root, style="Card.TFrame", padding=30)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center", width=440)

        ttk.Label(self.auth_frame, text="📋 Register Clinician Account", style="Header.TLabel").pack(pady=(0, 5))
        ttk.Label(self.auth_frame, text="Create your medical staff login", style="MutedText.TLabel").pack(pady=(0, 15))

        ttk.Label(self.auth_frame, text="Full Name:", style="CardText.TLabel").pack(anchor="w", pady=(2, 2))
        self.ent_reg_name = ttk.Entry(self.auth_frame, font=("Segoe UI", 10))
        self.ent_reg_name.pack(fill="x", pady=(0, 8))

        ttk.Label(self.auth_frame, text="Email Address:", style="CardText.TLabel").pack(anchor="w", pady=(2, 2))
        self.ent_reg_email = ttk.Entry(self.auth_frame, font=("Segoe UI", 10))
        self.ent_reg_email.pack(fill="x", pady=(0, 8))

        ttk.Label(self.auth_frame, text="Password:", style="CardText.TLabel").pack(anchor="w", pady=(2, 2))
        self.ent_reg_pass = ttk.Entry(self.auth_frame, show="•", font=("Segoe UI", 10))
        self.ent_reg_pass.pack(fill="x", pady=(0, 15))

        btn_signup = ttk.Button(self.auth_frame, text="✅ Complete Registration", style="Success.TButton", command=self._handle_signup)
        btn_signup.pack(fill="x", pady=(5, 10))

        btn_back_login = ttk.Button(self.auth_frame, text="⬅ Back to Login", style="Primary.TButton", command=self._build_auth_screen)
        btn_back_login.pack(fill="x")

    def _handle_login(self):
        email = self.ent_login_email.get().strip()
        password = self.ent_login_pass.get().strip()

        res = self.auth_service.login_user(email, password)
        if res["success"]:
            self.current_user = res["user"]
            messagebox.showinfo("Login Success", f"Welcome back, {res['user']['full_name']}!")
            self._build_ui()
        else:
            messagebox.showerror("Login Failed", res["message"])

    def _handle_signup(self):
        name = self.ent_reg_name.get().strip()
        email = self.ent_reg_email.get().strip()
        password = self.ent_reg_pass.get().strip()

        if not name or not email or not password:
            messagebox.showwarning("Incomplete Form", "Please fill in all registration fields.")
            return

        res = self.auth_service.register_user(email=email, password=password, full_name=name, role="Doctor / Physician")
        if res["success"]:
            self.current_user = res["user"]
            messagebox.showinfo("Registration Success", res["message"])
            self._build_ui()
        else:
            messagebox.showerror("Registration Failed", res["message"])

    def _build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Header Bar
        header_frame = ttk.Frame(self.root, padding=15)
        header_frame.pack(fill="x")
        
        title_label = ttk.Label(header_frame, text="🧠 AI Mental Health Assistant - Clinical Suite", style="Header.TLabel")
        title_label.pack(side="left")

        user_info = f"Logged in: {self.current_user['full_name']} ({self.current_user['role']})" if self.current_user else ""
        lbl_user = ttk.Label(header_frame, text=user_info, style="CardText.TLabel")
        lbl_user.pack(side="right", padx=10)

        btn_logout = ttk.Button(header_frame, text="🚪 Logout", style="Primary.TButton", command=self._build_auth_screen)
        btn_logout.pack(side="right")

        # Main Notebook Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab 1: Live Assessment & Prediction
        self.tab_assess = ttk.Frame(notebook, padding=15)
        notebook.add(self.tab_assess, text=" Live Assessment ")

        # Tab 2: Dataset Inspector
        self.tab_datasets = ttk.Frame(notebook, padding=15)
        notebook.add(self.tab_datasets, text=" Dataset Inspector ")

        # Tab 3: Model Training
        self.tab_train = ttk.Frame(notebook, padding=15)
        notebook.add(self.tab_train, text=" AI Model Training ")

        self._build_assessment_tab()
        self._build_dataset_tab()
        self._build_training_tab()

    def _build_assessment_tab(self):
        # Left Panel - Inputs
        left_panel = ttk.Frame(self.tab_assess, style="Card.TFrame", padding=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ttk.Label(left_panel, text="1. Clinical Session Control", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 5))

        self.btn_start = ttk.Button(left_panel, text="🚀 Start New Assessment Session", style="Primary.TButton", command=self._start_session)
        self.btn_start.pack(fill="x", pady=5)

        self.lbl_session = ttk.Label(left_panel, text="Session ID: No active session", style="MutedText.TLabel")
        self.lbl_session.pack(anchor="w", pady=5)

        ttk.Separator(left_panel).pack(fill="x", pady=10)

        # Patient Details Section
        ttk.Label(left_panel, text="2. Patient Details", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 5))

        ttk.Label(left_panel, text="Patient ID:", style="CardText.TLabel").pack(anchor="w")
        self.ent_patient_id = ttk.Entry(left_panel)
        self.ent_patient_id.insert(0, "PAT-1002")
        self.ent_patient_id.pack(fill="x", pady=(0, 5))

        ttk.Label(left_panel, text="Patient Name:", style="CardText.TLabel").pack(anchor="w")
        self.ent_patient_name = ttk.Entry(left_panel)
        self.ent_patient_name.insert(0, "Jane Doe")
        self.ent_patient_name.pack(fill="x", pady=(0, 5))

        detail_frame = ttk.Frame(left_panel, style="Card.TFrame")
        detail_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(detail_frame, text="Age:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.ent_patient_age = ttk.Entry(detail_frame, width=8)
        self.ent_patient_age.insert(0, "32")
        self.ent_patient_age.grid(row=0, column=1, padx=(0, 15))

        ttk.Label(detail_frame, text="Gender:", style="CardText.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.cmb_patient_gender = ttk.Combobox(detail_frame, values=["Female", "Male", "Other"], width=10)
        self.cmb_patient_gender.set("Female")
        self.cmb_patient_gender.grid(row=0, column=3)

        ttk.Separator(left_panel).pack(fill="x", pady=10)

        ttk.Label(left_panel, text="3. Emotion Media Inputs", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 5))


        btn_face = ttk.Button(left_panel, text="📷 Upload Face Image", style="Primary.TButton", command=self._upload_face_image)
        btn_face.pack(fill="x", pady=5)

        btn_voice = ttk.Button(left_panel, text="🎙️ Upload Voice Audio (.wav)", style="Primary.TButton", command=self._upload_voice_audio)
        btn_voice.pack(fill="x", pady=5)

        ttk.Separator(left_panel).pack(fill="x", pady=10)

        btn_finish = ttk.Button(left_panel, text="📄 Finish Session & Generate PDF Report", style="Success.TButton", command=self._finish_session)
        btn_finish.pack(fill="x", pady=10)

    # Right Panel - Predictions & Fusion Matrix Output
        right_panel = ttk.Frame(self.tab_assess, style="Card.TFrame", padding=15)
        right_panel.pack(side="right", fill="both", expand=True)

        ttk.Label(right_panel, text="Clinical Fusion Results", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))

        self.txt_results = tk.Text(right_panel, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), relief="flat", padx=10, pady=10)
        self.txt_results.pack(fill="both", expand=True)
        self.txt_results.insert("end", "Clinical multi-modal predictions will appear here upon media upload...\n")

    def _start_session(self):
        pid = self.ent_patient_id.get().strip() or "PAT-1002"
        session = self.assessment_service.start_session(patient_id=pid)
        self.current_session_id = session["session_id"]
        self.lbl_session.config(text=f"Active Session: {self.current_session_id}")
        messagebox.showinfo("Session Started", f"Assessment Session '{self.current_session_id}' initialized.")

    def _capture_live_face_photo(self):
        try:
            import cv2
            cap = None
            for cam_idx in [0, 1, -1]:
                temp_cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
                if temp_cap.isOpened():
                    ret, test_frame = temp_cap.read()
                    if ret and test_frame is not None:
                        cap = temp_cap
                        break
                    temp_cap.release()

            if cap is None:
                for cam_idx in [0, 1]:
                    temp_cap = cv2.VideoCapture(cam_idx)
                    if temp_cap.isOpened():
                        ret, test_frame = temp_cap.read()
                        if ret and test_frame is not None:
                            cap = temp_cap
                            break
                        temp_cap.release()

            if cap is None or not cap.isOpened():
                messagebox.showwarning("Camera Error", "No working webcam found.\n\nPlease check camera permissions or use '📷 Upload Face Image'.")
                return

            # Build Tkinter Native Camera Capture Window
            cam_win = tk.Toplevel(self.root)
            cam_win.title("📷 Live Patient Camera Feed")
            cam_win.geometry("680x560")
            cam_win.configure(bg="#0F172A")
            cam_win.grab_set()

            ttk.Label(cam_win, text="🎥 Patient Live Webcam Feed", style="SubHeader.TLabel").pack(pady=10)

            video_label = ttk.Label(cam_win)
            video_label.pack(padx=10, pady=5)

            captured_container = {"frame": None, "active": True}

            def close_cam():
                captured_container["active"] = False
                cap.release()
                cam_win.destroy()

            def snap_photo():
                ret, frame = cap.read()
                if ret and frame is not None:
                    captured_container["frame"] = frame
                close_cam()

            btn_frame = ttk.Frame(cam_win, style="Card.TFrame")
            btn_frame.pack(fill="x", pady=10, padx=20)

            btn_snap = ttk.Button(btn_frame, text="📸 Take Patient Photo", style="Success.TButton", command=snap_photo)
            btn_snap.pack(side="left", expand=True, fill="x", padx=5)

            btn_cancel = ttk.Button(btn_frame, text="❌ Cancel", style="Primary.TButton", command=close_cam)
            btn_cancel.pack(side="right", expand=True, fill="x", padx=5)

            cam_win.protocol("WM_DELETE_WINDOW", close_cam)

            def update_stream():
                if not captured_container["active"]:
                    return
                ret, frame = cap.read()
                if ret and frame is not None:
                    cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv2_img)
                    img = img.resize((640, 420), Image.BILINEAR)
                    imgtk = ImageTk.PhotoImage(image=img)
                    video_label.imgtk = imgtk
                    video_label.configure(image=imgtk)
                cam_win.after(30, update_stream)

            update_stream()
            self.root.wait_window(cam_win)

            captured_frame = captured_container["frame"]
            if captured_frame is not None:
                success, encoded_img = cv2.imencode(".png", captured_frame)
                if success:
                    img_bytes = encoded_img.tobytes()
                    pred = self.face_service.predict_emotion(img_bytes)
                    self.last_face_pred = pred

                    self.txt_results.insert("end", f"\n[Live Patient Camera Capture Prediction]: {pred['emotion']} ({pred['confidence']}%)\n")
                    for emo, prob in pred['probabilities'].items():
                        self.txt_results.insert("end", f"  - {emo:<10}: {prob*100:>5.1f}%\n")
                    messagebox.showinfo("Photo Captured", f"Live photo captured successfully!\nDominant Emotion: {pred['emotion']} ({pred['confidence']}%)")
        except Exception as e:
            messagebox.showerror("Camera Exception", f"Error accessing webcam: {str(e)}")

    def _upload_face_image(self):
        fpath = filedialog.askopenfilename(title="Select Face Image", filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not fpath:
            return

        with open(fpath, "rb") as f:
            img_bytes = f.read()

        pred = self.face_service.predict_emotion(img_bytes)
        self.last_face_pred = pred

        self.txt_results.insert("end", f"\n[Face Prediction]: {pred['emotion']} ({pred['confidence']}%\n")
        for emo, prob in pred['probabilities'].items():
            self.txt_results.insert("end", f"  - {emo:<10}: {prob*100:>5.1f}%\n")

    def _upload_voice_audio(self):
        fpath = filedialog.askopenfilename(title="Select Voice Audio", filetypes=[("Audio WAV", "*.wav")])
        if not fpath:
            return

        pred = self.voice_service.predict_emotion_from_file(fpath)
        self.last_voice_pred = pred

        self.txt_results.insert("end", f"\n[Voice Prediction]: {pred['emotion']} ({pred['confidence']}%)\n")
        for emo, prob in pred['probabilities'].items():
            self.txt_results.insert("end", f"  - {emo:<10}: {prob*100:>5.1f}%\n")

    def _finish_session(self):
        if not self.current_session_id:
            messagebox.showwarning("Warning", "Please start an assessment session first.")
            return

        patient_details = {
            "patient_id": self.ent_patient_id.get().strip() or "PAT-1002",
            "name": self.ent_patient_name.get().strip() or "Jane Doe",
            "age": int(self.ent_patient_age.get().strip()) if self.ent_patient_age.get().strip().isdigit() else 32,
            "gender": self.cmb_patient_gender.get().strip() or "Female",
            "hospital": "MindMate AI",
            "attending_physician": self.current_user["full_name"] if self.current_user else "Dr. Sarah Jenkins, MD"
        }

        session_data = self.assessment_service.get_session(self.current_session_id)

        # Get latest predictions from session if recorded, else fallback to GUI last prediction or default
        face = session_data["face_predictions"][-1] if session_data.get("face_predictions") else (self.last_face_pred or {"emotion": "Happy", "confidence": 95.0})
        voice = session_data["voice_predictions"][-1] if session_data.get("voice_predictions") else (self.last_voice_pred or {"emotion": "Happy", "confidence": 90.0})

        fused = self.fusion_service.fuse_predictions(face, voice)
        session_data["fused_result"] = fused

        report = self.report_service.generate_report(session_data, patient_details=patient_details)

        self.txt_results.insert("end", "\n================ CLINICAL REPORT GENERATED ================\n")
        self.txt_results.insert("end", f" Report ID          : {report['report_id']}\n")
        self.txt_results.insert("end", f" Session ID         : {session_data.get('session_id')}\n")
        self.txt_results.insert("end", f" Patient ID         : {patient_details['patient_id']}\n")
        self.txt_results.insert("end", f" Patient Name       : {patient_details['name']}\n")
        self.txt_results.insert("end", f" Age / Gender       : {patient_details['age']} / {patient_details['gender']}\n")
        self.txt_results.insert("end", f" Physician          : {patient_details['attending_physician']}\n")
        self.txt_results.insert("end", " ---------------------------------------------------------\n")
        self.txt_results.insert("end", f" Overall Emotion    : {fused.get('overall_emotion', 'N/A')}\n")
        self.txt_results.insert("end", f" Stress Score       : {fused.get('stress_score', 0)} / 100\n")
        self.txt_results.insert("end", f" Mental Health Score: {fused.get('mental_health_score', 100)} / 100\n")
        self.txt_results.insert("end", f" Risk Level         : {fused.get('risk_level', 'LOW')}\n")
        self.txt_results.insert("end", f" Model Confidence   : {fused.get('confidence', 0)}%\n")
        self.txt_results.insert("end", " ---------------------------------------------------------\n")
        self.txt_results.insert("end", f" Clinical Observation:\n {fused.get('doctor_observation', 'No observation recorded.')}\n")
        self.txt_results.insert("end", " ---------------------------------------------------------\n")
        self.txt_results.insert("end", f" PDF Report Path    : {report['paths']['pdf']}\n")
        self.txt_results.insert("end", "===========================================================\n")

        messagebox.showinfo("Report Generated", f"Hospital PDF Report created for Patient '{patient_details['name']}':\n{report['paths']['pdf']}")

    def _build_dataset_tab(self):
        panel = ttk.Frame(self.tab_datasets, style="Card.TFrame", padding=15)
        panel.pack(fill="both", expand=True)

        ttk.Label(panel, text="Dataset Inspector & Statistics", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))

        btn_inspect = ttk.Button(panel, text="🔍 Inspect Image, Audio, and Text Datasets", style="Primary.TButton", command=self._inspect_datasets)
        btn_inspect.pack(anchor="w", pady=5)

        self.txt_datasets = tk.Text(panel, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), relief="flat", padx=10, pady=10)
        self.txt_datasets.pack(fill="both", expand=True, pady=10)

    def _inspect_datasets(self):
        self.txt_datasets.delete("1.0", "end")
        img_report = self.dataset_service.validate_and_generate_metadata("image")
        aud_report = self.dataset_service.validate_and_generate_metadata("audio")

        self.txt_datasets.insert("end", "[Image Dataset Summary]\n")
        self.txt_datasets.insert("end", f" Total Files: {img_report['total_files']}\n")
        for emo, count in img_report['emotion_counts'].items():
            self.txt_datasets.insert("end", f"   - {emo:<10}: {count} files\n")

        self.txt_datasets.insert("end", "\n[Audio Dataset Summary]\n")
        self.txt_datasets.insert("end", f" Total Files: {aud_report['total_files']}\n")
        for emo, count in aud_report['emotion_counts'].items():
            self.txt_datasets.insert("end", f"   - {emo:<10}: {count} files\n")

    def _build_training_tab(self):
        panel = ttk.Frame(self.tab_train, style="Card.TFrame", padding=15)
        panel.pack(fill="both", expand=True)

        ttk.Label(panel, text="Train Face & Voice CNN Models", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))

        btn_train_all = ttk.Button(panel, text="⚡ Train Both AI Models & Calculate Accuracy", style="Primary.TButton", command=self._train_models_gui)
        btn_train_all.pack(anchor="w", pady=5)

        self.txt_train = tk.Text(panel, bg="#0F172A", fg="#F8FAFC", font=("Consolas", 10), relief="flat", padx=10, pady=10)
        self.txt_train.pack(fill="both", expand=True, pady=10)

    def _train_models_gui(self):
        self.txt_train.delete("1.0", "end")
        self.txt_train.insert("end", "Training models, please wait...\n")
        self.root.update()

        face_metrics = self.face_service.train_model()
        voice_metrics = self.voice_service.train_model()

        self.txt_train.insert("end", "\n[Face Emotion CNN Model]\n")
        self.txt_train.insert("end", f" Model Type          : {face_metrics['model_type']}\n")
        self.txt_train.insert("end", f" Training Accuracy   : {face_metrics['train_accuracy']}%\n")
        self.txt_train.insert("end", f" Validation Accuracy : {face_metrics['validation_accuracy']}%\n")

        self.txt_train.insert("end", "\n[Voice Emotion 1D-CNN Model]\n")
        self.txt_train.insert("end", f" Model Type          : {voice_metrics['model_type']}\n")
        self.txt_train.insert("end", f" Training Accuracy   : {voice_metrics['train_accuracy']}%\n")
        self.txt_train.insert("end", f" Validation Accuracy : {voice_metrics['validation_accuracy']}%\n")


def launch_gui():
    root = tk.Tk()
    app = MentalHealthAIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
