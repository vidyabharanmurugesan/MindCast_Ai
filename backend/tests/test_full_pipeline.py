"""
Full System Integration Test Suite for End-to-End Clinical Pipeline.
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService
from app.services.fusion_service import FusionEngineService
from app.services.assessment_service import AssessmentService
from app.services.report_generator_service import ReportGeneratorService


class TestFullPipeline(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_01_face_and_voice_prediction(self):
        """
        Verify face and voice emotion services return formatted predictions with class probabilities.
        """
        face_service = FaceEmotionService()
        voice_service = VoiceEmotionService()

        # Dummy 48x48 image
        import cv2
        import numpy as np
        img = np.zeros((48, 48), dtype=np.uint8)
        _, img_bytes = cv2.imencode(".png", img)

        face_pred = face_service.predict_emotion(img_bytes.tobytes())
        self.assertIn("emotion", face_pred)
        self.assertIn("confidence", face_pred)
        self.assertIn("probabilities", face_pred)

    def test_02_fusion_engine(self):
        """
        Verify multi-modal fusion engine score and risk level outputs.
        """
        fusion_service = FusionEngineService()
        face_result = {"emotion": "Sad", "confidence": 88.5}
        voice_result = {"emotion": "Fear", "confidence": 92.0}

        fused = fusion_service.fuse_predictions(face_result, voice_result)
        self.assertIn("overall_emotion", fused)
        self.assertIn("stress_score", fused)
        self.assertIn("mental_health_score", fused)
        self.assertIn("risk_level", fused)
        self.assertGreater(fused["stress_score"], 50.0)

    def test_03_full_clinical_assessment_and_report(self):
        """
        Test start session -> finish session -> hospital PDF/JSON/CSV report generation.
        """
        assess_service = AssessmentService()
        report_service = ReportGeneratorService()

        session = assess_service.start_session("PATIENT-TEST-99")
        session_id = session["session_id"]
        
        finished_session = assess_service.finish_session(session_id)
        report = report_service.generate_report(finished_session)

        self.assertIn("report_id", report)
        self.assertTrue(os.path.exists(report["paths"]["json"]))
        self.assertTrue(os.path.exists(report["paths"]["csv"]))
        self.assertTrue(os.path.exists(report["paths"]["pdf"]))
        self.assertTrue(os.path.exists(report["paths"]["qr"]))


if __name__ == "__main__":
    unittest.main()
