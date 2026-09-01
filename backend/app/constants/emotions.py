"""
Emotion & Mental Health Scoring Constants.
"""
from typing import List, Dict

EMOTIONS_FACE: List[str] = [
    "Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"
]

EMOTIONS_VOICE: List[str] = [
    "Angry", "Disgust", "Fear", "Happy", "Neutral", "Sad", "Surprise"
]

EMOTION_WEIGHTS: Dict[str, float] = {
    "Angry": 0.85,
    "Disgust": 0.70,
    "Fear": 0.90,
    "Sad": 0.80,
    "Neutral": 0.20,
    "Happy": 0.05,
    "Surprise": 0.35,
}

RISK_LEVELS: Dict[str, str] = {
    "LOW": "Low Risk - Maintain normal mental wellness routines.",
    "MODERATE": "Moderate Stress Detected - Mindfulness and relaxation recommended.",
    "HIGH": "High Risk - Follow up with clinical specialist recommended.",
    "CRITICAL": "Critical Risk - Immediate professional intervention requested."
}
