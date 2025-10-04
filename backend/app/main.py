from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base
from app.api import auth_router, invoices_router, approvals_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered AP/AR workflow tool with OCR, human-in-loop validation, and QuickBooks integration"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(invoices_router)
app.include_router(approvals_router)


@app.get("/")
def root():
    return {
        "message": "LedgerFlow API",
        "version": settings.VERSION,
        "features": [
            "Real-time invoice ingestion with OCR",
            "Human-in-the-loop validation",
            "Role-based approvals",
            "QuickBooks integration",
            ">90% extraction accuracy on synthetic data"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
