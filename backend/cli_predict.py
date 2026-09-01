"""
Interactive Terminal CLI Utility for Testing Face & Voice AI Emotion Models.
"""
import sys
import os
import warnings
import argparse

# Suppress TensorFlow C++ & Keras deprecation warnings in CLI
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService


def test_face_model(image_path: str):
    """
    Test Face Emotion AI model on an image file from terminal.
    """
    print(f"\n[Testing Face Emotion Model on Image: {image_path}]")
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist.")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    service = FaceEmotionService()
    result = service.predict_emotion(image_bytes)

    print("\n---------------- PREDICTION RESULTS ----------------")
    print(f" Predicted Emotion : {result['emotion']}")
    print(f" Confidence Score  : {result['confidence']}%")
    print(" Emotion Probabilities:")
    for emo, prob in result['probabilities'].items():
        bar = "#" * int(prob * 20)

        print(f"   {emo:<10}: {prob*100:>5.1f}% | {bar}")
    print("----------------------------------------------------\n")


def test_voice_model(audio_path: str):
    """
    Test Voice Emotion AI model on an audio WAV file from terminal.
    """
    print(f"\n[Testing Voice Emotion Model on Audio: {audio_path}]")
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' does not exist.")
        return

    service = VoiceEmotionService()
    result = service.predict_emotion_from_file(audio_path)

    print("\n---------------- PREDICTION RESULTS ----------------")
    print(f" Predicted Emotion : {result['emotion']}")
    print(f" Confidence Score  : {result['confidence']}%")
    print(" Emotion Probabilities:")
    for emo, prob in result['probabilities'].items():
        bar = "#" * int(prob * 20)

        print(f"   {emo:<10}: {prob*100:>5.1f}% | {bar}")
    print("----------------------------------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Face & Voice Emotion AI Models from Terminal")
    parser.add_argument("--type", choices=["face", "voice"], default="face", help="Model type: 'face' or 'voice'")
    parser.add_argument("--file", type=str, help="Path to sample image (PNG/JPG) or audio (WAV) file")

    args = parser.parse_args()

    # Default fallback sample files if --file is omitted
    if not args.file:
        if args.type == "face":
            args.file = "backend/sample_datasets/image_dataset/Happy/Happy_000.png"
        else:
            args.file = "backend/sample_datasets/audio_dataset/Happy/Happy_000.wav"

    if args.type == "face":
        test_face_model(args.file)
    else:
        test_voice_model(args.file)
