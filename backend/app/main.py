"""
FastAPI Application Entry Point
Plateforme Universite - Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    API Backend pour la Plateforme Universite.

    ## Fonctionnalites

    * **Authentification** - JWT tokens pour etudiants, professeurs et admins
    * **Evaluations** - Gestion des examens et evaluations
    * **Soumissions** - Soumission de copies par les etudiants
    * **Corrections IA** - Correction automatisee avec GPT-4
    * **Candidatures** - Gestion des candidatures avec verification OCR
    * **Rapports** - Generation de rapports PDF
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": f"Bienvenue sur {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_NAME}
