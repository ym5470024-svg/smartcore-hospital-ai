from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HospitalRecordCreate(BaseModel):
    hospital_id: str | None = None
    hospital_name: str | None = None
    governorate: str | None = None
    city: str | None = None
    district: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    hospital_type: str | None = None
    reporting_timestamp: str | None = None
    reporting_period: str | None = None
    total_beds: float | None = None
    occupied_beds: float | None = None
    available_beds: float | None = None
    emergency_capacity: float | None = None
    emergency_current_load: float | None = None
    emergency_status: str | None = None
    accident_service_available: str | None = None
    burn_unit_available: str | None = None
    intensive_care_available: str | None = None
    operating_room_available: str | None = None
    laboratory_available: str | None = None
    radiology_available: str | None = None
    ambulance_service_available: str | None = None
    waiting_patients: float | None = None
    average_waiting_time_minutes: float | None = None
    staff_available: float | None = None
    source_name: str | None = None
    source_url: str | None = None
    source_updated_at: str | None = None
    data_quality_status: str | None = None


class HospitalRecordRead(HospitalRecordCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ValidationIssue(BaseModel):
    row_index: int
    field: str
    level: str
    message: str


class ImportPreviewResponse(BaseModel):
    columns: list[str]
    preview_rows: list[dict[str, Any]]
    warnings: list[str]
    file_name: str


class ImportConfirmResponse(BaseModel):
    accepted: int
    rejected: int
    duplicates: int
    mode: str
    log_id: int | None = None
