import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent.core.state_machine import InvalidStateTransitionError
from apps.api.routers import (
    agent_feed,
    audit,
    cases,
    customers,
    dashboard,
    evaluations,
    payments,
    razorpay_connection,
    settings,
    simulator,
    webhooks,
)
from database.connection import get_db_session, init_db
from database.seed.demo_case import seed_demo_case
from database.schema.models import RecoveryCase
from simulator.generators.data_generator import SimulatorDataGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("razorrecover-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RazorRecover AI Database...")
    init_db()
    # Seed initial demo case and sample dataset if database is fresh
    with get_db_session() as db:
        case_count = db.query(RecoveryCase).count()
        if case_count == 0:
            logger.info("Seeding initial demo case and representative sample cases...")
            seed_demo_case(db)
            SimulatorDataGenerator.generate_batch(db, count=25)
    yield
    logger.info("Shutting down RazorRecover AI Backend.")


app = FastAPI(
    title="RazorRecover AI",
    description="Autonomous, deterministic-first AI revenue recovery platform for Razorpay merchants.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidStateTransitionError)
async def state_transition_exception_handler(request: Request, exc: InvalidStateTransitionError):
    return JSONResponse(
        status_code=400,
        content={"error": "INVALID_STATE_TRANSITION", "message": str(exc)},
    )


# Include all modular routers
app.include_router(dashboard.router)
app.include_router(cases.router)
app.include_router(payments.router)
app.include_router(customers.router)
app.include_router(audit.router)
app.include_router(evaluations.router)
app.include_router(simulator.router)
app.include_router(settings.router)
app.include_router(webhooks.router)
app.include_router(agent_feed.router)
app.include_router(razorpay_connection.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    payment_mode = os.getenv("PAYMENT_MODE", "simulator").upper()
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "healthy",
        "service": "RazorRecover AI",
        "version": "1.0.0",
        "payment_mode": f"{payment_mode} MODE",
        "ai_engine": "Gemini API (Active)" if has_gemini else "Deterministic AI Expert (Active)",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
