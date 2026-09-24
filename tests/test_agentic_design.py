def test_agent_is_not_a_fixed_business_workflow():
    # Architectural test/documentation:
    # there is no hard-coded balance->policy->calendar->approval sequence.
    from app.agent import SYSTEM_PROMPT
    assert "DO NOT FOLLOW A FIXED SEQUENCE" in SYSTEM_PROMPT
    assert "re-plan" in SYSTEM_PROMPT
