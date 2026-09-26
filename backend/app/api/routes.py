from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Returns a simple status response confirming the API is running."""
    return {"status": "ok", "service": "AI Food Packaging Optimizer API"}
