from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    Appointment,
    AppointmentCreate,
    AppointmentRead,
    AppointmentStatus,
    AppointmentUpdate,
    Doctor,
    Patient,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=List[AppointmentRead])
def list_appointments(
    *,
    session: Session = Depends(get_session),
    status_filter: Optional[AppointmentStatus] = Query(default=None, alias="status"),
) -> List[AppointmentRead]:
    """Return appointments with optional status filter."""

    statement = select(Appointment).options(
        selectinload(Appointment.patient), selectinload(Appointment.doctor)
    )
    if status_filter:
        statement = statement.where(Appointment.status == status_filter)
    statement = statement.order_by(Appointment.scheduled_time)
    appointments = session.exec(statement).all()
    return appointments


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    *, session: Session = Depends(get_session), appointment_in: AppointmentCreate
) -> AppointmentRead:
    """Create an appointment ensuring referenced entities exist."""

    patient = session.get(Patient, appointment_in.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    doctor = session.get(Doctor, appointment_in.doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    appointment = Appointment(**appointment_in.model_dump())
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    appointment.patient = patient
    appointment.doctor = doctor
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    *, session: Session = Depends(get_session), appointment_id: int
) -> AppointmentRead:
    """Retrieve an appointment with relations."""

    appointment = session.exec(
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(selectinload(Appointment.patient), selectinload(Appointment.doctor))
    ).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    *,
    session: Session = Depends(get_session),
    appointment_id: int,
    appointment_update: AppointmentUpdate,
) -> AppointmentRead:
    """Update appointment details such as status or schedule."""

    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    update_data = appointment_update.model_dump(exclude_unset=True)
    if "doctor_id" in update_data and update_data["doctor_id"] is not None:
        doctor = session.get(Doctor, update_data["doctor_id"])
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    if "scheduled_time" in update_data and update_data["scheduled_time"]:
        new_time = update_data["scheduled_time"]
        if isinstance(new_time, datetime) and new_time < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Schedule must be in the future")

    for key, value in update_data.items():
        setattr(appointment, key, value)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    appointment = session.exec(
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(selectinload(Appointment.patient), selectinload(Appointment.doctor))
    ).first()
    return appointment
