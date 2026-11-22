"""Work interrupted by a restart is picked up again on start-up."""

import time

from app.models import Policy
from app.recovery import resume_interrupted
from app.seed import seed


def test_policy_left_running_by_a_restart_is_read_again(session_factory, db_session):
    user = seed(db_session)
    policy = next(p for p in user.policies if p.name == "Suraksha Health Plus")
    policy.analysis_status = "running"  # what a server stopped mid-read leaves behind
    db_session.commit()

    resume_interrupted(session_factory)
    for _ in range(50):  # it runs in a background thread
        with session_factory() as db:
            if db.get(Policy, policy.id).analysis_status != "running":
                break
        time.sleep(0.1)
    with session_factory() as db:
        # no documents: understanding finishes with nothing to read instead of staying "running"
        assert db.get(Policy, policy.id).analysis_status == "none"


def test_nothing_to_resume_starts_nothing(session_factory):
    resume_interrupted(session_factory)  # empty database: returns without starting a thread
