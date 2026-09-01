"""
Automated Model Training & Output Accuracy Verification Script.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.dataset_generator import generate_synthetic_image_dataset, generate_synthetic_audio_dataset
from app.services.dataset_service import DatasetService
from app.services.face_emotion_service import FaceEmotionService
from app.services.voice_emotion_service import VoiceEmotionService


class TestModelTrainingAndAccuracy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n========================================================")
        print(" GENERATING SYNTHETIC DATASETS FOR TRAIN & TEST PHASE   ")
        print("========================================================")
        generate_synthetic_image_dataset(samples_per_emotion=40)
        generate_synthetic_audio_dataset(samples_per_emotion=30)
        cls.dataset_service = DatasetService()
        cls.face_service = FaceEmotionService()
        cls.voice_service = VoiceEmotionService()

    def test_01_dataset_validation(self):
        """
        Validate face image and audio datasets.
        """
        image_report = self.dataset_service.validate_and_generate_metadata(dataset_type="image")
        self.assertGreater(image_report["total_files"], 0)
        self.assertEqual(image_report["corrupted_count"], 0)

        audio_report = self.dataset_service.validate_and_generate_metadata(dataset_type="audio")
        self.assertGreater(audio_report["total_files"], 0)
        self.assertEqual(audio_report["corrupted_count"], 0)

    def test_02_face_cnn_model_training_and_accuracy(self):
        """
        Train Face Emotion CNN Model and evaluate accuracy metrics.
        """
        print("\n--------------------------------------------------------")
        print(" TRAINING FACE EMOTION AI MODEL (FER2013 / CNN)         ")
        print("--------------------------------------------------------")
        metrics = self.face_service.train_model()
        
        print(f" Model Type          : {metrics['model_type']}")
        print(f" Train Samples       : {metrics['train_samples']}")
        print(f" Validation Samples  : {metrics['val_samples']}")
        print(f" Training Accuracy   : {metrics['train_accuracy']}%")
        print(f" Validation Accuracy : {metrics['validation_accuracy']}%")
        print(f" Model Saved Location: {metrics['model_saved_path']}")
        
        self.assertGreater(metrics["validation_accuracy"], 50.0)

    def test_03_voice_model_training_and_accuracy(self):
        """
        Train Voice Emotion AI Model and evaluate accuracy metrics.
        """
        print("\n--------------------------------------------------------")
        print(" TRAINING VOICE EMOTION AI MODEL (RAVDESS / CNN)        ")
        print("--------------------------------------------------------")
        metrics = self.voice_service.train_model()
        
        print(f" Model Type          : {metrics['model_type']}")
        print(f" Train Samples       : {metrics['train_samples']}")
        print(f" Validation Samples  : {metrics['val_samples']}")
        print(f" Training Accuracy   : {metrics['train_accuracy']}%")
        print(f" Validation Accuracy : {metrics['validation_accuracy']}%")
        print(f" Model Saved Location: {metrics['model_saved_path']}")

        self.assertGreater(metrics["validation_accuracy"], 50.0)


if __name__ == "__main__":
    unittest.main()
