from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Patient, PatientCreate, PatientRead, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[PatientRead])
def list_patients(*, session: Session = Depends(get_session)) -> List[PatientRead]:
    """按创建时间倒序返回全部患者列表。"""

    patients = session.exec(select(Patient).order_by(Patient.created_at.desc())).all()
    return patients


@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(*, session: Session = Depends(get_session), patient_in: PatientCreate) -> PatientRead:
    """登记一位新患者，并返回持久化后的完整信息。"""

    patient = Patient(**patient_in.model_dump())
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(*, session: Session = Depends(get_session), patient_id: int) -> PatientRead:
    """根据主键编号获取患者详情。"""

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
    """对患者记录做部分字段更新，仅覆盖请求中提供的内容。"""

    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    update_data = patient_update.model_dump(exclude_unset=True)
    # 遍历需要更新的键值对并写回实例
    for key, value in update_data.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient
