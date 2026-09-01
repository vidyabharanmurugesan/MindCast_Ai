"""
Dataset Directory Verification CLI Script for Image, Audio, and Text Datasets.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.dataset_service import DatasetService


def check_all_datasets():
    dataset_base = os.path.abspath("backend/sample_datasets")
    print("==========================================================================")
    print(f" CONNECTING & VERIFYING DATASET PATH: {dataset_base}")
    print("==========================================================================")

    if not os.path.exists(dataset_base):
        print(f"Error: Dataset directory '{dataset_base}' does not exist.")
        return

    service = DatasetService()

    # 1. Check Image Dataset
    img_report = service.validate_and_generate_metadata("image")
    print("\n[1. IMAGE DATASET (FER2013 Facial Emotion Images)]")
    print(f" Path                : {service.image_dir}")
    print(f" Total Image Files   : {img_report['total_files']}")
    print(f" Duplicate Files     : {img_report['duplicate_count']}")
    print(f" Corrupted Files     : {img_report['corrupted_count']}")
    print(" Class Distribution:")
    for emo, count in img_report['emotion_counts'].items():
        print(f"   - {emo:<10}: {count} files")

    # 2. Check Audio Dataset
    aud_report = service.validate_and_generate_metadata("audio")
    print("\n[2. AUDIO DATASET (RAVDESS/CREMA-D Voice WAV Audio)]")
    print(f" Path                : {service.audio_dir}")
    print(f" Total Audio Files   : {aud_report['total_files']}")
    print(f" Duplicate Files     : {aud_report['duplicate_count']}")
    print(f" Corrupted Files     : {aud_report['corrupted_count']}")
    print(" Class Distribution:")
    for emo, count in aud_report['emotion_counts'].items():
        print(f"   - {emo:<10}: {count} files")

    # 3. Check Text Dataset
    text_dir = os.path.join(dataset_base, "text_dataset")
    print("\n[3. TEXT DATASET (Clinical Emotion Text Transcripts)]")
    print(f" Path                : {text_dir}")
    if os.path.exists(text_dir):
        text_files = [f for f in os.listdir(text_dir) if f.endswith(('.csv', '.json', '.txt'))]
        print(f" Total Text Files    : {len(text_files)}")
        for tf in text_files:
            size_kb = round(os.path.getsize(os.path.join(text_dir, tf)) / 1024, 2)
            print(f"   - {tf:<25} ({size_kb} KB)")
    else:
        print(" Text dataset directory not found.")

    print("\n==========================================================================")
    print(" DATASET VERIFICATION & HEALTH CHECK COMPLETE")
    print("==========================================================================")


if __name__ == "__main__":
    check_all_datasets()
