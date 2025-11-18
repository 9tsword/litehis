from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Gender(str, Enum):
    """患者性别枚举，限定可选值。"""

    FEMALE = "female"
    MALE = "male"
    OTHER = "other"
    UNKNOWN = "unknown"


class AppointmentStatus(str, Enum):
    """预约单状态枚举，描述就诊流程节点。"""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TimestampedModel(SQLModel):
    """为模型增加创建与更新时间字段的混入类。"""

    # 使用 UTC 时间戳记录，便于服务之间同步
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DepartmentBase(SQLModel):
    name: str = Field(index=True, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


class Department(DepartmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # 反向关联医生列表，便于一次性加载同科室医生信息
    doctors: list["Doctor"] = Relationship(back_populates="department")


class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class DepartmentCreate(DepartmentBase):
    pass


class PatientBase(SQLModel):
    full_name: str = Field(max_length=200)
    gender: Gender = Field(default=Gender.UNKNOWN)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(default=None, max_length=32)
    id_card: Optional[str] = Field(default=None, max_length=64)
    address: Optional[str] = Field(default=None, max_length=500)


class Patient(TimestampedModel, PatientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # 维护患者下的所有预约记录
    appointments: list["Appointment"] = Relationship(back_populates="patient")


class PatientRead(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientCreate(PatientBase):
    pass


class PatientUpdate(SQLModel):
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    address: Optional[str] = None


class DoctorBase(SQLModel):
    full_name: str = Field(max_length=200)
    title: Optional[str] = Field(default=None, max_length=120)
    department_id: Optional[int] = Field(default=None, foreign_key="department.id")
    specialty: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=32)


class Doctor(TimestampedModel, DoctorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # 单个医生所属科室以及负责的预约
    department: Optional[Department] = Relationship(back_populates="doctors")
    appointments: list["Appointment"] = Relationship(back_populates="doctor")


class DoctorRead(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentRead] = None

    class Config:
        from_attributes = True


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(SQLModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    department_id: Optional[int] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None


class AppointmentBase(SQLModel):
    scheduled_time: datetime
    reason: Optional[str] = Field(default=None, max_length=500)


class Appointment(TimestampedModel, AppointmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)
    patient_id: int = Field(foreign_key="patient.id")
    doctor_id: int = Field(foreign_key="doctor.id")

    patient: Patient = Relationship(back_populates="appointments")
    doctor: Doctor = Relationship(back_populates="appointments")


class AppointmentRead(AppointmentBase):
    id: int
    status: AppointmentStatus
    patient: PatientRead
    doctor: DoctorRead
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentCreate(AppointmentBase):
    patient_id: int
    doctor_id: int


class AppointmentUpdate(SQLModel):
    scheduled_time: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    doctor_id: Optional[int] = None


class DashboardSummary(SQLModel):
    total_patients: int
    total_doctors: int
    appointments_today: int
    upcoming_appointments: int
    active_departments: int
