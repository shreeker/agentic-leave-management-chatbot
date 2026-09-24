import sqlite3
from pathlib import Path
from contextlib import contextmanager
import uuid
from .models import Employee

DB_PATH = Path("leave.db")

@contextmanager
def connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with connection() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            manager_id TEXT NOT NULL,
            department TEXT NOT NULL,
            location TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS balances (
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            available_days REAL NOT NULL,
            used_days REAL NOT NULL,
            PRIMARY KEY(employee_id, leave_type)
        );

        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            working_days INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS approvals (
            request_id TEXT PRIMARY KEY,
            approver_id TEXT NOT NULL,
            status TEXT NOT NULL,
            comment TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            employee_id TEXT,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

def audit(employee_id: str | None, action: str, details: str):
    with connection() as c:
        c.execute(
            "INSERT INTO audit_events(event_id, employee_id, action, details) VALUES(?,?,?,?)",
            (str(uuid.uuid4()), employee_id, action, details),
        )

def get_employee(employee_id: str):
    with connection() as c:
        row = c.execute(
            "SELECT * FROM employees WHERE employee_id=?", (employee_id,)
        ).fetchone()
        return dict(row) if row else None

def get_balance(employee_id: str, leave_type: str):
    with connection() as c:
        row = c.execute(
            "SELECT * FROM balances WHERE employee_id=? AND leave_type=?",
            (employee_id, leave_type),
        ).fetchone()
        return dict(row) if row else None

def create_request(employee_id, leave_type, start_date, end_date, working_days, reason):
    request_id = "LR-" + uuid.uuid4().hex[:10].upper()
    with connection() as c:
        c.execute(
            """INSERT INTO leave_requests
            VALUES(?,?,?,?,?,?,?,?)""",
            (request_id, employee_id, leave_type, start_date, end_date,
             working_days, reason, "PENDING_APPROVAL"),
        )
    audit(employee_id, "CREATE_LEAVE_REQUEST", request_id)
    return request_id

def get_request(request_id):
    with connection() as c:
        row = c.execute(
            "SELECT * FROM leave_requests WHERE request_id=?", (request_id,)
        ).fetchone()
        return dict(row) if row else None

def save_approval(request_id, approver_id, status, comment):
    with connection() as c:
        c.execute(
            """INSERT OR REPLACE INTO approvals
            VALUES(?,?,?,?)""",
            (request_id, approver_id, status, comment),
        )
        if status == "APPROVED":
            c.execute(
                "UPDATE leave_requests SET status='APPROVED' WHERE request_id=?",
                (request_id,),
            )
        elif status == "REJECTED":
            c.execute(
                "UPDATE leave_requests SET status='REJECTED' WHERE request_id=?",
                (request_id,),
            )
    audit(None, "APPROVAL", f"{request_id}:{status}")
