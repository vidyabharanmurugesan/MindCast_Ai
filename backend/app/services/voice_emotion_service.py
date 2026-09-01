"""
Voice Emotion AI Model Training, Feature Extraction, and Audio Analysis Service.
"""
import os
import wave
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.exceptions import ModelInferenceException
from app.constants.emotions import EMOTIONS_VOICE

logger = get_logger(__name__)


class VoiceEmotionService:
    """
    Service for audio feature extraction (MFCCs, Mel Spectrogram, Chroma, RMS, Spectral Contrast, ZCR),
    Voice CNN model training, accuracy evaluation, and emotion prediction.
    """
    def __init__(self) -> None:
        self.model_dir = settings.MODEL_DIR
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "voice_emotion_model.keras")
        self.pkl_model_path = os.path.join(self.model_dir, "voice_emotion_model.pkl")
        self.model = None
        self.emotions = EMOTIONS_VOICE

    def extract_audio_features(self, filepath: str) -> np.ndarray:
        """
        Extract acoustic features from WAV audio file.
        Features: MFCCs (40), Chroma, Mel Spectrogram, Spectral Contrast, RMS, Zero Crossing Rate.
        """
        try:
            import librosa
            audio, sample_rate = librosa.load(filepath, res_type="kaiser_fast")
            
            # MFCCs (40)
            mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40).T, axis=0)
            # Chroma
            chroma = np.mean(librosa.feature.chroma_stft(y=audio, sr=sample_rate).T, axis=0)
            # Mel Spectrogram
            mel = np.mean(librosa.feature.melspectrogram(y=audio, sr=sample_rate).T, axis=0)
            # Spectral Contrast
            contrast = np.mean(librosa.feature.spectral_contrast(y=audio, sr=sample_rate).T, axis=0)
            # RMS
            rms = np.mean(librosa.feature.rms(y=audio).T, axis=0)
            # Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(y=audio).T, axis=0)

            features = np.hstack([mfccs, chroma, mel, contrast, rms, zcr])
            return features

        except Exception as e:
            logger.debug(f"Librosa feature extraction fallback to wave file analysis ({e})")
            # Native wave feature extraction fallback
            with wave.open(filepath, "rb") as wf:
                n_frames = wf.getnframes()
                frames = wf.readframes(n_frames)
                signal = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                
            if len(signal) == 0:
                return np.zeros(60, dtype=np.float32)
                
            # Basic acoustic statistical feature vector (length 60)
            mean_val = np.mean(signal)
            std_val = np.std(signal)
            rms_val = np.sqrt(np.mean(signal**2))
            zcr_val = np.sum(np.diff(np.sign(signal)) != 0) / float(len(signal))
            fft_vals = np.abs(np.fft.rfft(signal[:1024]))
            
            features = np.zeros(60, dtype=np.float32)
            features[0] = mean_val
            features[1] = std_val
            features[2] = rms_val
            features[3] = zcr_val
            features[4:4+len(fft_vals[:56])] = fft_vals[:56] / (np.max(fft_vals) + 1e-6)
            return features

    def load_dataset_from_dir(self, dataset_dir: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load audio features and labels from audio_dataset folder.
        """
        X_list = []
        y_list = []

        for idx, emotion in enumerate(self.emotions):
            emotion_path = os.path.join(dataset_dir, emotion)
            if not os.path.exists(emotion_path):
                continue
            for fname in os.listdir(emotion_path):
                if fname.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
                    fpath = os.path.join(emotion_path, fname)
                    feat = self.extract_audio_features(fpath)
                    if feat is not None:
                        X_list.append(feat)
                        y_list.append(idx)

        if not X_list:
            raise ModelInferenceException("No valid audio files found in dataset directory")

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int64)
        return X, y

    def train_model(self, dataset_dir: str = None) -> Dict[str, Any]:
        """
        Train Voice Emotion 1D-CNN / Classifier model and save voice_emotion_model.keras.
        Returns training metrics and output accuracy.
        """
        dataset_dir = dataset_dir or os.path.join(settings.DATASET_DIR, "audio_dataset")
        X, y = self.load_dataset_from_dir(dataset_dir)

        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        train_accuracy = 0.0
        val_accuracy = 0.0

        try:
            import tensorflow as tf
            import logging
            tf.get_logger().setLevel(logging.ERROR)
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Conv1D, MaxPooling1D, Flatten


            X_train_cnn = np.expand_dims(X_train, -1)
            X_val_cnn = np.expand_dims(X_val, -1)

            model = Sequential([
                Conv1D(64, kernel_size=3, activation="relu", input_shape=(X_train.shape[1], 1)),
                BatchNormalization(),
                MaxPooling1D(pool_size=2),
                Dropout(0.3),
                Conv1D(128, kernel_size=3, activation="relu"),
                BatchNormalization(),
                MaxPooling1D(pool_size=2),
                Dropout(0.3),
                Flatten(),
                Dense(128, activation="relu"),
                Dropout(0.4),
                Dense(len(self.emotions), activation="softmax")
            ])

            model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
            history = model.fit(X_train_cnn, y_train, validation_data=(X_val_cnn, y_val), epochs=15, batch_size=16, verbose=0)

            model.save(self.model_path)
            self.model = model

            train_accuracy = float(history.history["accuracy"][-1])
            val_accuracy = float(history.history["val_accuracy"][-1])
            model_type = "1D-CNN (TensorFlow/Keras)"

        except Exception as e:
            logger.warning(f"TensorFlow not available for Audio CNN ({e}). Using Scikit-Learn RandomForestClassifier.")
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import accuracy_score

            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)

            train_accuracy = float(accuracy_score(y_train, clf.predict(X_train)))
            val_accuracy = float(accuracy_score(y_val, clf.predict(X_val)))

            with open(self.pkl_model_path, "wb") as f:
                pickle.dump(clf, f)

            with open(self.model_path, "w") as f:
                f.write(f"Voice Emotion Model - RandomForest Accuracy: {val_accuracy:.4f}")

            self.model = clf
            model_type = "RandomForestClassifier (Scikit-Learn Fallback)"

        metrics = {
            "model_type": model_type,
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "train_accuracy": round(train_accuracy * 100, 2),
            "validation_accuracy": round(val_accuracy * 100, 2),
            "model_saved_path": self.model_path
        }
        logger.info(f"Voice Emotion AI Model Trained: Accuracy = {metrics['validation_accuracy']}%")
        return metrics

    def predict_emotion_from_file(self, audio_filepath: str) -> Dict[str, Any]:
        """
        Predict voice emotion from audio file path.
        """
        features = self.extract_audio_features(audio_filepath)
        if features is None:
            raise ModelInferenceException("Failed to extract audio features from file")

        if self.model is None:
            if os.path.exists(self.pkl_model_path):
                with open(self.pkl_model_path, "rb") as f:
                    self.model = pickle.load(f)
            elif os.path.exists(self.model_path):
                try:
                    import tensorflow as tf
                    self.model = tf.keras.models.load_model(self.model_path)
                except Exception:
                    self.train_model()
            else:
                self.train_model()



        if hasattr(self.model, "predict_proba"):
            X_flat = features.reshape(1, -1)
            probs = self.model.predict_proba(X_flat)[0]
        else:
            X_cnn = np.expand_dims(np.expand_dims(features, 0), -1)
            probs = self.model.predict(X_cnn, verbose=0)[0]

        top_idx = int(np.argmax(probs))
        predicted_emotion = self.emotions[top_idx]
        confidence = float(probs[top_idx])

        probabilities_map = {self.emotions[i]: round(float(probs[i]), 4) for i in range(len(self.emotions))}

        return {
            "emotion": predicted_emotion,
            "confidence": round(confidence * 100, 2),
            "probabilities": probabilities_map
        }
