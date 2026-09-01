"""
Multi-Modal Fusion Engine for Clinical Emotion & Mental Health Assessment.
"""
from typing import Dict, Any, List
from app.constants.emotions import EMOTION_WEIGHTS, RISK_LEVELS
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class FusionEngineService:
    """
    Combines visual face emotion predictions and acoustic voice emotion predictions
    using confidence-weighted fusion matrix to calculate clinical stress scores,
    mental health index, risk classification, doctor observations, and recommendations.
    """

    def fuse_predictions(
        self,
        face_result: Dict[str, Any],
        voice_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform clinical multi-modal fusion.
        """
        face_emotion = face_result.get("emotion", "Neutral")
        face_conf = face_result.get("confidence", 50.0) / 100.0

        voice_emotion = voice_result.get("emotion", "Neutral")
        voice_conf = voice_result.get("confidence", 50.0) / 100.0

        # Face weight: 0.55, Voice weight: 0.45
        w_face = 0.55 * face_conf
        w_voice = 0.45 * voice_conf
        total_w = w_face + w_voice + 1e-6

        norm_w_face = w_face / total_w
        norm_w_voice = w_voice / total_w

        # Overall emotion selection
        if norm_w_face >= norm_w_voice:
            overall_emotion = face_emotion
        else:
            overall_emotion = voice_emotion

        # Stress Score Calculation (0 - 100)
        face_stress_weight = EMOTION_WEIGHTS.get(face_emotion, 0.2)
        voice_stress_weight = EMOTION_WEIGHTS.get(voice_emotion, 0.2)

        stress_score = round(
            (norm_w_face * face_stress_weight + norm_w_voice * voice_stress_weight) * 100.0,
            2
        )

        # Mental Health Score (100 - Stress Score)
        mental_health_score = round(max(0.0, 100.0 - stress_score), 2)

        # Risk Level Classification
        if stress_score < 30.0:
            risk_level = "LOW"
        elif stress_score < 60.0:
            risk_level = "MODERATE"
        elif stress_score < 80.0:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        risk_description = RISK_LEVELS[risk_level]
        overall_confidence = round(((face_conf + voice_conf) / 2.0) * 100.0, 2)

        # Doctor Observations
        doctor_observation = (
            f"Patient exhibited predominantly '{face_emotion}' facial expression ({round(face_conf*100, 1)}% confidence) "
            f"and '{voice_emotion}' vocal tone ({round(voice_conf*100, 1)}% confidence). "
            f"Fused clinical stress index measured at {stress_score}/100 ({risk_level} risk)."
        )

        # Recommendations
        recommendations = {
            "walking_goals": "Target 7,500 daily steps for optimal endorphin release.",
            "meditation": "15 minutes of guided deep breathing exercises twice daily.",
            "sleep": "Maintain 7.5 to 8 hours of consistent nightly sleep.",
            "hydration": "Drink 2.5 to 3.0 Liters of water daily.",
            "clinical_note": risk_description
        }

        return {
            "overall_emotion": overall_emotion,
            "face_emotion": face_emotion,
            "face_confidence": round(face_conf * 100, 2),
            "voice_emotion": voice_emotion,
            "voice_confidence": round(voice_conf * 100, 2),
            "stress_score": stress_score,
            "mental_health_score": mental_health_score,
            "confidence": overall_confidence,
            "risk_level": risk_level,
            "doctor_observation": doctor_observation,
            "recommendations": recommendations
        }
