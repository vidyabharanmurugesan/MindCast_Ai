"""
Model Training and Accuracy Evaluation Entrypoint Script.
"""
import sys
import os
import warnings

# Suppress TensorFlow C++ & Keras deprecation warnings during training
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
warnings.filterwarnings("ignore")

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.utils.dataset_generator import generate_synthetic_image_dataset, generate_synthetic_audio_dataset
from app.services.dataset_service import DatasetService
from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService



def run_training():
    print("\n========================================================")
    print(" 1. GENERATING SYNTHETIC DATASETS FOR TRAIN & TEST     ")
    print("========================================================")
    generate_synthetic_image_dataset(samples_per_emotion=250)
    generate_synthetic_audio_dataset(samples_per_emotion=250)


    dataset_service = DatasetService()
    print("\n[Dataset Validation]")
    img_report = dataset_service.validate_and_generate_metadata("image")
    aud_report = dataset_service.validate_and_generate_metadata("audio")
    print(f" Image Dataset Files: {img_report['total_files']} across {len(img_report['emotion_counts'])} emotions")
    print(f" Audio Dataset Files: {aud_report['total_files']} across {len(aud_report['emotion_counts'])} emotions")

    print("\n========================================================")
    print(" 2. TRAINING FACE EMOTION AI MODEL (FER2013 / CNN)      ")
    print("========================================================")
    face_service = FaceEmotionService()
    face_metrics = face_service.train_model()

    print(f" Model Type          : {face_metrics['model_type']}")
    print(f" Train Samples       : {face_metrics['train_samples']}")
    print(f" Validation Samples  : {face_metrics['val_samples']}")
    print(f" Training Accuracy   : {face_metrics['train_accuracy']}%")
    print(f" Validation Accuracy : {face_metrics['validation_accuracy']}%")
    print(f" Saved Model Path    : {face_metrics['model_saved_path']}")

    print("\n========================================================")
    print(" 3. TRAINING VOICE EMOTION AI MODEL (RAVDESS / CNN)     ")
    print("========================================================")
    voice_service = VoiceEmotionService()
    voice_metrics = voice_service.train_model()

    print(f" Model Type          : {voice_metrics['model_type']}")
    print(f" Train Samples       : {voice_metrics['train_samples']}")
    print(f" Validation Samples  : {voice_metrics['val_samples']}")
    print(f" Training Accuracy   : {voice_metrics['train_accuracy']}%")
    print(f" Validation Accuracy : {voice_metrics['validation_accuracy']}%")
    print(f" Saved Model Path    : {voice_metrics['model_saved_path']}")

    print("\n========================================================")
    print(" TRAINING SUMMARY & ACCURACY REPORT COMPLETE             ")
    print("========================================================")


if __name__ == "__main__":
    run_training()
