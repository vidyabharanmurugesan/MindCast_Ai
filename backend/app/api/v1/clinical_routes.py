"""
Clinical Assessment, Reports, Analysis, and Dashboard REST API Routes.
"""
from flask import Blueprint, request, send_file
from app.services.assessment_service import AssessmentService
from app.services.report_generator_service import ReportGeneratorService
from app.services.analysis_service import ReportAnalysisService
from app.services.dashboard_service import DashboardService
from app.utils.response import api_response
from app.core.exceptions import ValidationException

clinical_bp = Blueprint("clinical", __name__)
assessment_service = AssessmentService()
report_service = ReportGeneratorService()
analysis_service = ReportAnalysisService()
dashboard_service = DashboardService()


@clinical_bp.route("/assessment/start", methods=["POST"])
def start_assessment():
    """
    Start new clinical assessment session.
    """
    data = request.get_json(silent=True) or {}
    patient_id = data.get("patient_id", "PATIENT-001")
    session = assessment_service.start_session(patient_id=patient_id)
    return api_response(success=True, data=session, message="Assessment session initialized")


@clinical_bp.route("/assessment/<session_id>/finish", methods=["POST"])
def finish_assessment(session_id: str):
    """
    Finish session and run Fusion Engine.
    """
    data = request.get_json(silent=True) or {}
    patient_details = data.get("patient_details")
    
    session = assessment_service.finish_session(session_id)
    report = report_service.generate_report(session, patient_details=patient_details)
    return api_response(success=True, data={"session": session, "report": report}, message="Assessment completed and report generated")


@clinical_bp.route("/assessment/<session_id>/face", methods=["POST"])
def process_face(session_id: str):
    """
    Process face image for a specific session.
    """
    if "image" not in request.files:
        raise ValidationException("Missing 'image' file in multipart/form-data request")
    file = request.files["image"]
    image_bytes = file.read()
    pred = assessment_service.process_face_frame(session_id, image_bytes)
    return api_response(success=True, data=pred, message="Face processed for session")


@clinical_bp.route("/assessment/<session_id>/voice", methods=["POST"])
def process_voice(session_id: str):
    """
    Process voice audio for a specific session.
    """
    if "audio" not in request.files:
        raise ValidationException("Missing 'audio' file in multipart/form-data request")
    file = request.files["audio"]
    
    import os
    import tempfile
    
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    file.save(temp_path)
    
    try:
        pred = assessment_service.process_voice_chunk(session_id, temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return api_response(success=True, data=pred, message="Voice processed for session")


@clinical_bp.route("/reports/<report_id>/download", methods=["GET"])
def download_report(report_id: str):
    """
    Download report PDF, JSON, or CSV. Query param: format = pdf | json | csv
    """
    from app.core.config import settings
    import os
    fmt = request.args.get("format", "pdf").lower()
    file_path = os.path.join(settings.BASE_DIR, "reports", f"{report_id}.{fmt}")
    return send_file(file_path, as_attachment=True)


@clinical_bp.route("/reports", methods=["GET"])
def list_reports():
    """
    List all generated reports.
    """
    import os
    from app.core.config import settings
    reports_dir = os.path.join(settings.BASE_DIR, "reports")
    reports = []
    if os.path.exists(reports_dir):
        for filename in os.listdir(reports_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(reports_dir, filename), "r") as f:
                        import json
                        data = json.load(f)
                        reports.append({
                            "report_id": data.get("report_id"),
                            "patient_name": data.get("patient_details", {}).get("name", "Unknown"),
                            "generated_at": data.get("generated_at"),
                            "overall_emotion": data.get("fused_clinical_result", {}).get("overall_emotion", "Unknown")
                        })
                except Exception:
                    pass
    # Sort by most recent
    reports.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
    return api_response(success=True, data=reports, message="Reports retrieved successfully")


@clinical_bp.route("/dashboard/summary", methods=["GET"])
def get_dashboard():
    """
    Fetch aggregated clinical dashboard data.
    """
    data = dashboard_service.get_dashboard_summary()
    return api_response(success=True, data=data, message="Dashboard summary retrieved")
