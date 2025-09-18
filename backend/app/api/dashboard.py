from datetime import datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from ..database import get_session
from ..models import Appointment, DashboardSummary, Doctor, Patient

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(*, session: Session = Depends(get_session)) -> DashboardSummary:
    """Return aggregate metrics for the landing dashboard."""

    total_patients = session.exec(select(func.count(Patient.id))).one()
    total_doctors = session.exec(select(func.count(Doctor.id))).one()

    today = datetime.utcnow().date()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)

    appointments_today = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.scheduled_time >= start_of_day,
            Appointment.scheduled_time <= end_of_day,
        )
    ).one()

    upcoming_appointments = session.exec(
        select(func.count(Appointment.id)).where(Appointment.scheduled_time > datetime.utcnow())
    ).one()

    active_departments = session.exec(
        select(func.count(func.distinct(Doctor.department_id))).where(Doctor.department_id.isnot(None))
    ).one()

    return DashboardSummary(
        total_patients=total_patients or 0,
        total_doctors=total_doctors or 0,
        appointments_today=appointments_today or 0,
        upcoming_appointments=upcoming_appointments or 0,
        active_departments=active_departments or 0,
    )
