from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Patient, PatientCreate, PatientRead, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[PatientRead])
def list_patients(*, session: Session = Depends(get_session)) -> List[PatientRead]:
    """Return all patients ordered by creation time."""

    patients = session.exec(select(Patient).order_by(Patient.created_at.desc())).all()
    return patients


@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(*, session: Session = Depends(get_session), patient_in: PatientCreate) -> PatientRead:
    """Register a new patient."""

    patient = Patient(**patient_in.model_dump())
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(*, session: Session = Depends(get_session), patient_id: int) -> PatientRead:
    """Retrieve patient details by identifier."""

    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientRead)
def update_patient(
    *,
    session: Session = Depends(get_session),
    patient_id: int,
    patient_update: PatientUpdate,
) -> PatientRead:
    """Update mutable fields on a patient record."""

    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient
