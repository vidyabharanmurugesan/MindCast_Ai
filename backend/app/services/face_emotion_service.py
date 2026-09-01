"""
Face Emotion AI Model Training, Validation, and Prediction Service.
"""
import os
import cv2
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.exceptions import ModelInferenceException
from app.constants.emotions import EMOTIONS_FACE

logger = get_logger(__name__)


class FaceEmotionService:
    """
    Service for loading FER2013 image dataset, preprocessing facial frames,
    training Convolutional Neural Network (CNN) / Classifier, calculating accuracy,
    and making real-time emotion predictions.
    """
    def __init__(self) -> None:
        self.model_dir = settings.MODEL_DIR
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "face_emotion_model.keras")
        self.pkl_model_path = os.path.join(self.model_dir, "face_emotion_model.pkl")
        self.model = None
        self.emotions = EMOTIONS_FACE
        self.image_size = (48, 48)

    def load_dataset_from_dir(self, dataset_dir: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load grayscale 48x48 image data and labels from image_dataset folder.
        """
        X_list = []
        y_list = []

        for idx, emotion in enumerate(self.emotions):
            emotion_path = os.path.join(dataset_dir, emotion)
            if not os.path.exists(emotion_path):
                continue
            for fname in os.listdir(emotion_path):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    fpath = os.path.join(emotion_path, fname)
                    img = cv2.imread(fpath, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img_resized = cv2.resize(img, self.image_size)
                        X_list.append(img_resized)
                        y_list.append(idx)

        if not X_list:
            raise ModelInferenceException("No valid face images found in dataset directory")

        X = np.array(X_list, dtype=np.float32) / 255.0
        y = np.array(y_list, dtype=np.int64)
        return X, y

    def train_model(self, dataset_dir: str = None) -> Dict[str, Any]:
        """
        Train Face Emotion CNN / Classifier model and save face_emotion_model.keras.
        Returns training metrics and output accuracy.
        """
        dataset_dir = dataset_dir or os.path.join(settings.DATASET_DIR, "image_dataset")
        X, y = self.load_dataset_from_dir(dataset_dir)
        
        # Split into Train and Validation
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        train_accuracy = 0.0
        val_accuracy = 0.0

        try:
            import tensorflow as tf
            import logging
            tf.get_logger().setLevel(logging.ERROR)
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization


            # Build 2D CNN Architecture
            X_train_cnn = np.expand_dims(X_train, -1)
            X_val_cnn = np.expand_dims(X_val, -1)

            model = Sequential([
                Conv2D(32, (3, 3), activation="relu", input_shape=(48, 48, 1)),
                BatchNormalization(),
                MaxPooling2D((2, 2)),
                Dropout(0.25),
                Conv2D(64, (3, 3), activation="relu"),
                BatchNormalization(),
                MaxPooling2D((2, 2)),
                Dropout(0.25),
                Flatten(),
                Dense(128, activation="relu"),
                Dropout(0.5),
                Dense(len(self.emotions), activation="softmax")
            ])

            model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
            history = model.fit(X_train_cnn, y_train, validation_data=(X_val_cnn, y_val), epochs=10, batch_size=16, verbose=0)

            model.save(self.model_path)
            self.model = model

            train_accuracy = float(history.history["accuracy"][-1])
            val_accuracy = float(history.history["val_accuracy"][-1])
            model_type = "CNN (TensorFlow/Keras)"

        except Exception as e:
            logger.warning(f"TensorFlow not available or encountered issue ({e}). Falling back to Scikit-Learn MLPClassifier.")
            from sklearn.neural_network import MLPClassifier
            from sklearn.metrics import accuracy_score

            X_train_flat = X_train.reshape(X_train.shape[0], -1)
            X_val_flat = X_val.reshape(X_val.shape[0], -1)

            clf = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=200, random_state=42)
            clf.fit(X_train_flat, y_train)

            train_accuracy = float(accuracy_score(y_train, clf.predict(X_train_flat)))
            val_accuracy = float(accuracy_score(y_val, clf.predict(X_val_flat)))

            with open(self.pkl_model_path, "wb") as f:
                pickle.dump(clf, f)
            
            # Save surrogate keras marker
            with open(self.model_path, "w") as f:
                f.write(f"Face Emotion Model - MLP Accuracy: {val_accuracy:.4f}")

            self.model = clf
            model_type = "MLPClassifier (Scikit-Learn Fallback)"

        metrics = {
            "model_type": model_type,
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "train_accuracy": round(train_accuracy * 100, 2),
            "validation_accuracy": round(val_accuracy * 100, 2),
            "model_saved_path": self.model_path
        }
        logger.info(f"Face Emotion AI Model Trained: Accuracy = {metrics['validation_accuracy']}%")
        return metrics

    def predict_emotion(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predict emotion from image byte input.
        """
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ModelInferenceException("Failed to decode image file")

        img_resized = cv2.resize(img, self.image_size) / 255.0

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
            X_flat = img_resized.reshape(1, -1)
            probs = self.model.predict_proba(X_flat)[0]
        else:
            X_cnn = np.expand_dims(np.expand_dims(img_resized, 0), -1)
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
