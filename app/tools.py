from datetime import date
from langchain_core.tools import tool
from . import db
from .calendar import working_days, holidays_between
from .policy import search_policy

@tool
def get_employee_profile(employee_id: str) -> dict:
    """Get authoritative employee profile information."""
    employee = db.get_employee(employee_id)
    return employee or {"error": "Employee not found"}

@tool
def get_leave_balance(employee_id: str, leave_type: str) -> dict:
    """Get authoritative remaining leave entitlement for an employee."""
    result = db.get_balance(employee_id, leave_type.upper())
    return result or {"error": "Leave balance not found"}

@tool
def get_leave_history(employee_id: str) -> list[dict]:
    """Get the employee's historical leave requests."""
    with db.connection() as c:
        rows = c.execute(
            "SELECT * FROM leave_requests WHERE employee_id=? ORDER BY start_date DESC",
            (employee_id,),
        ).fetchall()
        return [dict(r) for r in rows]

@tool
def get_company_holidays(start_date: str, end_date: str) -> dict:
    """Get company holidays in a date range."""
    return holidays_between(start_date, end_date)

@tool
def calculate_working_days(start_date: str, end_date: str) -> dict:
    """Calculate actual working leave days, excluding weekends and company holidays."""
    days = working_days(start_date, end_date)
    return {"working_days": len(days), "dates": days}

@tool
def search_leave_policy(question: str) -> list[dict]:
    """Search HR policy documents for an answer to a leave-policy question."""
    return search_policy(question)

@tool
def get_manager(employee_id: str) -> dict:
    """Get the employee's manager."""
    employee = db.get_employee(employee_id)
    if not employee:
        return {"error": "Employee not found"}
    manager = db.get_employee(employee["manager_id"])
    return manager or {"manager_id": employee["manager_id"]}

@tool
def get_team_calendar(employee_id: str, start_date: str, end_date: str) -> dict:
    """Get a demo team-availability signal. Replace with a real calendar service."""
    # Deliberately returns data, not a decision. The agent decides what it means.
    return {
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "known_team_absences": [],
        "capacity_signal": "AVAILABLE",
    }

@tool
def create_leave_request(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str,
) -> dict:
    """
    Create a leave request only after the agent has gathered enough evidence.
    This is a side-effecting tool and performs deterministic safety checks.
    """
    days = working_days(start_date, end_date)
    balance = db.get_balance(employee_id, leave_type.upper())

    if not balance:
        return {"error": "No balance found for this leave type"}

    if len(days) > balance["available_days"]:
        return {
            "error": "INSUFFICIENT_BALANCE",
            "available_days": balance["available_days"],
            "requested_working_days": len(days),
        }

    request_id = db.create_request(
        employee_id, leave_type.upper(), start_date, end_date, len(days), reason
    )
    return {
        "request_id": request_id,
        "status": "PENDING_APPROVAL",
        "working_days": len(days),
    }

@tool
def request_manager_approval(request_id: str) -> dict:
    """Create a pending manager approval for an existing leave request."""
    request = db.get_request(request_id)
    if not request:
        return {"error": "Leave request not found"}

    employee = db.get_employee(request["employee_id"])
    if not employee:
        return {"error": "Employee not found"}

    with db.connection() as c:
        c.execute(
            """INSERT OR REPLACE INTO approvals
               VALUES(?,?,?,?)""",
            (request_id, employee["manager_id"], "PENDING", None),
        )

    db.audit(request["employee_id"], "REQUEST_MANAGER_APPROVAL", request_id)

    return {
        "request_id": request_id,
        "approval_status": "PENDING",
        "approver_id": employee["manager_id"],
    }

@tool
def get_approval_status(request_id: str) -> dict:
    """Get the current approval state of a leave request."""
    with db.connection() as c:
        row = c.execute(
            "SELECT * FROM approvals WHERE request_id=?", (request_id,)
        ).fetchone()
        return dict(row) if row else {"status": "NOT_REQUESTED"}

@tool
def cancel_leave_request(employee_id: str, request_id: str) -> dict:
    """Cancel an employee's own leave request."""
    request = db.get_request(request_id)
    if not request:
        return {"error": "Leave request not found"}
    if request["employee_id"] != employee_id:
        return {"error": "UNAUTHORIZED"}
    if request["status"] in ("CANCELLED", "REJECTED"):
        return {"error": f"Cannot cancel request in {request['status']} state"}

    with db.connection() as c:
        c.execute(
            "UPDATE leave_requests SET status='CANCELLED' WHERE request_id=?",
            (request_id,),
        )
    db.audit(employee_id, "CANCEL_LEAVE_REQUEST", request_id)
    return {"request_id": request_id, "status": "CANCELLED"}

@tool
def notify_employee(employee_id: str, message: str) -> dict:
    """Send a notification to an employee. Demo implementation."""
    db.audit(employee_id, "NOTIFICATION", message)
    return {"sent": True, "employee_id": employee_id, "message": message}

TOOLS = [
    get_employee_profile,
    get_leave_balance,
    get_leave_history,
    get_company_holidays,
    calculate_working_days,
    search_leave_policy,
    get_manager,
    get_team_calendar,
    create_leave_request,
    request_manager_approval,
    get_approval_status,
    cancel_leave_request,
    notify_employee,
]
