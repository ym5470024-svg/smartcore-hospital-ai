from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HospitalRecord(Base):
    __tablename__ = "hospital_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hospital_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    hospital_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    governorate: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    hospital_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reporting_timestamp: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reporting_period: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_beds: Mapped[float | None] = mapped_column(Float, nullable=True)
    occupied_beds: Mapped[float | None] = mapped_column(Float, nullable=True)
    available_beds: Mapped[float | None] = mapped_column(Float, nullable=True)
    emergency_capacity: Mapped[float | None] = mapped_column(Float, nullable=True)
    emergency_current_load: Mapped[float | None] = mapped_column(Float, nullable=True)
    emergency_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    accident_service_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    burn_unit_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    intensive_care_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    operating_room_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    laboratory_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    radiology_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ambulance_service_available: Mapped[str | None] = mapped_column(String(30), nullable=True)
    waiting_patients: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_waiting_time_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    staff_available: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_updated_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_quality_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    import_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    records_total: Mapped[int] = mapped_column(Integer, default=0)
    records_accepted: Mapped[int] = mapped_column(Integer, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[str] = mapped_column(String(50), default="2024-01-01T00:00:00")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
