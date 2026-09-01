"""
Dataset Management Service for Validation, Duplicate Detection, and Metadata Generation.
"""
import os
import glob
import json
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.core.config import settings
from app.core.logging_config import get_logger
from app.constants.emotions import EMOTIONS_FACE, EMOTIONS_VOICE

logger = get_logger(__name__)


class DatasetService:
    """
    Service for dataset indexing, validation, statistics calculation, and metadata generation.
    """
    def __init__(self, dataset_dir: str = None) -> None:
        self.dataset_dir = dataset_dir or settings.DATASET_DIR
        self.image_dir = os.path.join(self.dataset_dir, "image_dataset")
        self.audio_dir = os.path.join(self.dataset_dir, "audio_dataset")
        self.text_dir = os.path.join(self.dataset_dir, "text_dataset")
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """
        Create dataset folders if missing and populate initial datasets.
        """
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        
        for emotion in EMOTIONS_FACE:
            os.makedirs(os.path.join(self.image_dir, emotion), exist_ok=True)

        for emotion in EMOTIONS_VOICE:
            os.makedirs(os.path.join(self.audio_dir, emotion), exist_ok=True)

    @staticmethod
    def calculate_file_hash(filepath: str) -> str:
        """
        Calculate SHA-256 hash of file for duplicate detection.
        """
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def validate_and_generate_metadata(self, dataset_type: str = "image") -> Dict[str, Any]:
        """
        Validate dataset files, generate metadata.csv, dataset_report.json, and compute statistics.
        """
        if dataset_type == "image":
            target_dir = self.image_dir
            emotions = EMOTIONS_FACE
            allowed_exts = {".jpg", ".jpeg", ".png", ".bmp"}
        elif dataset_type == "audio":
            target_dir = self.audio_dir
            emotions = EMOTIONS_VOICE
            allowed_exts = {".wav", ".mp3", ".flac", ".ogg"}
        else:
            target_dir = self.text_dir
            emotions = EMOTIONS_FACE
            allowed_exts = {".csv", ".json", ".txt"}



        metadata_records = []
        hashes = {}
        duplicates = []
        corrupted_files = []
        emotion_counts = {e: 0 for e in emotions}

        for emotion in emotions:
            folder_path = os.path.join(target_dir, emotion)
            if not os.path.exists(folder_path):
                continue

            for root, _, files in os.walk(folder_path):
                for fname in files:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in allowed_exts:
                        continue

                    fpath = os.path.join(root, fname)
                    file_size = os.path.getsize(fpath)

                    if file_size == 0:
                        corrupted_files.append(fpath)
                        continue

                    file_hash = self.calculate_file_hash(fpath)
                    if file_hash in hashes:
                        duplicates.append({"original": hashes[file_hash], "duplicate": fpath})
                    else:
                        hashes[file_hash] = fpath

                    emotion_counts[emotion] += 1
                    metadata_records.append({
                        "filename": fname,
                        "file_path": fpath,
                        "emotion": emotion,
                        "file_size_bytes": file_size,
                        "file_hash": file_hash
                    })

        # Save metadata.csv
        df = pd.DataFrame(metadata_records)
        metadata_csv_path = os.path.join(target_dir, "metadata.csv")
        df.to_csv(metadata_csv_path, index=False)

        # Generate report json
        report = {
            "dataset_type": dataset_type,
            "total_files": len(metadata_records),
            "emotion_counts": emotion_counts,
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
            "corrupted_count": len(corrupted_files),
            "corrupted_files": corrupted_files,
            "metadata_csv_path": metadata_csv_path
        }

        report_json_path = os.path.join(target_dir, "dataset_report.json")
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        logger.info(f"Dataset report generated for {dataset_type}: {len(metadata_records)} total files.")
        return report
