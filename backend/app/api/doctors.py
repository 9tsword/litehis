from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Department, Doctor, DoctorCreate, DoctorRead, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/", response_model=List[DoctorRead])
def list_doctors(*, session: Session = Depends(get_session)) -> List[DoctorRead]:
    """Return doctors with department information."""

    statement = select(Doctor).order_by(Doctor.full_name)
    doctors = session.exec(statement).all()
    return doctors


@router.post("/", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor(*, session: Session = Depends(get_session), doctor_in: DoctorCreate) -> DoctorRead:
    """Create a doctor, ensuring referenced department exists."""

    if doctor_in.department_id is not None:
        department = session.get(Department, doctor_in.department_id)
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    doctor = Doctor(**doctor_in.model_dump())
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return doctor


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor(*, session: Session = Depends(get_session), doctor_id: int) -> DoctorRead:
    """Retrieve doctor details."""

    doctor = session.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor


@router.patch("/{doctor_id}", response_model=DoctorRead)
def update_doctor(
    *,
    session: Session = Depends(get_session),
    doctor_id: int,
    doctor_update: DoctorUpdate,
) -> DoctorRead:
    """Update doctor attributes."""

    doctor = session.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    update_data = doctor_update.model_dump(exclude_unset=True)
    if "department_id" in update_data and update_data["department_id"] is not None:
        department = session.get(Department, update_data["department_id"])
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    for key, value in update_data.items():
        setattr(doctor, key, value)
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return doctor
