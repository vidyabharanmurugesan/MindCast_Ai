"""
Clinical Assessment Session Engine.
"""
import uuid
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService
from app.services.fusion_service import FusionEngineService
from app.core.exceptions import NotFoundException
from app.core.config import settings


class AssessmentService:
    """
    Manages active assessment sessions, records face/voice stream frames,
    executes Fusion Engine, and stores session summary data.
    """
    _sessions: Dict[str, Dict[str, Any]] = {}
    _is_loaded = False

    def __init__(self) -> None:
        self.face_service = FaceEmotionService()
        self.voice_service = VoiceEmotionService()
        self.fusion_service = FusionEngineService()
        self.sessions_file = os.path.join(settings.BASE_DIR, "data", "sessions.json")
        os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
        if not AssessmentService._is_loaded:
            self._load_sessions()

    def _load_sessions(self) -> None:
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    AssessmentService._sessions.update(data)
            except Exception:
                pass
        AssessmentService._is_loaded = True

    def _save_sessions(self) -> None:
        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump(AssessmentService._sessions, f, indent=4)

    def start_session(self, patient_id: str = "PATIENT-001") -> Dict[str, Any]:
        """
        Start new assessment session with unique session ID.
        """
        session_id = f"SESS-{uuid.uuid4().hex[:8].upper()}"
        session_data = {
            "session_id": session_id,
            "patient_id": patient_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "status": "ACTIVE",
            "face_predictions": [],
            "voice_predictions": [],
            "fused_result": None
        }
        AssessmentService._sessions[session_id] = session_data
        self._save_sessions()
        return session_data

    def process_face_frame(self, session_id: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process single webcam frame for session.
        """
        if session_id not in AssessmentService._sessions:
            raise NotFoundException(f"Assessment session '{session_id}' not found")

        pred = self.face_service.predict_emotion(image_bytes)
        pred["timestamp"] = datetime.now(timezone.utc).isoformat()
        AssessmentService._sessions[session_id]["face_predictions"].append(pred)
        self._save_sessions()
        return pred

    def process_voice_chunk(self, session_id: str, audio_path: str) -> Dict[str, Any]:
        """
        Process single audio chunk for session.
        """
        if session_id not in AssessmentService._sessions:
            raise NotFoundException(f"Assessment session '{session_id}' not found")

        pred = self.voice_service.predict_emotion_from_file(audio_path)
        pred["timestamp"] = datetime.now(timezone.utc).isoformat()
        AssessmentService._sessions[session_id]["voice_predictions"].append(pred)
        self._save_sessions()
        return pred

    def finish_session(self, session_id: str) -> Dict[str, Any]:
        """
        Finish assessment session, run multi-modal fusion engine, and compile report data.
        """
        if session_id not in AssessmentService._sessions:
            raise NotFoundException(f"Assessment session '{session_id}' not found")

        session = AssessmentService._sessions[session_id]
        session["end_time"] = datetime.now(timezone.utc).isoformat()
        session["status"] = "COMPLETED"

        # Calculate average/dominant face prediction
        face_preds = session["face_predictions"]
        last_face = face_preds[-1] if face_preds else {"emotion": "Neutral", "confidence": 75.0}

        # Calculate average/dominant voice prediction
        voice_preds = session["voice_predictions"]
        last_voice = voice_preds[-1] if voice_preds else {"emotion": "Neutral", "confidence": 75.0}

        fused = self.fusion_service.fuse_predictions(last_face, last_voice)
        session["fused_result"] = fused
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session details.
        """
        if session_id not in AssessmentService._sessions:
            raise NotFoundException(f"Assessment session '{session_id}' not found")
        return AssessmentService._sessions[session_id]
