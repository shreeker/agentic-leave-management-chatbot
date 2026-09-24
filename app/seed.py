from .db import init_db, connection

def seed():
    init_db()
    with connection() as c:
        c.execute(
            """INSERT OR REPLACE INTO employees
            VALUES(?,?,?,?,?)""",
            ("E1001", "Alex Employee", "M1001", "Engineering", "Hyderabad"),
        )
        c.execute(
            """INSERT OR REPLACE INTO employees
            VALUES(?,?,?,?,?)""",
            ("M1001", "Morgan Manager", "M2000", "Engineering", "Hyderabad"),
        )
        for leave_type, available in [
            ("VACATION", 8),
            ("SICK", 10),
            ("PERSONAL", 3),
            ("BEREAVEMENT", 5),
        ]:
            c.execute(
                """INSERT OR REPLACE INTO balances
                VALUES(?,?,?,?)""",
                ("E1001", leave_type, available, 0),
            )
    print("Seeded demo employee E1001 and manager M1001.")

if __name__ == "__main__":
    seed()
