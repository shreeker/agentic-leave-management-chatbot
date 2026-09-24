from app.calendar import working_days

def test_working_days_excludes_weekends_and_holidays():
    days = working_days("2026-10-12", "2026-10-20")
    assert "2026-10-15" not in days
    assert "2026-10-16" not in days
    assert len(days) == 5
