"""
Dataset Management REST API Routes.
"""
from flask import Blueprint, request
from app.services.dataset_service import DatasetService
from app.utils.response import api_response

dataset_bp = Blueprint("datasets", __name__)
dataset_service = DatasetService()


@dataset_bp.route("/datasets/validate", methods=["POST"])
def validate_dataset():
    """
    Validate dataset and generate metadata.csv and dataset_report.json.
    Query param or JSON payload: dataset_type = 'image' | 'audio'
    """
    data = request.get_json(silent=True) or {}
    dataset_type = data.get("dataset_type", request.args.get("dataset_type", "image"))
    
    report = dataset_service.validate_and_generate_metadata(dataset_type=dataset_type)
    return api_response(success=True, data=report, message=f"Dataset {dataset_type} validated successfully")
