import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agent.tools.registry import AgentToolRegistry
from database.schema.models import Base, Customer, Payment
from database.seed.demo_case import seed_demo_case


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_demo_case(session)
    yield session
    session.close()


def test_tool_get_payment_details(test_db):
    tools = AgentToolRegistry(test_db)
    payment = test_db.query(Payment).first()
    res = tools.get_payment_details(payment.id)
    assert res["amount"] == 4999.0
    assert res["status"] == "FAILED"
    assert res["failure_reason"] == "insufficient_funds"


def test_tool_get_customer_history(test_db):
    tools = AgentToolRegistry(test_db)
    customer = test_db.query(Customer).first()
    res = tools.get_customer_history(customer.id)
    assert res["name"] == "Acme Media"
    assert res["payment_success_rate"] == 0.96


def test_tool_calculate_risk_and_recoverability(test_db):
    tools = AgentToolRegistry(test_db)
    payment = test_db.query(Payment).first()
    risk_res = tools.calculate_risk(payment.id)
    rec_res = tools.calculate_recoverability(payment.id)
    assert "risk_score" in risk_res
    assert "recoverability_score" in rec_res
    assert rec_res["recoverability_score"] > 60.0


def test_tool_classify_failure(test_db):
    tools = AgentToolRegistry(test_db)
    c1 = tools.classify_failure("temporary_bank_failure")
    assert c1["classified_category"] == "TEMPORARY_BANK_FAILURE"
    assert c1["recommended_action"] == "DELAYED_RETRY"

    c2 = tools.classify_failure("expired_card")
    assert c2["classified_category"] == "EXPIRED_CARD"
    assert c2["recommended_action"] == "PAYMENT_LINK"
