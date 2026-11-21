from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from app.db import add_missing_columns, init_db
from app.understanding.clauses import split_clauses

WORDING = """Suraksha Health Plus
Policy Wording

1. Preamble
This Policy is a contract between the Policyholder and the Company.

2. Definitions
2.1 Accident
A sudden, unforeseen and involuntary event.
2.2 Continuous Coverage
Uninterrupted coverage renewed without any break.

3. What is not covered
The Company will not pay for:
1. Cosmetic surgery.
2. Treatment of obesity.
8. Unproven or experimental treatment.

4. Waiting periods
4.1 Initial waiting period
No expenses are payable in the first 30 days.
4.2 Specified illnesses
Joint replacement is covered after 24 months from the First Policy Date."""


def test_split_numbered_sections_and_subclauses():
    clauses = split_clauses([(1, WORDING)])
    assert [c.ref for c in clauses] == ["1", "2.1", "2.2", "3", "4.1", "4.2"]
    c = clauses[-1]
    assert (c.title, c.section_title, c.section_ref) == ("Specified illnesses", "Waiting periods", "4")
    assert "24 months" in c.text
    # numbered list items stay inside their clause instead of becoming headings
    assert "8. Unproven or experimental treatment." in clauses[3].text
    assert [c.order for c in clauses] == list(range(6))


def test_clause_pages_span_page_breaks():
    pages = [(1, "4. Waiting periods\n4.1 Initial\nFirst 30 days."), (2, "4.2 Specified illnesses\nJoint replacement after"), (3, "24 months.\n5. Exclusions\nCosmetic surgery is excluded from cover here.")]
    clauses = {c.ref: c for c in split_clauses(pages)}
    assert (clauses["4.2"].page_start, clauses["4.2"].page_end) == (2, 3)
    assert clauses["5"].page_start == 3


def test_dates_and_amounts_are_not_headings():
    text = "6. Co-payment\nApplies from\n12 Mar 2026 onwards\n10 percent of every claim\n7. Renewal\nRenew within 30 days."
    assert [c.ref for c in split_clauses([(1, text)])] == ["6", "7"]


def test_sample_wordings_split_fully():
    from pathlib import Path

    from app.extraction import extract

    pdf = Path(__file__).resolve().parents[2] / "samples" / "suraksha-health-plus-policy-wording.pdf"
    if not pdf.exists():
        return
    pages = extract(pdf.read_bytes(), "application/pdf")
    refs = [c.ref for c in split_clauses([(p.number, p.text) for p in pages])]
    assert refs[:2] == ["1", "2.1"] and "4.2" in refs and "6" in refs and refs[-1] == "11"
    assert len(refs) == 30


def test_add_missing_columns_upgrades_old_database():
    engine = create_engine("sqlite://", poolclass=StaticPool)
    with engine.begin() as conn:  # a 'policies' table as Stage 0 created it
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255), full_name VARCHAR(120), password_hash VARCHAR(255), preferred_language VARCHAR(8), created_at DATETIME)"))
        conn.execute(text("CREATE TABLE policies (id INTEGER PRIMARY KEY, owner_id INTEGER, category VARCHAR(20), name VARCHAR(160), insurer VARCHAR(160), policy_number VARCHAR(80), status VARCHAR(20), sum_insured BIGINT, cover_since DATE, renews_on DATE, highlights JSON, created_at DATETIME)"))
        conn.execute(text("INSERT INTO policies (id, owner_id, category, name, insurer, status, highlights) VALUES (1, 1, 'health', 'Old', 'X', 'active', '{}')"))
    init_db(engine)
    cols = {c["name"] for c in inspect(engine).get_columns("policies")}
    assert {"terms", "analysis_status", "auto_created"} <= cols
    with engine.connect() as conn:
        row = conn.execute(text("SELECT analysis_status, auto_created FROM policies WHERE id = 1")).one()
    assert tuple(row) == ("none", 0)
    assert add_missing_columns(engine) == []  # running again changes nothing
