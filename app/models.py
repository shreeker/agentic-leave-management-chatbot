from typing import Literal, Optional
from pydantic import BaseModel, Field

LeaveType = Literal["VACATION", "SICK", "PERSONAL", "BEREAVEMENT"]

class Employee(BaseModel):
    employee_id: str
    name: str
    manager_id: str
    department: str
    location: str

class LeaveBalance(BaseModel):
    employee_id: str
    leave_type: LeaveType
    available_days: float
    used_days: float

class LeaveRequest(BaseModel):
    request_id: str
    employee_id: str
    leave_type: LeaveType
    start_date: str
    end_date: str
    working_days: int
    reason: str
    status: Literal["DRAFT", "PENDING_APPROVAL", "APPROVED", "REJECTED", "CANCELLED"]

class Approval(BaseModel):
    request_id: str
    approver_id: str
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    comment: Optional[str] = None

class ChatRequest(BaseModel):
    employee_id: str
    message: str

class ChatResponse(BaseModel):
    thread_id: str
    response: str
