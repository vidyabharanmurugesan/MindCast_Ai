"""
Face and Voice Emotion AI Model REST API Routes.
"""
from flask import Blueprint, request
from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService
from app.utils.response import api_response
from app.core.exceptions import ValidationException

model_bp = Blueprint("models", __name__)
face_service = FaceEmotionService()
voice_service = VoiceEmotionService()


@model_bp.route("/models/face/train", methods=["POST"])
def train_face_model():
    """
    Train Face Emotion AI model and output accuracy metrics.
    """
    metrics = face_service.train_model()
    return api_response(success=True, data=metrics, message="Face Emotion AI model trained successfully")


@model_bp.route("/models/face/predict", methods=["POST"])
def predict_face_emotion():
    """
    Predict emotion from uploaded image file.
    """
    if "image" not in request.files:
        raise ValidationException("Missing 'image' file in multipart/form-data request")
    
    file = request.files["image"]
    image_bytes = file.read()
    prediction = face_service.predict_emotion(image_bytes)
    return api_response(success=True, data=prediction, message="Face emotion prediction completed")


@model_bp.route("/models/voice/train", methods=["POST"])
def train_voice_model():
    """
    Train Voice Emotion AI model and output accuracy metrics.
    """
    metrics = voice_service.train_model()
    return api_response(success=True, data=metrics, message="Voice Emotion AI model trained successfully")


@model_bp.route("/models/voice/predict", methods=["POST"])
def predict_voice_emotion():
    """
    Predict emotion from uploaded audio file.
    """
    if "audio" not in request.files:
        raise ValidationException("Missing 'audio' file in multipart/form-data request")

    file = request.files["audio"]
    
    import os
    import tempfile
    
    # Save temp audio file for librosa / wav analysis
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    file.save(temp_path)

    try:
        prediction = voice_service.predict_emotion_from_file(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return api_response(success=True, data=prediction, message="Voice emotion prediction completed")
