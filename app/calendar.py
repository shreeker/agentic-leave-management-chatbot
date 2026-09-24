from datetime import date, timedelta

# Demo corporate calendar. Replace with your corporate calendar/holiday service.
HOLIDAYS = {
    "2026-10-15": "Company Foundation Day",
    "2026-10-16": "Company Holiday",
}

def is_weekday(d: date) -> bool:
    return d.weekday() < 5

def working_days(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        raise ValueError("end_date must not be before start_date")

    result = []
    current = start
    while current <= end:
        iso = current.isoformat()
        if is_weekday(current) and iso not in HOLIDAYS:
            result.append(iso)
        current += timedelta(days=1)
    return result

def holidays_between(start_date: str, end_date: str):
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    return {
        d: name for d, name in HOLIDAYS.items()
        if start <= date.fromisoformat(d) <= end
    }
