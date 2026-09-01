"""
Session and Assessment Status Constants.
"""
class AssessmentStatus:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class UserRole:
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"
