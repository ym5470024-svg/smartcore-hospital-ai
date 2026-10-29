from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import HospitalRecord, ImportLog
from app.schemas import HospitalRecordCreate, HospitalRecordRead
from app.services.ai_assistant import generate_insights
from app.services.analytics import compute_crowding, compute_service_summary, compute_summary, compute_trend, occupancy_rate
from app.services.forecasting import forecast_series, validate_forecast_requirements
from app.services.ingestion import preview_upload

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Core Hospital Intelligence", version="0.1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "smartcore-hospital-ai"}


@app.get("/api/hospitals")
def list_hospitals(
    db: Session = Depends(get_db),
    governorate: str | None = None,
    hospital_name: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False))
    if governorate:
        query = query.filter(HospitalRecord.governorate.ilike(f"%{governorate}%"))
    if hospital_name:
        query = query.filter(HospitalRecord.hospital_name.ilike(f"%{hospital_name}%"))
    total = query.count()
    rows = query.order_by(HospitalRecord.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [HospitalRecordRead.model_validate(r).model_dump() for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@app.get("/api/hospitals/{hospital_id}")
def get_hospital(hospital_id: str, db: Session = Depends(get_db)):
    record = db.query(HospitalRecord).filter(HospitalRecord.hospital_id == hospital_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Hospital not found.")
    return HospitalRecordRead.model_validate(record).model_dump()


@app.get("/api/analytics/overview")
def analytics_overview(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    records = [
        {
            "hospital_name": r.hospital_name,
            "occupied_beds": r.occupied_beds,
            "total_beds": r.total_beds,
            "reporting_timestamp": r.reporting_timestamp,
            "reporting_period": r.reporting_period,
            "governorate": r.governorate,
            "available_beds": r.available_beds,
        }
        for r in rows
    ]
    summary = compute_summary(records)
    return summary


@app.get("/api/analytics/occupancy")
def analytics_occupancy(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    records = [
        {
            "hospital_name": r.hospital_name,
            "occupied_beds": r.occupied_beds,
            "total_beds": r.total_beds,
            "available_beds": r.available_beds,
        }
        for r in rows
    ]
    result = []
    for r in records:
        result.append({
            "hospital_name": r["hospital_name"],
            "occupancy_rate": occupancy_rate(r.get("occupied_beds"), r.get("total_beds")),
            "available_beds": r.get("available_beds"),
        })
    return result


@app.get("/api/analytics/crowding")
def analytics_crowding(db: Session = Depends(get_db), threshold: float = 75.0):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    records = [{
        "hospital_name": r.hospital_name,
        "occupied_beds": r.occupied_beds,
        "total_beds": r.total_beds,
        "reporting_period": r.reporting_period,
    } for r in rows]
    return compute_crowding(records, threshold=threshold)


@app.get("/api/analytics/services")
def analytics_services(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    records = [{
        "accident_service_available": r.accident_service_available,
        "burn_unit_available": r.burn_unit_available,
        "intensive_care_available": r.intensive_care_available,
        "operating_room_available": r.operating_room_available,
        "laboratory_available": r.laboratory_available,
        "radiology_available": r.radiology_available,
        "ambulance_service_available": r.ambulance_service_available,
    } for r in rows]
    return compute_service_summary(records)


@app.get("/api/analytics/trends")
def analytics_trends(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    records = [{
        "hospital_name": r.hospital_name,
        "reporting_period": r.reporting_period,
        "occupied_beds": r.occupied_beds,
        "total_beds": r.total_beds,
    } for r in rows]
    return compute_trend(records)


@app.post("/api/import/preview")
async def import_preview(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Please upload a CSV or Excel file.")
    content = await file.read()
    from io import BytesIO
    buffer = BytesIO(content)
    if file.filename.lower().endswith(".csv"):
        import pandas as pd
        df = pd.read_csv(buffer)
    else:
        import pandas as pd
        df = pd.read_excel(buffer)
    preview = {
        "columns": list(df.columns),
        "preview_rows": df.head(10).to_dict(orient="records"),
        "warnings": ["Preview generated successfully."],
        "file_name": file.filename,
    }
    return preview


@app.post("/api/import/confirm")
async def import_confirm(
    file: UploadFile = File(...),
    mode: str = Form("append"),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Please upload a CSV or Excel file.")
    from io import BytesIO
    import pandas as pd
    content = await file.read()
    buffer = BytesIO(content)
    if file.filename.lower().endswith(".csv"):
        df = pd.read_csv(buffer)
    else:
        df = pd.read_excel(buffer)

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file contains no rows.")

    records_inserted = 0
    for _, row in df.iterrows():
        item = HospitalRecord(
            hospital_id=str(row.get("hospital_id") or row.get("Hospital ID") or row.get("hospital_name") or "unknown"),
            hospital_name=str(row.get("hospital_name") or row.get("Hospital Name") or "Unknown hospital"),
            governorate=str(row.get("governorate") or row.get("Governorate") or "Unknown"),
            city=str(row.get("city") or row.get("City") or ""),
            district=str(row.get("district") or row.get("District") or ""),
            hospital_type=str(row.get("hospital_type") or row.get("Hospital Type") or ""),
            reporting_timestamp=str(row.get("reporting_timestamp") or row.get("Last Updated") or ""),
            reporting_period=str(row.get("reporting_period") or row.get("Reporting Period") or ""),
            total_beds=float(row.get("total_beds") or 0),
            occupied_beds=float(row.get("occupied_beds") or 0),
            available_beds=float(row.get("available_beds") or 0),
            emergency_capacity=float(row.get("emergency_capacity") or 0),
            emergency_current_load=float(row.get("emergency_current_load") or 0),
            emergency_status=str(row.get("emergency_status") or row.get("Emergency") or "unknown"),
            accident_service_available=str(row.get("accident_service_available") or row.get("Accident Service") or "unknown"),
            burn_unit_available=str(row.get("burn_unit_available") or row.get("Burn Unit") or "unknown"),
            intensive_care_available=str(row.get("intensive_care_available") or row.get("ICU") or "unknown"),
            operating_room_available=str(row.get("operating_room_available") or row.get("Operating Room") or "unknown"),
            laboratory_available=str(row.get("laboratory_available") or row.get("Laboratory") or "unknown"),
            radiology_available=str(row.get("radiology_available") or row.get("Radiology") or "unknown"),
            ambulance_service_available=str(row.get("ambulance_service_available") or row.get("Ambulance") or "unknown"),
            waiting_patients=float(row.get("waiting_patients") or 0),
            average_waiting_time_minutes=float(row.get("average_waiting_time_minutes") or 0),
            staff_available=float(row.get("staff_available") or 0),
            source_name="uploaded_file",
            data_quality_status="accepted",
        )
        db.add(item)
        records_inserted += 1
    db.commit()
    log = ImportLog(
        file_name=file.filename,
        import_mode=mode,
        records_total=int(len(df)),
        records_accepted=records_inserted,
        records_rejected=0,
        status="success",
        created_at="now",
        summary=f"Accepted {records_inserted} rows from {file.filename}.",
    )
    db.add(log)
    db.commit()
    return {"accepted": records_inserted, "rejected": 0, "duplicates": 0, "mode": mode, "log_id": log.id}


@app.get("/api/import/history")
def import_history(db: Session = Depends(get_db)):
    logs = db.query(ImportLog).order_by(ImportLog.id.desc()).all()
    return [{
        "id": log.id,
        "file_name": log.file_name,
        "import_mode": log.import_mode,
        "records_total": log.records_total,
        "records_accepted": log.records_accepted,
        "records_rejected": log.records_rejected,
        "status": log.status,
        "summary": log.summary,
        "created_at": log.created_at,
    } for log in logs]


@app.get("/api/data-quality")
def data_quality(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    issues = []
    for r in rows:
        if r.total_beds and r.occupied_beds and r.occupied_beds > r.total_beds:
            issues.append({"hospital_name": r.hospital_name, "field": "occupied_beds", "issue": "Occupied beds exceed total beds."})
        if r.total_beds and r.available_beds and abs((r.total_beds - r.occupied_beds) - r.available_beds) > 1:
            issues.append({"hospital_name": r.hospital_name, "field": "available_beds", "issue": "Available beds are inconsistent with capacity."})
    return {"issues": issues, "count": len(issues)}


@app.post("/api/assistant/query")
def assistant_query(payload: dict[str, Any], db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    records = [{
        "hospital_name": r.hospital_name,
        "occupied_beds": r.occupied_beds,
        "total_beds": r.total_beds,
        "reporting_period": r.reporting_period,
    } for r in rows]
    insights = generate_insights(records, payload.get("question"))
    return {"answer": "\n".join(insights), "insights": insights}


@app.get("/api/reports/export")
def export_report(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).all()
    payload = [{
        "hospital_id": r.hospital_id,
        "hospital_name": r.hospital_name,
        "governorate": r.governorate,
        "reporting_period": r.reporting_period,
        "total_beds": r.total_beds,
        "occupied_beds": r.occupied_beds,
        "available_beds": r.available_beds,
    } for r in rows]
    return {"records": payload, "count": len(payload)}


@app.get("/api/forecast")
def forecast_endpoint(db: Session = Depends(get_db)):
    rows = db.query(HospitalRecord).filter(HospitalRecord.is_deleted.is_(False)).order_by(HospitalRecord.id.asc()).all()
    values = [float(r.occupied_beds or 0.0) for r in rows]
    if not validate_forecast_requirements(values):
        return {"status": "Insufficient historical data", "forecast": None}
    return forecast_series(values)
