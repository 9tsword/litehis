from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Department, DepartmentCreate, DepartmentRead

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/", response_model=List[DepartmentRead])
def list_departments(*, session: Session = Depends(get_session)) -> List[DepartmentRead]:
    """按名称排序返回全部科室。"""

    departments = session.exec(select(Department).order_by(Department.name)).all()
    return departments


@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(
    *, session: Session = Depends(get_session), department_in: DepartmentCreate
) -> DepartmentRead:
    """新增科室时避免重名，若存在则返回冲突错误。"""

    existing = session.exec(
        select(Department).where(Department.name == department_in.name)
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department already exists")

    department = Department(**department_in.model_dump())
    session.add(department)
    session.commit()
    session.refresh(department)
    return department


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(*, session: Session = Depends(get_session), department_id: int) -> DepartmentRead:
    """根据主键编号获取科室详情。"""

    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department
